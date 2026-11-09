"""Human-reviewed batch approval and payment recording."""

from collections import defaultdict

import frappe
from frappe.utils import flt, now_datetime

from social_welfare.eligibility import bulk_action, require_officer
from social_welfare.permissions import FINANCE, LEADER, is_admin


def require_role(role):
	if not is_admin() and role not in frappe.get_roles():
		frappe.throw("Vai trò hiện tại không được thực hiện thao tác này.", frappe.PermissionError)


def ensure_not_in_active_batch(result_name, current_batch=None):
	rows = frappe.db.sql(
		"SELECT b.name FROM `tabApproval Batch Item` i JOIN `tabApproval Batch` b ON b.name=i.parent "
		"WHERE i.eligibility_result=%s AND i.selection_status='SELECTED' "
		"AND b.status IN ('SUBMITTED','APPROVED') AND b.name!=%s LIMIT 1",
		(result_name, current_batch or ""),
	)
	if rows:
		frappe.throw("Đối tượng đã nằm trong một đợt đang trình hoặc đã duyệt từ lần rà soát này.")


@frappe.whitelist(methods=["POST"])
def create_batch(run_name, selected_results):
	require_officer()
	run = frappe.get_doc("Eligibility Run", run_name)
	run.check_permission("read")
	if run.status != "COMPLETED":
		frappe.throw("Chỉ lập đợt từ lần rà soát đã hoàn tất.")
	selected = frappe.parse_json(selected_results) if isinstance(selected_results, str) else selected_results
	if not isinstance(selected, list) or not selected or len(selected) > 5000 or len(set(selected)) != len(selected):
		frappe.throw("Hãy chọn danh sách kết quả đủ điều kiện, không trùng lặp.")
	program = frappe.get_doc("Support Program", run.support_program)
	items = []
	for name in selected:
		result = frappe.get_doc("Eligibility Result", name)
		result.check_permission("read")
		if result.eligibility_run != run.name or result.result_status != "ELIGIBLE":
			frappe.throw("Chỉ chọn kết quả đủ điều kiện của đúng lần rà soát.")
		ensure_not_in_active_batch(name)
		items.append({"beneficiary_type": result.beneficiary_type, "household": result.household, "citizen": result.citizen, "eligibility_result": name, "proposed_amount": flt(program.support_amount) if program.support_type == "CASH" else 0, "selection_status": "SELECTED", "modified_by_user": frappe.session.user, "modified_at": now_datetime()})
	batch = frappe.get_doc({"doctype": "Approval Batch", "support_program": program.name, "eligibility_run": run.name, "status": "DRAFT", "items": items})
	with bulk_action("create"):
		batch.insert(ignore_permissions=True)
	return batch.name


@frappe.whitelist(methods=["POST"])
def submit_batch(name):
	require_officer()
	frappe.db.sql("SELECT name FROM `tabApproval Batch` WHERE name=%s FOR UPDATE", name)
	batch = frappe.get_doc("Approval Batch", name)
	batch.check_permission("read")
	if batch.status != "DRAFT" or not batch.total_beneficiaries:
		frappe.throw("Đợt cần có ít nhất một đối tượng được chọn ở trạng thái DRAFT.")
	for item in batch.items:
		if item.selection_status == "SELECTED":
			frappe.db.sql("SELECT name FROM `tabEligibility Result` WHERE name=%s FOR UPDATE", item.eligibility_result)
			ensure_not_in_active_batch(item.eligibility_result, batch.name)
	batch.status, batch.submitted_by, batch.submitted_at = "SUBMITTED", frappe.session.user, now_datetime()
	with bulk_action(batch.name):
		batch.save(ignore_permissions=True)
	return batch.name


