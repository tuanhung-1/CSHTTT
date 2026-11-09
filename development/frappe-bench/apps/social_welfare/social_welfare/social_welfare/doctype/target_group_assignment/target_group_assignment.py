import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class TargetGroupAssignment(Document):
	def validate(self):
		if bool(self.citizen) == bool(self.household):
			frappe.throw("Chọn đúng một đối tượng: Công dân hoặc Hộ gia đình.")
		if getdate(self.valid_from) > getdate(self.valid_to):
			frappe.throw("Ngày bắt đầu hiệu lực không được sau ngày kết thúc.")
		if self.is_new():
			if self.status != "ACTIVE" or self.void_reason:
				frappe.throw("Gán nhóm mới phải ở trạng thái ACTIVE.")
			if not self.verification_case:
				frappe.throw("Cần hồ sơ xác minh đã kết luận trước khi gán nhóm đối tượng.")
			verification = frappe.get_doc("Verification Case", self.verification_case)
			verification.check_permission("read")
			if verification.status != "COMPLETED" or verification.conclusion != "CONFIRMED" or verification.question_type != "TARGET_GROUP":
				frappe.throw("Hồ sơ xác minh chưa xác nhận nhóm đối tượng.")
			if verification.target_group != self.target_group or verification.citizen != self.citizen or verification.household != self.household:
				frappe.throw("Hồ sơ xác minh không khớp nhóm hoặc đối tượng được gán.")
			if getdate(self.valid_from) < getdate(verification.verified_from) or getdate(self.valid_to) > getdate(verification.verified_to):
				frappe.throw("Khoảng hiệu lực gán nhóm phải nằm trong thời gian đã được xác minh.")
			if not frappe.db.get_value("Target Group", self.target_group, "is_active"):
				frappe.throw("Nhóm đối tượng đã ngừng áp dụng.")
			field = "citizen" if self.citizen else "household"
			frappe.db.sql(f"SELECT name FROM `tab{('Citizen' if self.citizen else 'Household')}` WHERE name=%s FOR UPDATE", self.get(field))
			if frappe.db.exists("Target Group Assignment", {
				field: self.get(field), "target_group": self.target_group, "status": "ACTIVE",
				"valid_from": ["<=", self.valid_to], "valid_to": [">=", self.valid_from],
			}):
				frappe.throw("Nhóm này đã được gán cho đối tượng trong khoảng hiệu lực chồng lấn.")
			return
		previous = self.get_doc_before_save()
		protected = ("target_group", "citizen", "household", "verification_case", "valid_from", "valid_to", "evidence")
		if any(self.has_value_changed(field) for field in protected):
			frappe.throw("Lịch sử gán nhóm đã lưu không được sửa. Hãy tạo bản ghi mới.")
		if any(self.has_value_changed(field) for field in ("status", "void_reason")):
			if not (
				frappe.flags.social_welfare_void_target_group_assignment == self.name
				and previous.status == "ACTIVE" and self.status == "VOID" and self.void_reason
			):
				frappe.throw("Chỉ được hủy hiệu lực có lý do qua thao tác được phân quyền.")

	def on_trash(self):
		frappe.throw("Không xóa lịch sử gán nhóm đối tượng.")
