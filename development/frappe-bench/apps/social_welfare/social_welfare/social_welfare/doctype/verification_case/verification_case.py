import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class VerificationCase(Document):
	def validate(self):
		if frappe.flags.social_welfare_verification_action not in ("create", self.name):
			frappe.throw("Hồ sơ xác minh chỉ được thay đổi qua thao tác nghiệp vụ được phân quyền.", frappe.PermissionError)
		if bool(self.citizen) == bool(self.household) or self.beneficiary_type != ("Citizen" if self.citizen else "Household"):
			frappe.throw("Hồ sơ xác minh phải gắn với đúng một hộ hoặc công dân.")
		if self.question_type == "TARGET_GROUP" and not self.target_group:
			frappe.throw("Cần chọn nhóm đối tượng để xác minh.")
		if self.status == "COMPLETED" and not all((self.conclusion, self.finding, self.basis, self.completed_by, self.completed_at)):
			frappe.throw("Kết luận xác minh cần có nội dung, căn cứ và người xác minh.")
		if self.status == "COMPLETED" and self.conclusion == "CONFIRMED" and self.question_type == "TARGET_GROUP":
			if not self.verified_from or not self.verified_to or getdate(self.verified_from) > getdate(self.fact_date) or getdate(self.verified_to) < getdate(self.fact_date):
				frappe.throw("Khoảng hiệu lực xác minh nhóm phải bao gồm ngày dữ liệu cần xác minh.")

	def on_trash(self):
		frappe.throw("Không xóa hồ sơ xác minh; kết luận được giữ làm lịch sử.")
