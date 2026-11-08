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

	def validate_support_amount(self):
		if flt(self.support_amount) < 0:
			frappe.throw(_("Support amount must be greater than or equal to zero."))

	def validate_date_range(self):
		if self.start_date and self.end_date and getdate(self.start_date) > getdate(self.end_date):
			frappe.throw(_("Start date must be earlier than or equal to end date."))
