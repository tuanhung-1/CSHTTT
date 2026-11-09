import frappe
from frappe.model.document import Document


class PolicyRule(Document):
	def validate(self):
		previous = self.get_doc_before_save()
		if previous and self.policy_version != previous.policy_version:
			frappe.throw("Không chuyển quy tắc sang phiên bản khác; hãy tạo quy tắc mới.")
		if frappe.db.get_value("Policy Version", self.policy_version, "status") != "DRAFT":
			frappe.throw("Chỉ được sửa quy tắc khi phiên bản chính sách ở trạng thái DRAFT.")
		if self.operator in ("EQ", "IN") and not self.expected_value:
			frappe.throw("Phép kiểm tra EQ/IN cần giá trị yêu cầu.")
		if frappe.db.exists("Policy Rule", {"policy_version": self.policy_version, "rule_code": self.rule_code, "name": ["!=", self.name]}):
			frappe.throw("Mã điều kiện đã tồn tại trong phiên bản này.")

	def on_trash(self):
		if frappe.db.get_value("Policy Version", self.policy_version, "status") != "DRAFT":
			frappe.throw("Không xóa quy tắc của phiên bản đã kích hoạt.")
