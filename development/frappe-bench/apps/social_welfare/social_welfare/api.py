import frappe

from social_welfare import has_app_permission
from social_welfare.permissions import FINANCE, LEADER, OFFICER, VERIFIER, is_admin
from social_welfare.social_welfare.doctype.household_classification.household_classification import (
	get_effective_classification,
)


@frappe.whitelist()
def household_history(household):
	frappe.get_doc("Household", household).check_permission("read")
	if not frappe.has_permission("Household Classification", "read"):
		frappe.throw("Bạn không có quyền xem lịch sử phân loại.", frappe.PermissionError)
	return {
		"current": get_effective_classification(household),
		"history": frappe.get_list(
			"Household Classification",
			filters={"household": household},
			fields=[
				"name",
				"classification",
				"period",
				"valid_from",
				"valid_to",
				"basis",
				"is_legacy",
				"is_void",
				"void_reason",
			],
			order_by="valid_from desc, creation desc",
			limit=100,
		),
	}


@frappe.whitelist(methods=["POST"])
def void_classification(name, reason):
	if not is_admin() and LEADER not in frappe.get_roles():
		frappe.throw("Chỉ lãnh đạo được hủy hiệu lực phân loại.", frappe.PermissionError)
	if not reason or not reason.strip():
		frappe.throw("Cần nhập lý do hủy hiệu lực.")
	from frappe.utils import now_datetime

	doc = frappe.get_doc("Household Classification", name)
	doc.check_permission("read")
	if doc.is_void:
		frappe.throw("Bản phân loại đã bị hủy hiệu lực.")
	doc.is_void, doc.void_reason = 1, reason.strip()
	doc.voided_by, doc.voided_at = frappe.session.user, now_datetime()
	previous_flag = frappe.flags.social_welfare_void_classification
	frappe.flags.social_welfare_void_classification = doc.name
	try:
		doc.save(ignore_permissions=True)
	finally:
		frappe.flags.social_welfare_void_classification = previous_flag
	return doc.name


@frappe.whitelist()
def dashboard():
	if not has_app_permission():
		frappe.throw("Bạn không có quyền truy cập ứng dụng an sinh.", frappe.PermissionError)
	roles = set(frappe.get_roles())
	cards = []
	definitions = [
		("Household", "Hộ gia đình", {"is_archived": 0}, "household"),
		("Citizen", "Công dân", {"is_archived": 0}, "citizen"),
		("Household Classification", "Lịch sử phân loại", {}, "classification"),
		("Support Program", "Chương trình hỗ trợ", {"is_archived": 0}, "program"),
		("Support Application", "Hồ sơ hỗ trợ", {}, "application"),
	]
	for doctype, label, filters, key in definitions:
		if frappe.has_permission(doctype, "read"):
			count = frappe.get_list(doctype, filters=filters, fields=[{"COUNT": "name", "as": "total"}])[
				0
			].total
			cards.append({"doctype": doctype, "label": label, "count": count, "key": key})
	tasks = []
	for role, states, title in [
		(OFFICER, ["Draft", "Returned"], "Hồ sơ cần hoàn thiện"),
		(VERIFIER, ["Submitted", "Reviewing"], "Hồ sơ được giao xác minh"),
		(LEADER, ["Pending Approval"], "Hồ sơ chờ phê duyệt"),
		(FINANCE, ["Approved"], "Hồ sơ chờ xác nhận chi trả"),
	]:
		if role in roles or is_admin():
			tasks.append(
				{
					"title": title,
					"states": states,
					"items": frappe.get_list(
						"Support Application",
						filters={"workflow_state": ["in", states]},
						fields=["name", "household", "program", "workflow_state"],
						order_by="modified desc",
						limit=8,
					),
				}
			)
	return {
		"cards": cards,
		"tasks": tasks,
		"roles": list(roles),
		"can_create": is_admin() or OFFICER in roles,
	}
