"""Explicit, idempotent setup for a fictional household disaster program.

This function creates demo records only. It does not run screening or approval.
"""

import frappe
from frappe.utils import now_datetime


PROGRAM_CODE = "TEST-TT-HH-2026"
POLICY_CODE = "TEST-CS-TT-HH-2026"
GROUP_CODE = "TEST_DISASTER_AFFECTED"
START = "2026-01-01"
END = "2026-12-31"

# Two eligible, three ineligible, one missing residence for manual screening.
HOUSEHOLDS = (
	("TEST-HH-TT-01", "TEST Nguyễn Văn Hải", "Tổ 01", "Địa chỉ TEST số 01", GROUP_CODE, END),
	("TEST-HH-TT-02", "TEST Trần Thị Bích", "Tổ 02", "Địa chỉ TEST số 02", GROUP_CODE, END),
	("TEST-HH-TT-03", "TEST Lê Văn Phúc", "Tổ 03", "Địa chỉ TEST số 03", GROUP_CODE, END),
	("TEST-HH-TT-04", "TEST Phạm Thị Thu", "Tổ 01", "Địa chỉ TEST số 04", GROUP_CODE, "2026-10-31"),
	("TEST-HH-TT-05", "TEST Võ Văn Khang", "Tổ 01", "Địa chỉ TEST số 05", None, None),
	("TEST-HH-TT-06", "TEST Đặng Thị Hà", None, None, GROUP_CODE, END),
)

RULES = (
	("AFFECTED", "Có ghi nhận ảnh hưởng thiên tai", "TARGET_GROUP", "EQ", GROUP_CODE, "NEED_VERIFICATION", 10),
	("AREA", "Thuộc tổ dân phố trong phạm vi TEST", "RESIDENCY", "IN", "Tổ 01,Tổ 02", "NEED_VERIFICATION", 20),
	("NO_DUP", "Chưa có khoản hỗ trợ từ chương trình", "DUPLICATE", "NOT_EXISTS", None, "NEED_VERIFICATION", 30),
)


def ensure_verified_group(household, target_group, valid_to):
	existing = frappe.db.get_value("Verification Case", {
		"household": household, "question_type": "TARGET_GROUP", "target_group": target_group,
		"status": "COMPLETED", "conclusion": "CONFIRMED",
	}, "name")
	if existing:
		return existing
	verification = frappe.get_doc({
		"doctype": "Verification Case", "beneficiary_type": "Household", "household": household,
		"question_type": "TARGET_GROUP", "target_group": target_group, "fact_date": "2026-06-01",
		"request_note": "Xác minh dữ liệu mẫu phục vụ demo", "assigned_reviewer": "Administrator",
		"requested_by": "Administrator", "requested_at": now_datetime(), "status": "COMPLETED",
		"conclusion": "CONFIRMED", "verified_from": START, "verified_to": valid_to,
		"finding": "Đã xác nhận dữ liệu mẫu", "basis": "TEST-ONLY - dữ liệu giả lập",
		"completed_by": "Administrator", "completed_at": now_datetime(),
	})
	previous_action = getattr(frappe.flags, "social_welfare_verification_action", None)
	frappe.flags.social_welfare_verification_action = "create"
	try:
		verification.insert(ignore_permissions=True)
	finally:
		frappe.flags.social_welfare_verification_action = previous_action
	return verification.name


