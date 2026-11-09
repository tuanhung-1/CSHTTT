# Copyright (c) 2026, Student Project and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import flt


class Household(Document):
	def before_naming(self):
		if not self.household_code:
			self.household_code = make_autoname("HH-.YYYY.-.#####", doctype=self.doctype)

	def validate(self):
		self.validate_average_income()
		self.validate_head_citizen()
		self.set_member_count()
		self.validate_assignment_and_legacy()

	def validate_assignment_and_legacy(self):
		previous = self.get_doc_before_save()
		if previous and self.assigned_verifier != previous.assigned_verifier and frappe.db.table_exists("Verification Case"):
			pending = frappe.db.sql(
				"SELECT v.name FROM `tabVerification Case` v LEFT JOIN `tabCitizen` c ON c.name=v.citizen "
				"WHERE v.status='AWAITING_REVIEW' AND (v.household=%s OR c.household=%s) LIMIT 1",
				(self.name, self.name),
			)
			if pending:
				frappe.throw("Hộ còn hồ sơ xác minh đang chờ. Kết luận hồ sơ trước khi đổi người được giao.")
		if (previous and self.poverty_status != previous.poverty_status) or (
			self.is_new() and self.poverty_status
		):
			frappe.throw("Hãy ghi phân loại trong Lịch sử phân loại; không sửa nhãn phân loại cũ.")
		if self.assigned_verifier:
			user = frappe.db.get_value("User", self.assigned_verifier, ["enabled", "user_type"], as_dict=True)
			if (
				not user
				or not user.enabled
				or user.user_type != "System User"
				or "Social Welfare Reviewer" not in frappe.get_roles(self.assigned_verifier)
			):
				frappe.throw(
					"Người được phân công phải là tài khoản hệ thống đang bật và có vai trò Người xác minh."
				)

	def validate_average_income(self):
		if flt(self.average_income) < 0:
			frappe.throw(_("Average income must be greater than or equal to zero."))

	def validate_head_citizen(self):
		if not self.head_citizen:
			return

		citizen = frappe.db.get_value("Citizen", self.head_citizen, ["household", "full_name", "relationship"], as_dict=True)
		if not citizen or citizen.household != self.name:
			frappe.throw(_("The head citizen must be a member of this household."))
		if citizen.relationship != "Head":
			frappe.throw("Công dân được chọn làm chủ hộ phải có quan hệ Chủ hộ.")
		self.head_name = citizen.full_name

	def set_member_count(self):
		self.member_count = frappe.db.count("Citizen", {"household": self.name}) if not self.is_new() else 0
