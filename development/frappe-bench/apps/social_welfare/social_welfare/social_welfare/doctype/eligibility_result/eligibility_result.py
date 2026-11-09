import frappe
from frappe.model.document import Document


class EligibilityResult(Document):
	def validate(self):
		if not frappe.flags.social_welfare_bulk_action:
			frappe.throw("Kết quả rà soát chỉ được tạo bởi hệ thống.")
		if bool(self.household) == bool(self.citizen):
			frappe.throw("Kết quả phải gắn đúng một hộ hoặc công dân.")
		if self.beneficiary_type != ("Citizen" if self.citizen else "Household"):
			frappe.throw("Loại đối tượng không khớp kết quả.")
		field = "citizen" if self.citizen else "household"
		if self.is_new() and frappe.db.exists("Eligibility Result", {"eligibility_run": self.eligibility_run, field: self.get(field)}):
			frappe.throw("Đối tượng đã có kết quả trong lần rà soát này.")

	def on_trash(self):
		frappe.throw("Không xóa kết quả rà soát.")
