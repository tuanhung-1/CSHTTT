# Copyright (c) 2026, Student Project and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class SupportProgram(Document):
	def validate(self):
		self.validate_support_amount()
		self.validate_date_range()
		self.validate_beneficiary()
		previous = self.get_doc_before_save()
		if previous:
			if self.screening_status != previous.screening_status:
				frappe.throw("Trạng thái rà soát chỉ được cập nhật bởi hệ thống.")
			if frappe.db.exists("Eligibility Run", {"support_program": self.name}):
				locked = ("beneficiary_type", "target_group", "target_group_ref", "policy_version", "cutoff_date", "support_type", "support_amount", "start_date", "end_date")
				if any(self.has_value_changed(field) for field in locked):
					frappe.throw("Chương trình đã rà soát; hãy tạo chương trình mới để đổi điều kiện hoặc mức hỗ trợ.")

	def validate_support_amount(self):
		if flt(self.support_amount) < 0:
			frappe.throw(_("Support amount must be greater than or equal to zero."))

	def validate_date_range(self):
		if self.start_date and self.end_date and getdate(self.start_date) > getdate(self.end_date):
			frappe.throw(_("Start date must be earlier than or equal to end date."))

	def validate_beneficiary(self):
		if self.beneficiary_type not in {"Household", "Citizen"}:
			frappe.throw("Chương trình phải chọn đối tượng Hộ gia đình hoặc Công dân.")
		if self.beneficiary_type == "Citizen" and not self.target_group_ref:
			frappe.throw("Chương trình cho công dân cần chọn Nhóm đối tượng chính sách.")
		if self.target_group_ref and not frappe.db.get_value("Target Group", self.target_group_ref, "is_active"):
			frappe.throw("Nhóm đối tượng đã ngừng áp dụng.")
		if self.policy_version:
			version = frappe.db.get_value("Policy Version", self.policy_version, ["policy", "status"], as_dict=True)
			policy_type = frappe.db.get_value("Policy", version.policy, "policy_type") if version else None
			if policy_type not in (self.beneficiary_type, "Both"):
				frappe.throw("Loại đối tượng của phiên bản chính sách không phù hợp chương trình.")
		if flt(self.budget_estimate) < 0:
			frappe.throw("Ngân sách dự kiến không được âm.")
