import frappe
from frappe.model.document import Document
from frappe.utils import flt


class Disbursement(Document):
	def validate(self):
		if not frappe.flags.social_welfare_bulk_action:
			frappe.throw("Khoản chi chỉ được tạo/cập nhật qua quy trình đợt đã duyệt.")
		if bool(self.household) == bool(self.citizen):
			frappe.throw("Khoản chi phải gắn đúng một hộ hoặc công dân.")
		if self.support_type == "CASH" and flt(self.amount) <= 0:
			frappe.throw("Khoản hỗ trợ tiền cần số tiền lớn hơn 0.")
		if self.support_type == "IN_KIND" and (not self.item_description or flt(self.quantity) <= 0):
			frappe.throw("Khoản hỗ trợ hiện vật cần tên hiện vật và số lượng.")
		if self.is_new():
			if frappe.db.get_value("Approval Batch", self.approval_batch, "status") != "APPROVED":
				frappe.throw("Chỉ tạo khoản chi từ đợt đã phê duyệt.")
			if frappe.db.exists("Disbursement", {"approval_batch": self.approval_batch, "eligibility_result": self.eligibility_result}):
				frappe.throw("Đối tượng đã có khoản chi trong đợt này.")
		elif self.get_doc_before_save().status == "PAID":
			frappe.throw("Khoản chi đã xác nhận không được sửa.")

	def on_trash(self):
		frappe.throw("Không xóa khoản chi để giữ lịch sử tài chính.")
