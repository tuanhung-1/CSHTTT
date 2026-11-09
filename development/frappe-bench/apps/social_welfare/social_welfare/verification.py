"""Assigned reviewer conclusions for missing welfare eligibility facts."""

import frappe
from frappe.utils import getdate, now_datetime, nowdate

from social_welfare.permissions import OFFICER, VERIFIER, is_admin

QUESTION_TYPES = {"TARGET_GROUP", "RESIDENCY", "CLASSIFICATION", "OTHER"}
CONCLUSIONS = {"CONFIRMED", "NOT_CONFIRMED", "INSUFFICIENT"}


def require_officer():
	if not is_admin() and OFFICER not in frappe.get_roles():
		frappe.throw("Chỉ cán bộ an sinh được gửi yêu cầu xác minh.", frappe.PermissionError)


def negative_target_group_verified(beneficiary_type, name, target_group, fact_date):
	"""A documented negative conclusion changes missing group data to a known failure."""
	field = "citizen" if beneficiary_type == "Citizen" else "household"
	rows = frappe.get_all(
		"Verification Case",
		filters={"beneficiary_type": beneficiary_type, field: name, "target_group": target_group,
			"question_type": "TARGET_GROUP", "fact_date": getdate(fact_date), "status": "COMPLETED"},
		fields=["conclusion"], order_by="completed_at desc, creation desc", limit=1,
	)
	return bool(rows and rows[0].conclusion == "NOT_CONFIRMED")


@frappe.whitelist(methods=["POST"])
def create_verification_request(question_type, request_note, target_group=None, eligibility_result=None,
		beneficiary_type=None, beneficiary=None):
	require_officer()
	if question_type not in QUESTION_TYPES or not (request_note or "").strip():
		frappe.throw("Chọn nội dung và ghi rõ yêu cầu xác minh.")
	if question_type == "TARGET_GROUP":
		if not target_group or not frappe.db.get_value("Target Group", target_group, "is_active"):
			frappe.throw("Chọn một nhóm đối tượng đang áp dụng.")
	else:
		target_group = None
	if eligibility_result:
		result = frappe.get_doc("Eligibility Result", eligibility_result)
		result.check_permission("read")
		if result.result_status != "NEED_VERIFICATION":
			frappe.throw("Chỉ kết quả cần xác minh mới được gửi từ lần rà soát.")
		beneficiary_type = result.beneficiary_type
		beneficiary = result.citizen or result.household
		fact_date = frappe.db.get_value("Eligibility Run", result.eligibility_run, "cutoff_date")
	else:
		fact_date = nowdate()
	if beneficiary_type not in {"Household", "Citizen"} or not beneficiary:
		frappe.throw("Chọn một hộ hoặc công dân cần xác minh.")
	frappe.get_doc(beneficiary_type, beneficiary).check_permission("read")
	household = beneficiary if beneficiary_type == "Household" else frappe.db.get_value("Citizen", beneficiary, "household")
	if not household:
		frappe.throw("Công dân chưa thuộc hộ gia đình.")
	frappe.db.sql("SELECT name FROM `tabHousehold` WHERE name=%s FOR UPDATE", household)
	reviewer = frappe.db.get_value("Household", household, "assigned_verifier")
	if not reviewer or not frappe.db.get_value("User", reviewer, "enabled") or VERIFIER not in frappe.get_roles(reviewer):
		frappe.throw("Hãy giao hộ gia đình cho một tài khoản Người xác minh đang hoạt động trước.")
	if not is_admin() and reviewer == frappe.session.user:
		frappe.throw("Người yêu cầu không được tự xác minh hồ sơ của mình.", frappe.PermissionError)
	field = "citizen" if beneficiary_type == "Citizen" else "household"
	if frappe.db.exists("Verification Case", {field: beneficiary, "question_type": question_type,
			"target_group": target_group, "fact_date": fact_date, "status": "AWAITING_REVIEW"}):
		frappe.throw("Đã có yêu cầu xác minh đang chờ cho nội dung này.")
	case = frappe.get_doc({
		"doctype": "Verification Case", "eligibility_result": eligibility_result,
		"beneficiary_type": beneficiary_type, field: beneficiary,
		"question_type": question_type, "target_group": target_group, "fact_date": fact_date,
		"request_note": request_note.strip(), "assigned_reviewer": reviewer,
		"requested_by": frappe.session.user, "requested_at": now_datetime(), "status": "AWAITING_REVIEW",
	})
	previous = frappe.flags.social_welfare_verification_action
	frappe.flags.social_welfare_verification_action = "create"
	try:
		case.insert(ignore_permissions=True)
	finally:
		frappe.flags.social_welfare_verification_action = previous
	return case.name


