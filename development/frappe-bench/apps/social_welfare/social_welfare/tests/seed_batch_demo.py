"""Optional, idempotent UI demo data. Run explicitly with bench execute on a local site."""

import frappe
from frappe.utils import now_datetime

from social_welfare.eligibility import screen_program


PROGRAM = "TEST-CN-20261109"
START = "2026-01-01"
END = "2026-12-31"

HOUSEHOLDS = (
	("TEST-HH-CN-01", "TEST Nguyễn Văn Minh", "Tổ 01"),
	("TEST-HH-CN-02", "TEST Trần Văn Bình", "Tổ 02"),
	("TEST-HH-CN-03", "TEST Lê Văn Hòa", "Tổ 03"),
	("TEST-HH-CN-04", "TEST Phạm Văn Sơn", "Tổ 04"),
)

CITIZENS = (
	("TEST-CT-CN-01", "TEST Nguyễn Văn Minh", "TEST-HH-CN-01", "Head", "DISABILITY", END),
	("TEST-CT-CN-02", "TEST Nguyễn Thị Lan", "TEST-HH-CN-01", "Spouse", None, None),
	("TEST-CT-CN-03", "TEST Trần Văn Bình", "TEST-HH-CN-02", "Head", "DISABILITY", END),
	("TEST-CT-CN-04", "TEST Trần Thị Mai", "TEST-HH-CN-02", "Child", "DISABILITY", "2026-10-31"),
	("TEST-CT-CN-05", "TEST Lê Văn Hòa", "TEST-HH-CN-03", "Head", "DISABILITY", END),
	("TEST-CT-CN-06", "TEST Lê Thị Hạnh", "TEST-HH-CN-03", "Spouse", None, None),
	("TEST-CT-CN-07", "TEST Phạm Văn Sơn", "TEST-HH-CN-04", "Head", "DISABILITY", END),
	("TEST-CT-CN-08", "TEST Phạm Thị An", "TEST-HH-CN-04", "Child", "CHILDREN", END),
)


def ensure_verified_group(citizen, target_group, valid_to):
	existing = frappe.db.get_value("Verification Case", {
		"citizen": citizen, "question_type": "TARGET_GROUP", "target_group": target_group,
		"status": "COMPLETED", "conclusion": "CONFIRMED",
	}, "name")
	if existing:
		return existing
	verification = frappe.get_doc({
		"doctype": "Verification Case", "beneficiary_type": "Citizen", "citizen": citizen,
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


def seed_batch_demo():
	"""Add eight fictional citizens, then screen the existing test program once."""
	if frappe.session.user != "Administrator":
		frappe.throw("Chỉ chạy bộ dữ liệu mẫu bằng bench execute với Administrator.")
	program = frappe.get_doc("Support Program", PROGRAM)
	if program.beneficiary_type != "Citizen" or program.target_group_ref != "DISABILITY":
		frappe.throw("Chương trình test không còn là chương trình cho công dân thuộc DISABILITY.")
	created = {"households": [], "citizens": [], "assignments": []}
	for code, head, group in HOUSEHOLDS:
		if not frappe.db.exists("Household", code):
			frappe.get_doc({
				"doctype": "Household", "household_code": code, "head_name": head,
				"residential_group": group, "address": "Địa chỉ TEST, phường kiểm thử",
			}).insert()
			created["households"].append(code)
	for code, full_name, household, relationship, target_group, valid_to in CITIZENS:
		if not frappe.db.exists("Citizen", code):
			frappe.get_doc({
				"doctype": "Citizen", "citizen_code": code, "full_name": full_name,
				"household": household, "relationship": relationship,
			}).insert()
			created["citizens"].append(code)
		if target_group and not frappe.db.exists("Target Group Assignment", {
			"citizen": code, "target_group": target_group, "status": "ACTIVE",
			"valid_from": START, "valid_to": valid_to,
		}):
			verification_case = ensure_verified_group(code, target_group, valid_to)
			assignment = frappe.get_doc({
				"doctype": "Target Group Assignment", "citizen": code,
				"target_group": target_group, "verification_case": verification_case,
				"valid_from": START, "valid_to": valid_to,
			}).insert()
			created["assignments"].append(assignment.name)
	run_name = screen_program(PROGRAM)
	rows = frappe.get_all("Eligibility Result", filters={"eligibility_run": run_name},
		fields=["citizen", "result_status", "reason_summary"], limit=1000)
	frappe.db.commit()
	return {
		"run": run_name,
		"created": created,
		"demo_results": [row for row in rows if row.citizen in {citizen[0] for citizen in CITIZENS}],
	}
