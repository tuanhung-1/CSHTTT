# Copyright (c) 2026, Student Project and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import flt


class SupportApplication(Document):
	def before_naming(self):
		if not self.application_code:
			self.application_code = make_autoname("APP-.YYYY.-.#####", doctype=self.doctype)

	def before_insert(self):
		if self.workflow_state != "Draft":
			frappe.throw(_("New applications must start in Draft."))

	def validate(self):
		self.validate_amounts()
		self.validate_household_program_uniqueness()
		self.validate_target_group()

	def validate_amounts(self):
		if flt(self.requested_amount) < 0:
			frappe.throw(_("Requested amount must be greater than or equal to zero."))
		if flt(self.approved_amount) < 0:
			frappe.throw(_("Approved amount must be greater than or equal to zero."))

	def validate_household_program_uniqueness(self):
		filters = {
			"household": self.household,
			"program": self.program,
			"name": ["!=", self.name],
		}
		if frappe.db.exists("Support Application", filters):
			frappe.throw(_("A household can have only one application for the same program."))

	def validate_target_group(self):
		if not self.household or not self.program:
			return

		target_group = frappe.db.get_value("Support Program", self.program, "target_group")
		poverty_status = frappe.db.get_value("Household", self.household, "poverty_status")
		required_status = {
			"poor": "Poor Household",
			"near_poor": "Near-poor Household",
		}.get(target_group)

		if required_status and poverty_status != required_status:
			frappe.throw(_("The household classification does not match the program target group."))
