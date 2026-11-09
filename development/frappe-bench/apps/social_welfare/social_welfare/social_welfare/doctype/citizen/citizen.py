# Copyright (c) 2026, Student Project and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import getdate, nowdate


class Citizen(Document):
	def before_naming(self):
		if not self.citizen_code:
			self.citizen_code = make_autoname("CT-.######", doctype=self.doctype)

	def validate(self):
		self.validate_pending_verification()
		self.validate_national_id()
		self.validate_date_of_birth()
		self.validate_single_household_head()
		self.validate_selected_head_household()
		self.warn_about_possible_duplicates()

	def validate_pending_verification(self):
		previous = self.get_doc_before_save()
		if previous and previous.household != self.household and frappe.db.table_exists("Verification Case"):
			if frappe.db.exists("Verification Case", {"citizen": self.name, "status": "AWAITING_REVIEW"}):
				frappe.throw("Công dân còn hồ sơ xác minh đang chờ. Kết luận trước khi chuyển sang hộ khác.")

	def after_insert(self):
		update_member_count(self.household)
		self.link_first_household_head()

	def on_update(self):
		previous = self.get_doc_before_save()
		update_member_count(self.household)
		if previous and previous.household != self.household:
			update_member_count(previous.household)
		if self.relationship == "Head":
			self.link_first_household_head()
		if self.relationship == "Head" and frappe.db.get_value("Household", self.household, "head_citizen") == self.name:
			frappe.db.set_value("Household", self.household, "head_name", self.full_name)

	def link_first_household_head(self):
		if self.relationship != "Head" or not self.household:
			return
		if not frappe.db.get_value("Household", self.household, "head_citizen"):
			frappe.db.set_value("Household", self.household, {"head_citizen": self.name, "head_name": self.full_name})

	def after_delete(self):
		update_member_count(self.household)

	def validate_date_of_birth(self):
		if self.date_of_birth and getdate(self.date_of_birth) > getdate(nowdate()):
			frappe.throw(_("Date of birth cannot be in the future."))

	def validate_national_id(self):
		normalized_id = "".join((self.national_id or "").split()).upper()
		self.national_id = normalized_id or None
		if not self.national_id:
			return

		duplicate = frappe.db.exists("Citizen", {"national_id": self.national_id, "name": ["!=", self.name]})
		if duplicate:
			frappe.throw(_("National ID already belongs to Citizen {0}.").format(duplicate))

	def warn_about_possible_duplicates(self):
		identity_fields = ("full_name", "date_of_birth", "phone")
		previous = self.get_doc_before_save()
		if previous and all(previous.get(field) == self.get(field) for field in identity_fields):
			return

		possible_duplicates = set()
		if self.full_name and self.date_of_birth:
			possible_duplicates.update(
				frappe.get_all(
					"Citizen",
					filters={
						"full_name": self.full_name,
						"date_of_birth": self.date_of_birth,
						"name": ["!=", self.name],
					},
					pluck="name",
					limit=5,
				)
			)

		if self.phone:
			possible_duplicates.update(
				frappe.get_all(
					"Citizen",
					filters={"phone": self.phone, "name": ["!=", self.name]},
					pluck="name",
					limit=5,
				)
			)

		if possible_duplicates:
			frappe.msgprint(
				_("Possible duplicate Citizen records: {0}.").format(", ".join(sorted(possible_duplicates))),
				title=_("Possible Duplicate"),
				indicator="orange",
			)

	def validate_single_household_head(self):
		if self.relationship != "Head":
			return

		filters = {
			"household": self.household,
			"relationship": "Head",
			"name": ["!=", self.name],
		}
		if frappe.db.exists("Citizen", filters):
			frappe.throw(_("A household can have only one citizen marked as Head."))

	def validate_selected_head_household(self):
		selected_by_household = frappe.db.get_value("Household", {"head_citizen": self.name}, "name")
		if selected_by_household and selected_by_household != self.household:
			frappe.throw(_("A selected head citizen cannot be moved to another household."))
		if selected_by_household and self.relationship != "Head":
			frappe.throw("Công dân đang được chọn làm chủ hộ không thể đổi quan hệ khỏi Chủ hộ.")


def update_member_count(household):
	if not household or not frappe.db.exists("Household", household):
		return

	member_count = frappe.db.count("Citizen", {"household": household})
	frappe.db.set_value("Household", household, "member_count", member_count, update_modified=False)