@frappe.whitelist(methods=["POST"])
def complete_verification(name, conclusion, finding, basis, verified_value=None,
		verified_from=None, verified_to=None, evidence_file=None):
	if not is_admin() and VERIFIER not in frappe.get_roles():
		frappe.throw("Chỉ người xác minh được ghi kết luận.", frappe.PermissionError)
	if conclusion not in CONCLUSIONS or not (finding or "").strip() or not (basis or "").strip():
		frappe.throw("Chọn kết luận và ghi nội dung cùng căn cứ xác minh.")
	frappe.db.sql("SELECT name FROM `tabVerification Case` WHERE name=%s FOR UPDATE", name)
	case = frappe.get_doc("Verification Case", name)
	case.check_permission("read")
	if not is_admin() and case.assigned_reviewer != frappe.session.user:
		frappe.throw("Hồ sơ này được giao cho người xác minh khác.", frappe.PermissionError)
	if not is_admin() and case.requested_by == frappe.session.user:
		frappe.throw("Người yêu cầu không được tự kết luận hồ sơ mình đã gửi.", frappe.PermissionError)
	if case.status != "AWAITING_REVIEW":
		frappe.throw("Hồ sơ đã có kết luận; không được sửa lịch sử.")
	if conclusion == "CONFIRMED" and case.question_type == "TARGET_GROUP":
		if not verified_from or not verified_to or getdate(verified_from) > getdate(case.fact_date) or getdate(verified_to) < getdate(case.fact_date):
			frappe.throw("Nhập khoảng hiệu lực đã xác minh, bao gồm ngày dữ liệu cần xác minh.")
		if getdate(verified_from) > getdate(verified_to):
			frappe.throw("Ngày bắt đầu hiệu lực không được sau ngày kết thúc.")
	if conclusion == "CONFIRMED" and case.question_type in {"RESIDENCY", "CLASSIFICATION"} and not (verified_value or "").strip():
		frappe.throw("Nhập giá trị địa bàn hoặc phân loại đã xác minh.")
	if evidence_file:
		file = frappe.db.get_value("File", {"file_url": evidence_file}, ["is_private", "owner"], as_dict=True)
		if not file or not file.is_private or (not is_admin() and file.owner != frappe.session.user):
			frappe.throw("Chỉ dùng tệp riêng tư do chính người xác minh tải lên.")
	case.status, case.conclusion = "COMPLETED", conclusion
	case.finding, case.basis = finding.strip(), basis.strip()
	case.verified_value = (verified_value or "").strip() if conclusion == "CONFIRMED" else None
	case.verified_from = verified_from if conclusion == "CONFIRMED" and case.question_type == "TARGET_GROUP" else None
	case.verified_to = verified_to if conclusion == "CONFIRMED" and case.question_type == "TARGET_GROUP" else None
	case.evidence_file = evidence_file or None
	case.completed_by, case.completed_at = frappe.session.user, now_datetime()
	previous = frappe.flags.social_welfare_verification_action
	frappe.flags.social_welfare_verification_action = case.name
	try:
		case.save(ignore_permissions=True)
	finally:
		frappe.flags.social_welfare_verification_action = previous
	return case.name
