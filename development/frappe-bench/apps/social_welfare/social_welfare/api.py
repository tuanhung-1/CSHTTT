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


@frappe.whitelist()
def target_group_history(beneficiary_type, name):
	if beneficiary_type not in ("Household", "Citizen"):
		frappe.throw("Loại đối tượng không hợp lệ.")
	frappe.get_doc(beneficiary_type, name).check_permission("read")
	if not frappe.has_permission("Target Group Assignment", "read"):
		frappe.throw("Bạn không có quyền xem nhóm đối tượng.", frappe.PermissionError)
	field = "household" if beneficiary_type == "Household" else "citizen"
	return frappe.get_list("Target Group Assignment", filters={field: name}, fields=["name", "target_group", "verification_case", "valid_from", "valid_to", "status", "void_reason"], order_by="valid_from desc", limit=100)


@frappe.whitelist(methods=["POST"])
def void_target_group_assignment(name, reason):
	if not is_admin() and LEADER not in frappe.get_roles():
		frappe.throw("Chỉ lãnh đạo được hủy hiệu lực nhóm đối tượng.", frappe.PermissionError)
	if not (reason or "").strip():
		frappe.throw("Cần nhập lý do hủy hiệu lực.")
	doc = frappe.get_doc("Target Group Assignment", name)
	doc.check_permission("read")
	if doc.status != "ACTIVE":
		frappe.throw("Bản gán nhóm không còn hiệu lực.")
	doc.status, doc.void_reason = "VOID", reason.strip()
	previous = frappe.flags.social_welfare_void_target_group_assignment
	frappe.flags.social_welfare_void_target_group_assignment = doc.name
	try:
		doc.save(ignore_permissions=True)
	finally:
		frappe.flags.social_welfare_void_target_group_assignment = previous
	return doc.name


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
	role_pages = [
		(OFFICER, "Công việc cán bộ an sinh", [
			("Hộ gia đình", "Household", {"is_archived": 0}),
			("Công dân", "Citizen", {"is_archived": 0}),
			("Chương trình", "Support Program", {"is_archived": 0}),
			("Đợt cần hoàn thiện", "Approval Batch", {"status": ["in", ["DRAFT", "RETURNED"]]}),
			("Hồ sơ chờ xác minh", "Verification Case", {"status": "AWAITING_REVIEW"}),
		], [
			("Đợt trình cần hoàn thiện", "Approval Batch", {"status": ["in", ["DRAFT", "RETURNED"]]}),
		], [
			("Tiếp nhận hộ gia đình", "Household", "new", {}),
			("Thêm công dân", "Citizen", "new", {}),
			("Rà soát chương trình", "Support Program", "list", {}),
			("Xem các lần rà soát", "Eligibility Run", "list", {}),
			("Theo dõi hồ sơ xác minh", "Verification Case", "list", {}),
		]),
		(VERIFIER, "Hồ sơ được giao xác minh", [
			("Hộ được giao", "Household", {"is_archived": 0}),
			("Hồ sơ cần kết luận", "Verification Case", {"status": "AWAITING_REVIEW"}),
			("Hồ sơ đơn lẻ cần xác minh", "Support Application", {"workflow_state": ["in", ["Submitted", "Reviewing"]]}),
		], [
			("Yêu cầu xác minh được giao", "Verification Case", {"status": "AWAITING_REVIEW"}),
			("Hồ sơ đơn lẻ được giao", "Support Application", {"workflow_state": ["in", ["Submitted", "Reviewing"]]}),
		], [
			("Xem yêu cầu xác minh", "Verification Case", "list", {"status": "AWAITING_REVIEW"}),
			("Xem hộ được giao", "Household", "list", {}),
			("Xem hồ sơ cần xác minh", "Support Application", "list", {"workflow_state": ["in", ["Submitted", "Reviewing"]]}),
		]),
		(LEADER, "Công việc chờ lãnh đạo quyết định", [
			("Đợt chờ phê duyệt", "Approval Batch", {"status": "SUBMITTED"}),
			("Chính sách đang soạn", "Policy Version", {"status": "DRAFT"}),
			("Hồ sơ xác minh đang chờ", "Verification Case", {"status": "AWAITING_REVIEW"}),
		], [
			("Đợt trình chờ quyết định", "Approval Batch", {"status": "SUBMITTED"}),
			("Hồ sơ đơn lẻ chờ duyệt", "Support Application", {"workflow_state": "Pending Approval"}),
		], [
			("Xem đợt chờ duyệt", "Approval Batch", "list", {"status": "SUBMITTED"}),
			("Xem phiên bản chính sách", "Policy Version", "list", {}),
			("Báo cáo tài chính", "bao-cao-tai-chinh", "page", {}),
		]),
		(FINANCE, "Công việc chi trả", [
			("Khoản đang chờ chi", "Disbursement", {"status": "PENDING"}),
			("Khoản đã xác nhận chi", "Disbursement", {"status": "PAID"}),
		], [
			("Khoản chờ xác nhận chi", "Disbursement", {"status": "PENDING"}),
			("Hồ sơ đơn lẻ chờ chi", "Support Application", {"workflow_state": "Approved"}),
		], [
			("Xem khoản chờ chi", "Disbursement", "list", {"status": "PENDING"}),
			("Báo cáo tài chính", "bao-cao-tai-chinh", "page", {}),
		]),
	]
	selected_pages = [page for page in role_pages if page[0] in roles]
	if is_admin():
		selected_pages = role_pages
	home_title = selected_pages[0][1] if len(selected_pages) == 1 else "Công việc an sinh xã hội"
	overview, queues, quick_actions = [], [], []
	seen_cards, seen_queues, seen_actions = set(), set(), set()
	for _role, _title, card_defs, queue_defs, action_defs in selected_pages:
		for label, doctype, filters in card_defs:
			key = (doctype, label)
			if key in seen_cards or not frappe.has_permission(doctype, "read"):
				continue
			seen_cards.add(key)
			count = frappe.get_list(doctype, filters=filters, fields=[{"COUNT": "name", "as": "total"}])[0].total
			overview.append({"label": label, "count": count, "doctype": doctype, "filters": filters})
		for title, doctype, filters in queue_defs:
			key = (doctype, title)
			if key in seen_queues or not frappe.has_permission(doctype, "read"):
				continue
			seen_queues.add(key)
			if doctype == "Approval Batch":
				fields = ["name", "support_program", "status", "total_beneficiaries"]
			elif doctype == "Disbursement":
				fields = ["name", "household", "citizen", "status", "amount"]
			elif doctype == "Verification Case":
				fields = ["name", "household", "citizen", "status", "question_type"]
			else:
				fields = ["name", "household", "program", "workflow_state"]
			items = frappe.get_list(doctype, filters=filters, fields=fields, order_by="modified desc", limit=6)
			queues.append({"title": title, "doctype": doctype, "filters": filters, "items": [
				{"name": item.name, "status": item.get("status") or item.get("workflow_state"),
				 "subtitle": item.get("support_program") or item.get("citizen") or item.get("household") or item.get("program") or ""}
				for item in items
			]})
		for label, target, action_type, filters in action_defs:
			key = (target, action_type, label)
			if key in seen_actions:
				continue
			if action_type == "new" and not frappe.has_permission(target, "create"):
				continue
			if action_type == "list" and not frappe.has_permission(target, "read"):
				continue
			seen_actions.add(key)
			quick_actions.append({"label": label, "target": target, "type": action_type, "filters": filters})
	return {
		"cards": cards,
		"tasks": tasks,
		"roles": list(roles),
		"can_create": is_admin() or OFFICER in roles,
		"home_title": home_title,
		"overview": overview,
		"queues": queues,
		"quick_actions": quick_actions,
	}
