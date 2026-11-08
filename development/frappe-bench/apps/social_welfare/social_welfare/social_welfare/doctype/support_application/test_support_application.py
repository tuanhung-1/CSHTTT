# Copyright (c) 2026, Student Project and contributors
# For license information, please see license.txt

from uuid import uuid4

import frappe
from frappe.tests import IntegrationTestCase as FrappeTestCase
from frappe.utils import add_days, nowdate


class TestSupportApplication(FrappeTestCase):
	def test_application_code_is_generated_when_blank(self):
		suffix = uuid4().hex[:10]
		household = frappe.get_doc(
			{
				"doctype": "Household",
				"head_name": "Application Test Head",
			}
		).insert(ignore_permissions=True)
		program = frappe.get_doc(
			{
				"doctype": "Support Program",
				"code": f"PRG-{suffix}",
				"program_name": "Application Test Program",
				"start_date": nowdate(),
				"end_date": add_days(nowdate(), 30),
				"target_group": "disaster",
			}
		).insert(ignore_permissions=True)

		application = frappe.get_doc(
			{
				"doctype": "Support Application",
				"household": household.name,
				"program": program.name,
				"requested_amount": 1000000,
			}
		).insert(ignore_permissions=True)

		self.assertRegex(application.application_code, r"^APP-\d{4}-\d{5}$")
		self.assertEqual(application.workflow_state, "Draft")
