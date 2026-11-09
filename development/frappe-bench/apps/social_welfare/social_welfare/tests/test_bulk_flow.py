"""Screen and pay a citizen on an isolated site; Frappe rolls the test transaction back."""

import unittest
from uuid import uuid4

import frappe
from frappe.utils import now_datetime

from social_welfare.bulk import confirm_disbursement, create_batch, decide_batch, financial_report, submit_batch
from social_welfare.eligibility import screen_program


class TestBulkFlow(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self.addCleanup(frappe.db.rollback)
		self.addCleanup(frappe.set_user, "Administrator")
		self.suffix = uuid4().hex[:8]

	def test_citizen_group_to_payment_and_report(self):
		household = frappe.get_doc({"doctype": "Household", "head_name": "Nguyễn Văn Mẫu"}).insert()
		citizen = frappe.get_doc({"doctype": "Citizen", "full_name": "Trần Thị Mẫu", "relationship": "Other", "household": household.name}).insert()
		verification = frappe.get_doc({
			"doctype": "Verification Case", "beneficiary_type": "Citizen", "citizen": citizen.name,
			"question_type": "TARGET_GROUP", "target_group": "DISABILITY", "fact_date": "2026-06-01",
			"request_note": "Yêu cầu kiểm thử", "assigned_reviewer": "Administrator",
			"requested_by": "Administrator", "requested_at": now_datetime(), "status": "COMPLETED",
			"conclusion": "CONFIRMED", "verified_from": "2026-01-01", "verified_to": "2026-12-31",
			"finding": "Xác nhận dữ liệu kiểm thử", "basis": "Căn cứ kiểm thử",
			"completed_by": "Administrator", "completed_at": now_datetime(),
		})
		previous_action = getattr(frappe.flags, "social_welfare_verification_action", None)
		frappe.flags.social_welfare_verification_action = "create"
		try:
			verification.insert(ignore_permissions=True)
		finally:
			frappe.flags.social_welfare_verification_action = previous_action
		frappe.get_doc({"doctype": "Target Group Assignment", "target_group": "DISABILITY", "citizen": citizen.name,
			"verification_case": verification.name, "valid_from": "2026-01-01", "valid_to": "2026-12-31"}).insert()
		policy = frappe.get_doc({"doctype": "Policy", "policy_code": "TP-" + self.suffix, "policy_name": "Chính sách kiểm thử", "policy_type": "Citizen", "is_active": 1}).insert()
		version = frappe.get_doc({"doctype": "Policy Version", "policy": policy.name, "version_number": "1", "effective_from": "2026-01-01", "effective_to": "2026-12-31", "legal_reference": "Quyết định kiểm thử", "status": "DRAFT"}).insert()
		frappe.get_doc({"doctype": "Policy Rule", "policy_version": version.name, "rule_code": "GROUP", "rule_name": "Có nhóm khuyết tật", "condition_type": "TARGET_GROUP", "operator": "IN", "expected_value": "DISABILITY", "is_required": 1}).insert()
		version.status = "ACTIVE"
		version.save()
		program = frappe.get_doc({"doctype": "Support Program", "code": "TB-" + self.suffix, "program_name": "Trợ cấp thử", "start_date": "2026-01-01", "end_date": "2026-12-31", "beneficiary_type": "Citizen", "target_group_ref": "DISABILITY", "policy_version": version.name, "cutoff_date": "2026-06-01", "support_type": "CASH", "support_amount": 100000, "active": 1}).insert()
		run_name = screen_program(program.name)
		result = frappe.db.get_value("Eligibility Result", {"eligibility_run": run_name, "citizen": citizen.name}, ["name", "result_status"], as_dict=True)
		self.assertEqual(result.result_status, "ELIGIBLE")
		batch_name = create_batch(run_name, [result.name])
		submit_batch(batch_name)
		decide_batch(batch_name, "APPROVED", "Đủ điều kiện theo hồ sơ")
		payment = frappe.db.get_value("Disbursement", {"approval_batch": batch_name}, "name")
		self.assertEqual(frappe.db.get_value("Disbursement", payment, "status"), "PENDING")
		confirm_disbursement(payment, "Đã chi và lưu chứng từ")
		program_row = next(row for row in financial_report()["programs"] if row["program"] == program.name)
		self.assertEqual(program_row["paid"], 100000)
