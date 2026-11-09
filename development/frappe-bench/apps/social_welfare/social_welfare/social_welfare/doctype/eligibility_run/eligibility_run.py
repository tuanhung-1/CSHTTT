import frappe
from frappe.model.document import Document


class EligibilityRun(Document):
	def validate(self):
		if frappe.flags.social_welfare_bulk_action != self.name and not self.is_new():
			frappe.throw("Lần rà soát đã lưu không được sửa trực tiếp.")
		if self.is_new() and not frappe.flags.social_welfare_bulk_action:
			frappe.throw("Hãy chạy rà soát từ Chương trình hỗ trợ.")

	def on_trash(self):
		frappe.throw("Không xóa lần rà soát để giữ lịch sử.")
