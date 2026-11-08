# Copyright (c) 2026, Student Project and contributors
# For license information, please see license.txt

from uuid import uuid4

import frappe
from frappe.tests import IntegrationTestCase as FrappeTestCase
from frappe.utils import add_days, nowdate


class TestCitizen(FrappeTestCase):
	def make_household(self, suffix=None, **values):
		suffix = suffix or uuid4().hex[:10]
		return frappe.get_doc(
			{
				"doctype": "Household",
				"household_code": f"HH-{suffix}",
				"head_name": "Legacy Head",
				**values,
			}
		).insert(ignore_permissions=True)

	def make_citizen(self, household, suffix=None, **values):
		suffix = suffix or uuid4().hex[:10]
		return frappe.get_doc(
			{
				"doctype": "Citizen",
				"citizen_code": f"CT-{suffix}",
				"full_name": "Test Citizen",
				"household": household,
				**values,
			}
		).insert(ignore_permissions=True)

	def test_single_head_and_member_count(self):
		household = self.make_household()
		self.make_citizen(household.name, relationship="Head")
		self.assertEqual(frappe.db.get_value("Household", household.name, "member_count"), 1)

		with self.assertRaises(frappe.ValidationError):
			self.make_citizen(household.name, relationship="Head")

	def test_head_citizen_must_belong_to_household_and_cannot_move(self):
		household = self.make_household()
		other_household = self.make_household()
		citizen = self.make_citizen(household.name, relationship="Head")

		household.head_citizen = citizen.name
		household.save(ignore_permissions=True)

		citizen.household = other_household.name
		with self.assertRaises(frappe.ValidationError):
			citizen.save(ignore_permissions=True)

		other_household.head_citizen = citizen.name
		with self.assertRaises(frappe.ValidationError):
			other_household.save(ignore_permissions=True)

	def test_non_negative_income_and_future_date_of_birth(self):
		with self.assertRaises(frappe.ValidationError):
			self.make_household(average_income=-1)

		household = self.make_household()
		with self.assertRaises(frappe.ValidationError):
			self.make_citizen(household.name, date_of_birth=add_days(nowdate(), 1))

	def test_codes_are_generated_when_blank(self):
		household = frappe.get_doc({"doctype": "Household", "head_name": "Generated Code Head"}).insert(
			ignore_permissions=True
		)
		self.assertRegex(household.household_code, r"^HH-\d{4}-\d{5}$")

		citizen = frappe.get_doc(
			{
				"doctype": "Citizen",
				"full_name": "Generated Code Citizen",
				"household": household.name,
			}
		).insert(ignore_permissions=True)
		self.assertRegex(citizen.citizen_code, r"^CT-\d{6}$")

	def test_national_id_is_normalized_and_unique(self):
		household = self.make_household()
		citizen = self.make_citizen(household.name, national_id=" 012345678901 ")
		self.assertEqual(citizen.national_id, "012345678901")

		with self.assertRaises(frappe.ValidationError):
			self.make_citizen(household.name, national_id="012345678901")

	def test_codes_are_unique(self):
		suffix = uuid4().hex[:10]
		household = self.make_household(suffix=suffix)
		with self.assertRaises(frappe.DuplicateEntryError):
			self.make_household(suffix=suffix)

		citizen = self.make_citizen(household.name, suffix=suffix)
		self.assertEqual(citizen.citizen_code, f"CT-{suffix}")
		with self.assertRaises(frappe.DuplicateEntryError):
			self.make_citizen(household.name, suffix=suffix)
