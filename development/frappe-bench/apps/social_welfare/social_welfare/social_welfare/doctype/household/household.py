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

	def validate_average_income(self):
		if flt(self.average_income) < 0:
			frappe.throw(_("Average income must be greater than or equal to zero."))

	def validate_head_citizen(self):
		if not self.head_citizen:
			return

		citizen_household = frappe.db.get_value("Citizen", self.head_citizen, "household")
		if citizen_household != self.name:
			frappe.throw(_("The head citizen must be a member of this household."))

	def set_member_count(self):
		self.member_count = frappe.db.count("Citizen", {"household": self.name}) if not self.is_new() else 0
