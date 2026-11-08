"""Run only on an isolated test site; every test rolls back its own records."""

import unittest
from unittest.mock import patch
from uuid import uuid4

import frappe
from frappe.model.workflow import apply_workflow

from social_welfare.api import dashboard, household_history, void_classification
from social_welfare.permissions import FINANCE, LEADER, OFFICER, VERIFIER
from social_welfare.social_welfare.doctype.household_classification.household_classification import (
	get_effective_classification,
)


class TestWardWorkflow(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self.addCleanup(frappe.db.rollback)
		self.addCleanup(frappe.set_user, "Administrator")
		throttle = patch("frappe.core.doctype.user.user.throttle_user_creation")
		throttle.start()
		self.addCleanup(throttle.stop)
		self.suffix = uuid4().hex[:8]
		self.users = {}
		for role in (OFFICER, VERIFIER, LEADER, FINANCE):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": f"{role.split()[-1].lower()}-{self.suffix}@example.com",
					"first_name": role.split()[-1],
					"enabled": 1,
					"send_welcome_email": 0,
					"roles": [{"role": role}],
				}
			).insert(ignore_permissions=True)
			self.users[role] = user.name
		self.household = frappe.get_doc(
			{"doctype": "Household", "head_name": "Test Household", "assigned_verifier": self.users[VERIFIER]}
		).insert()
		self.other = frappe.get_doc({"doctype": "Household", "head_name": "Unassigned Household"}).insert()

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def classification(self, start="2026-01-01", end="2026-12-31", **values):
		return frappe.get_doc(
			{
				"doctype": "Household Classification",
				"household": self.household.name,
				"classification": "Poor Household",
				"period": "2026",
				"valid_from": start,
				"valid_to": end,
				"basis": "Demo decision",
				**values,
			}
		).insert()

	def program(self, group="disaster"):
		return frappe.get_doc(
			{
				"doctype": "Support Program",
				"code": "TEST-" + self.suffix,
				"program_name": "Test program",
				"start_date": "2026-01-01",
				"end_date": "2027-12-31",
				"target_group": group,
				"active": 1,
			}
		).insert()

	def application(self, program):
		return frappe.get_doc(
			{
				"doctype": "Support Application",
				"household": self.household.name,
				"program": program.name,
				"application_date": "2026-06-01",
				"requested_amount": 1000000,
			}
		).insert()

	def test_periods_are_preserved_and_resolved_by_date(self):
		first = self.classification()
		second = self.classification(
			"2027-01-01", "2027-12-31", classification="Near-poor Household", period="2027"
		)
		self.assertEqual(get_effective_classification(self.household.name, "2026-12-31").name, first.name)
		self.assertEqual(get_effective_classification(self.household.name, "2027-01-01").name, second.name)
		self.assertIsNone(get_effective_classification(self.household.name, "2028-01-01"))
		self.assertEqual(frappe.db.count("Household Classification", {"household": self.household.name}), 2)

	def test_overlap_invalid_range_and_missing_basis_are_rejected(self):
		self.classification()
		for start, end, extra in [
			("2026-12-31", "2027-12-31", {}),
			("2028-12-31", "2028-01-01", {}),
			("2028-01-01", "2028-12-31", {"basis": ""}),
		]:
			with self.assertRaises(frappe.ValidationError):
				self.classification(start, end, **extra)

	def test_history_is_immutable_and_void_keeps_original(self):
		record = self.classification()
		record.classification = "Normal"
		with self.assertRaises(frappe.ValidationError):
			record.save()
		record.reload()
		record.is_void = 1
		record.flags.allow_void = True
		with self.assertRaises(frappe.ValidationError):
			record.save()
		record.reload()
		with self.assertRaises(frappe.ValidationError):
			record.delete()
		frappe.set_user(self.users[OFFICER])
		self.assertTrue(frappe.has_permission("Household Classification", "write"))
		self.assertFalse(frappe.has_permission("Household Classification", "write", doc=record))
		with self.assertRaises(frappe.PermissionError):
			void_classification(record.name, "Correction")
		frappe.set_user(self.users[LEADER])
		void_classification(record.name, "Correction with retained evidence")
		record.reload()
		self.assertEqual(record.classification, "Poor Household")
		self.assertEqual(record.voided_by, self.users[LEADER])
		self.assertIsNone(get_effective_classification(self.household.name, "2026-06-01"))
		frappe.set_user(self.users[OFFICER])
		self.classification(classification="Normal")

	def test_legacy_is_not_current_and_cannot_be_forged(self):
		with self.assertRaises(frappe.ValidationError):
			self.classification(is_legacy=1)
		forged = frappe.get_doc(
			{
				"doctype": "Household Classification",
				"household": self.household.name,
				"classification": "Poor Household",
				"period": "Forged legacy",
				"basis": "Forged",
				"is_legacy": 1,
			}
		)
		forged.flags.from_legacy_migration = True
		with self.assertRaises(frappe.ValidationError):
			forged.insert()
		from social_welfare.patches.v0_1.migrate_legacy_classifications import execute

		frappe.db.set_value("Household", self.household.name, "poverty_status", "Poor Household")
		execute()
		execute()
		self.assertEqual(
			frappe.db.count("Household Classification", {"household": self.household.name, "is_legacy": 1}), 1
		)
		self.assertIsNone(get_effective_classification(self.household.name, "2026-06-01"))

	def test_verifier_lists_direct_reads_and_dashboard_are_scoped(self):
		self.classification()
		citizen = frappe.get_doc(
			{"doctype": "Citizen", "full_name": "Assigned citizen", "household": self.household.name}
		).insert()
		outsider = frappe.get_doc(
			{"doctype": "Citizen", "full_name": "Other citizen", "household": self.other.name}
		).insert()
		frappe.set_user(self.users[VERIFIER])
		self.assertEqual(frappe.get_list("Household", pluck="name"), [self.household.name])
		self.assertIn(citizen.name, frappe.get_list("Citizen", pluck="name"))
		self.assertNotIn(outsider.name, frappe.get_list("Citizen", pluck="name"))
		self.assertFalse(frappe.has_permission("Household", doc=self.other, ptype="read"))
		with self.assertRaises(frappe.PermissionError):
			household_history(self.other.name)
		self.assertEqual(next(c for c in dashboard()["cards"] if c["doctype"] == "Household")["count"], 1)
		self.assertFalse(frappe.has_permission("Household", "write", doc=self.household))

	def test_role_matrix_and_no_hard_delete(self):
		expected = {
			OFFICER: (True, True),
			VERIFIER: (False, False),
			LEADER: (False, False),
			FINANCE: (False, False),
		}
		for role, (create_household, create_program) in expected.items():
			frappe.set_user(self.users[role])
			self.assertEqual(bool(frappe.has_permission("Household", "create")), create_household)
			self.assertEqual(bool(frappe.has_permission("Support Program", "create")), create_program)
			self.assertFalse(frappe.has_permission("Household", "delete"))
		frappe.set_user(self.users[FINANCE])
		self.assertFalse(frappe.has_permission("Citizen", "read"))
		self.assertNotIn("Citizen", [card["doctype"] for card in dashboard()["cards"]])
		self.assertNotIn("Household Classification", [card["doctype"] for card in dashboard()["cards"]])
		frappe.set_user("Administrator")
		with self.assertRaises(frappe.ValidationError):
			self.household.delete()

	def test_application_uses_effective_history_not_legacy_label(self):
		program = self.program("poor")
		with self.assertRaises(frappe.ValidationError):
			self.application(program)
		self.classification()
		self.assertEqual(self.application(program).workflow_state, "Draft")

	def test_full_workflow_and_field_tampering(self):
		program = self.program()
		frappe.set_user(self.users[OFFICER])
		doc = self.application(program)
		doc = apply_workflow(doc, "Submit")
		self.assertEqual(doc.submitted_by, self.users[OFFICER])
		frappe.set_user(self.users[VERIFIER])
		doc = frappe.get_doc("Support Application", doc.name)
		doc = apply_workflow(doc, "Start Review")
		doc.requested_amount = 2
		with self.assertRaises(frappe.PermissionError):
			doc.save()
		doc.reload()
		doc.verification_note = "Verified mock evidence"
		doc.save()
		doc = apply_workflow(doc, "Complete Verification")
		with self.assertRaises(frappe.ValidationError):
			apply_workflow(doc, "Approve")
		frappe.set_user(self.users[LEADER])
		doc.reload()
		doc.review_note, doc.approved_amount = "Approved in test", 1000000
		doc.save()
		doc = apply_workflow(doc, "Approve")
		self.assertEqual(doc.decided_by, self.users[LEADER])
		with self.assertRaises(frappe.ValidationError):
			apply_workflow(doc, "Mark as Paid")
		frappe.set_user(self.users[FINANCE])
		doc.reload()
		doc.payment_note = "Mock payment confirmation"
		doc.save()
		doc = apply_workflow(doc, "Mark as Paid")
		self.assertEqual(doc.workflow_state, "Paid")
		self.assertEqual(doc.paid_by, self.users[FINANCE])

	def test_submitter_cannot_approve_with_multiple_roles(self):
		user = frappe.get_doc("User", self.users[OFFICER])
		user.add_roles(LEADER)
		program = self.program()
		frappe.set_user(self.users[OFFICER])
		doc = apply_workflow(self.application(program), "Submit")
		frappe.set_user(self.users[VERIFIER])
		doc = apply_workflow(doc, "Start Review")
		doc.verification_note = "Verified"
		doc.save()
		doc = apply_workflow(doc, "Complete Verification")
		frappe.set_user(self.users[OFFICER])
		doc.reload()
		doc.review_note = "Attempt to self approve"
		doc.save()
		with self.assertRaises(frappe.ValidationError):
			apply_workflow(doc, "Approve")