def seed_household_disaster_demo():
	"""Create the program and sample households without running a screening."""
	if frappe.session.user != "Administrator":
		frappe.throw("Chỉ chạy dữ liệu mẫu bằng bench execute với Administrator.")
	created = {"target_group": False, "policy": False, "policy_version": False,
		"rules": [], "households": [], "citizens": [], "assignments": [], "program": False}
	if not frappe.db.exists("Target Group", GROUP_CODE):
		frappe.get_doc({
			"doctype": "Target Group", "group_code": GROUP_CODE,
			"group_name": "TEST Hộ chịu ảnh hưởng thiên tai",
			"description": "Nhóm dữ liệu giả lập để thử chương trình; không xác nhận thiệt hại thật.",
			"is_active": 1,
		}).insert()
		created["target_group"] = True
	if not frappe.db.exists("Policy", POLICY_CODE):
		frappe.get_doc({
			"doctype": "Policy", "policy_code": POLICY_CODE,
			"policy_name": "TEST Chính sách hỗ trợ hộ bị ảnh hưởng thiên tai",
			"description": "Quy tắc giả lập: nhóm ảnh hưởng, Tổ 01/02, chưa có khoản hỗ trợ trùng.",
			"policy_type": "Household", "is_active": 1,
		}).insert()
		created["policy"] = True
	version_name = frappe.db.get_value("Policy Version", {"policy": POLICY_CODE, "version_number": "1"}, "name")
	if not version_name:
		version = frappe.get_doc({
			"doctype": "Policy Version", "policy": POLICY_CODE,
			"version_number": "1", "effective_from": START, "effective_to": END,
			"legal_reference": "TEST-ONLY - không phải văn bản pháp lý",
			"status": "DRAFT",
		}).insert()
		version_name = version.name
		created["policy_version"] = True
	for code, label, condition_type, operator, expected, missing, priority in RULES:
		if not frappe.db.exists("Policy Rule", {"policy_version": version_name, "rule_code": code}):
			frappe.get_doc({
				"doctype": "Policy Rule", "policy_version": version_name,
				"rule_code": code, "rule_name": label,
				"condition_type": condition_type, "operator": operator,
				"expected_value": expected, "missing_behavior": missing,
				"priority": priority, "is_required": 1,
			}).insert()
			created["rules"].append(code)
	version = frappe.get_doc("Policy Version", version_name)
	if version.status == "DRAFT":
		version.status = "ACTIVE"
		version.save()
	for index, (code, head, area, address, target_group, valid_to) in enumerate(HOUSEHOLDS, 1):
		if not frappe.db.exists("Household", code):
			frappe.get_doc({
				"doctype": "Household", "household_code": code,
				"head_name": head, "residential_group": area, "address": address,
			}).insert()
			created["households"].append(code)
		citizen_code = f"TEST-CT-TT-{index:02d}"
		if not frappe.db.exists("Citizen", citizen_code):
			frappe.get_doc({
				"doctype": "Citizen", "citizen_code": citizen_code,
				"full_name": head, "relationship": "Head", "household": code,
			}).insert()
			created["citizens"].append(citizen_code)
		if target_group and not frappe.db.exists("Target Group Assignment", {
			"household": code, "target_group": target_group, "status": "ACTIVE",
			"valid_from": START, "valid_to": valid_to,
		}):
			verification_case = ensure_verified_group(code, target_group, valid_to)
			assignment = frappe.get_doc({
				"doctype": "Target Group Assignment", "household": code,
				"target_group": target_group, "verification_case": verification_case,
				"valid_from": START, "valid_to": valid_to,
			}).insert()
			created["assignments"].append(assignment.name)
	if not frappe.db.exists("Support Program", PROGRAM_CODE):
		frappe.get_doc({
			"doctype": "Support Program", "code": PROGRAM_CODE,
			"program_name": "TEST Hỗ trợ thiên tai cho hộ gia đình 2026",
			"description": "Dữ liệu giả lập để cán bộ tự chạy rà soát và trình duyệt.",
			"start_date": START, "end_date": END, "beneficiary_type": "Household",
			"target_group": "disaster", "policy_version": version_name,
			"cutoff_date": "2026-11-09", "support_type": "CASH",
			"support_amount": 2_000_000, "budget_estimate": 12_000_000,
			"active": 1,
		}).insert()
		created["program"] = True
	frappe.db.commit()
	return {"program": PROGRAM_CODE, "policy_version": version_name, "created": created,
		"screening_run_created": False}