@frappe.whitelist(methods=["POST"])
def decide_batch(name, decision, note):
	require_role(LEADER)
	if decision not in {"APPROVED", "REJECTED", "RETURNED"} or not (note or "").strip():
		frappe.throw("Chọn quyết định và nhập ý kiến của lãnh đạo.")
	frappe.db.sql("SELECT name FROM `tabApproval Batch` WHERE name=%s FOR UPDATE", name)
	batch = frappe.get_doc("Approval Batch", name)
	batch.check_permission("read")
	if batch.status != "SUBMITTED":
		frappe.throw("Chỉ quyết định đợt đã trình.")
	if not is_admin() and batch.submitted_by == frappe.session.user:
		frappe.throw("Người trình không được tự quyết định đợt mình đã trình.", frappe.PermissionError)
	batch.status, batch.decision_note = decision, note.strip()
	batch.decided_by, batch.decided_at = frappe.session.user, now_datetime()
	with bulk_action(batch.name):
		batch.save(ignore_permissions=True)
	if decision == "APPROVED":
		program = frappe.get_doc("Support Program", batch.support_program)
		for item in batch.items:
			if item.selection_status != "SELECTED":
				continue
			if frappe.db.exists("Disbursement", {"approval_batch": batch.name, "eligibility_result": item.eligibility_result}):
				frappe.throw("Đợt này đã có khoản chi cho đối tượng.")
			disbursement = frappe.get_doc({"doctype": "Disbursement", "approval_batch": batch.name, "eligibility_result": item.eligibility_result, "beneficiary_type": item.beneficiary_type, "household": item.household, "citizen": item.citizen, "support_type": program.support_type, "amount": item.proposed_amount if program.support_type == "CASH" else 0, "item_description": item.item_description if program.support_type == "IN_KIND" else None, "quantity": item.quantity if program.support_type == "IN_KIND" else None, "status": "PENDING"})
			with bulk_action("create"):
				disbursement.insert(ignore_permissions=True)
	return batch.name


@frappe.whitelist(methods=["POST"])
def reset_batch(name):
	require_officer()
	frappe.db.sql("SELECT name FROM `tabApproval Batch` WHERE name=%s FOR UPDATE", name)
	batch = frappe.get_doc("Approval Batch", name)
	batch.check_permission("read")
	if batch.status != "RETURNED":
		frappe.throw("Chỉ đợt bị trả lại mới được đưa về bản nháp.")
	batch.status = "DRAFT"
	with bulk_action(batch.name):
		batch.save(ignore_permissions=True)
	return batch.name


@frappe.whitelist(methods=["POST"])
def confirm_disbursement(name, payment_note, receipt_file=None):
	require_role(FINANCE)
	if not (payment_note or "").strip():
		frappe.throw("Cần ghi chú khi xác nhận chi trả.")
	frappe.db.sql("SELECT name FROM `tabDisbursement` WHERE name=%s FOR UPDATE", name)
	doc = frappe.get_doc("Disbursement", name)
	doc.check_permission("read")
	if doc.status != "PENDING":
		frappe.throw("Chỉ khoản chi đang chờ mới được xác nhận.")
	doc.status, doc.payment_note = "PAID", payment_note.strip()
	doc.paid_on, doc.confirmed_by = now_datetime(), frappe.session.user
	if receipt_file:
		doc.receipt_file = receipt_file
	with bulk_action(doc.name):
		doc.save(ignore_permissions=True)
	return doc.name


@frappe.whitelist()
def financial_report():
	if not is_admin() and not {FINANCE, LEADER}.intersection(frappe.get_roles()):
		frappe.throw("Bạn không có quyền xem báo cáo tài chính.", frappe.PermissionError)
	programs = {row.name: row.program_name for row in frappe.get_all("Support Program", fields=["name", "program_name"])}
	batches = {row.name: row for row in frappe.get_all("Approval Batch", fields=["name", "support_program", "status"])}
	by_program = defaultdict(lambda: {"approved": 0.0, "paid": 0.0, "pending": 0.0, "paid_count": 0, "pending_count": 0})
	by_month = defaultdict(float)
	for row in frappe.get_all("Disbursement", fields=["approval_batch", "support_type", "amount", "status", "paid_on"]):
		batch = batches.get(row.approval_batch)
		if not batch or batch.status != "APPROVED":
			continue
		entry = by_program[batch.support_program]
		if row.support_type == "CASH":
			entry["approved"] += flt(row.amount)
		if row.status == "PAID":
			entry["paid_count"] += 1
			if row.support_type == "CASH":
				entry["paid"] += flt(row.amount)
				by_month[str(row.paid_on)[:7]] += flt(row.amount)
		elif row.status == "PENDING":
			entry["pending_count"] += 1
			if row.support_type == "CASH":
				entry["pending"] += flt(row.amount)
	rows = [{"program": key, "label": programs.get(key, key), **value} for key, value in sorted(by_program.items())]
	return {"programs": rows, "months": [{"month": key, "amount": value} for key, value in sorted(by_month.items())], "totals": {key: sum(row[key] for row in rows) for key in ("approved", "paid", "pending", "paid_count", "pending_count")}, "legacy_note": "Hồ sơ Support Application cũ ở trạng thái Paid không được tính là khoản chi thực tế nếu chưa có Disbursement."}
