import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime

from social_welfare.permissions import OFFICER, is_admin


class ApprovalBatch(Document):
	def validate(self):
		if self.is_new() and not frappe.flags.social_welfare_bulk_action:
			frappe.throw("Hãy tạo đợt từ kết quả rà soát.")
		previous = self.get_doc_before_save()
		if previous and (self.support_program != previous.support_program or self.eligibility_run != previous.eligibility_run):
			frappe.throw("Không đổi chương trình hoặc lần rà soát của đợt đã tạo.")
		if previous and previous.status != "DRAFT" and frappe.flags.social_welfare_bulk_action != self.name:
			frappe.throw("Đợt đã trình không được sửa danh sách.")
		if previous and self.status != previous.status and frappe.flags.social_welfare_bulk_action != self.name:
			frappe.throw("Hãy dùng nút chuyển trạng thái của đợt trình.")
		if previous and self.status != previous.status and (previous.status, self.status) not in {
			("DRAFT", "SUBMITTED"), ("SUBMITTED", "APPROVED"),
			("SUBMITTED", "REJECTED"), ("SUBMITTED", "RETURNED"), ("RETURNED", "DRAFT"),
		}:
			frappe.throw("Chuyển trạng thái đợt trình không hợp lệ.")
		if previous and previous.status == "DRAFT" and frappe.flags.social_welfare_bulk_action != self.name and not is_admin() and OFFICER not in frappe.get_roles():
			frappe.throw("Chỉ cán bộ an sinh được sửa bản nháp.", frappe.PermissionError)
		if frappe.db.get_value("Eligibility Run", self.eligibility_run, "support_program") != self.support_program:
			frappe.throw("Chương trình và lần rà soát không khớp.")
		seen = set()
		if previous and frappe.flags.social_welfare_bulk_action != self.name:
			if {row.name for row in previous.items} - {row.name for row in self.items}:
				frappe.throw("Không xóa dòng đã lưu. Hãy chọn REMOVED và ghi lý do.")
		support_type = frappe.db.get_value("Support Program", self.support_program, "support_type")
		for item in self.items:
			result = frappe.db.get_value("Eligibility Result", item.eligibility_result, ["eligibility_run", "beneficiary_type", "household", "citizen", "result_status"], as_dict=True)
			if not result or result.eligibility_run != self.eligibility_run or result.result_status != "ELIGIBLE":
				frappe.throw("Đợt chỉ nhận đối tượng đủ điều kiện từ đúng lần rà soát.")
			if item.eligibility_result in seen:
				frappe.throw("Một đối tượng xuất hiện nhiều lần trong đợt trình.")
			seen.add(item.eligibility_result)
			if (item.beneficiary_type, item.household, item.citizen) != (result.beneficiary_type, result.household, result.citizen):
				frappe.throw("Đối tượng trong dòng không khớp kết quả rà soát.")
			if flt(item.proposed_amount) < 0:
				frappe.throw("Số tiền đề xuất không được âm.")
			if support_type == "CASH" and self.status != "DRAFT" and item.selection_status == "SELECTED" and flt(item.proposed_amount) <= 0:
				frappe.throw("Dòng hỗ trợ tiền cần số tiền đề xuất lớn hơn 0.")
			if support_type == "IN_KIND" and self.status != "DRAFT" and item.selection_status == "SELECTED" and (not item.item_description or flt(item.quantity) <= 0):
				frappe.throw("Dòng hỗ trợ hiện vật cần tên hiện vật và số lượng.")
			if item.selection_status == "REMOVED" and not item.change_reason:
				frappe.throw("Cần nêu lý do loại đối tượng.")
			if previous and frappe.flags.social_welfare_bulk_action != self.name:
				old = next((row for row in previous.items if row.name == item.name), None)
				if old and (old.selection_status != item.selection_status or flt(old.proposed_amount) != flt(item.proposed_amount)):
					if not item.change_reason or item.change_reason == old.change_reason:
						frappe.throw("Cần nhập lý do mới khi sửa hoặc khôi phục đối tượng.")
					item.modified_by_user, item.modified_at = frappe.session.user, now_datetime()
		self.total_beneficiaries = sum(row.selection_status == "SELECTED" for row in self.items)
		self.total_amount = sum(flt(row.proposed_amount) for row in self.items if row.selection_status == "SELECTED")

	def on_trash(self):
		frappe.throw("Không xóa đợt trình để giữ lịch sử.")
