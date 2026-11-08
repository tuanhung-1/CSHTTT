"""Ward roles and assignment-based access, applied to lists and direct reads."""

import frappe

OFFICER = "Social Welfare Officer"
VERIFIER = "Social Welfare Reviewer"  # Retain the existing role ID and users.
LEADER = "Social Welfare Manager"
FINANCE = "Social Welfare Finance"
ROLES = {OFFICER, VERIFIER, LEADER, FINANCE}


def is_admin(user=None):
	return (user or frappe.session.user) == "Administrator"


def assigned_condition(doctype, user=None):
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	if is_admin(user) or roles.intersection({OFFICER, LEADER}):
		return ""
	if FINANCE in roles and doctype in {"Household", "Support Program", "Support Application"}:
		return ""
	if VERIFIER not in roles:
		return "1=0"
	if doctype == "Support Program":
		return ""
	column = "name" if doctype == "Household" else "household"
	return (
		f"`tab{doctype}`.`{column}` IN (SELECT name FROM `tabHousehold` "
		f"WHERE assigned_verifier = {frappe.db.escape(user)})"
	)


def household_query(user=None):
	return assigned_condition("Household", user)


def citizen_query(user=None):
	return assigned_condition("Citizen", user)


def classification_query(user=None):
	return assigned_condition("Household Classification", user)


def application_query(user=None):
	return assigned_condition("Support Application", user)


def document_permission(doc, user=None, ptype=None, **kwargs):
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	if (
		doc.doctype == "Household Classification"
		and ptype == "write"
		and not doc.is_new()
		and not is_admin(user)
	):
		return False  # Write is needed to fill a new form, never to edit saved history.
	if is_admin(user) or roles.intersection({OFFICER, LEADER}):
		return True  # The DocType matrix remains the upper permission bound.
	if FINANCE in roles and doc.doctype in {"Household", "Support Program", "Support Application"}:
		return True
	if VERIFIER in roles:
		if doc.doctype == "Support Program":
			return True
		household = doc.name if doc.doctype == "Household" else doc.get("household")
		if household and frappe.db.get_value("Household", household, "assigned_verifier") == user:
			return True
	return False


def prevent_delete(doc, method=None):
	frappe.throw("Không xóa hồ sơ nghiệp vụ. Hãy sử dụng chức năng lưu trữ để giữ lịch sử.")


def boot_session(bootinfo):
	if not is_admin() and ROLES.intersection(frappe.get_roles()):
		bootinfo.home_page = "an-sinh-xa-hoi"
