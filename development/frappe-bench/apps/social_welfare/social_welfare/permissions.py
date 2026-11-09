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


def target_group_assignment_query(user=None):
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	if is_admin(user) or roles.intersection({OFFICER, LEADER}):
		return ""
	if VERIFIER not in roles:
		return "1=0"
	quoted_user = frappe.db.escape(user)
	return (
		"(`tabTarget Group Assignment`.household IN "
		f"(SELECT name FROM `tabHousehold` WHERE assigned_verifier={quoted_user}) "
		"OR `tabTarget Group Assignment`.citizen IN "
		"(SELECT c.name FROM `tabCitizen` c JOIN `tabHousehold` h ON h.name=c.household "
		f"WHERE h.assigned_verifier={quoted_user}))"
	)


def eligibility_result_query(user=None):
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	if is_admin(user) or roles.intersection({OFFICER, LEADER, FINANCE}):
		return ""
	if VERIFIER not in roles:
		return "1=0"
	quoted = frappe.db.escape(user)
	return (
		"(`tabEligibility Result`.household IN "
		f"(SELECT name FROM `tabHousehold` WHERE assigned_verifier={quoted}) "
		"OR `tabEligibility Result`.citizen IN "
		"(SELECT c.name FROM `tabCitizen` c JOIN `tabHousehold` h ON h.name=c.household "
		f"WHERE h.assigned_verifier={quoted}))"
	)


def verification_case_query(user=None):
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	if is_admin(user) or roles.intersection({OFFICER, LEADER}):
		return ""
	if VERIFIER in roles:
		return f"`tabVerification Case`.assigned_reviewer={frappe.db.escape(user)}"
	return "1=0"


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
	if doc.doctype == "Eligibility Result" and FINANCE in roles:
		return True
	if doc.doctype == "Verification Case":
		return VERIFIER in roles and doc.get("assigned_reviewer") == user
	if FINANCE in roles and doc.doctype in {"Household", "Support Program", "Support Application"}:
		return True
	if VERIFIER in roles:
		if doc.doctype == "Eligibility Result":
			household = doc.get("household") or frappe.db.get_value("Citizen", doc.get("citizen"), "household")
			return bool(household and frappe.db.get_value("Household", household, "assigned_verifier") == user)
		if doc.doctype == "Support Program":
			return True
		household = doc.name if doc.doctype == "Household" else doc.get("household")
		if doc.doctype == "Target Group Assignment" and doc.get("citizen"):
			household = frappe.db.get_value("Citizen", doc.citizen, "household")
		if household and frappe.db.get_value("Household", household, "assigned_verifier") == user:
			return True
	return False


def prevent_delete(doc, method=None):
	frappe.throw("Không xóa hồ sơ nghiệp vụ. Hãy sử dụng chức năng lưu trữ để giữ lịch sử.")


def boot_session(bootinfo):
	roles = set(frappe.get_roles())
	if not is_admin() and ROLES.intersection(roles):
		bootinfo.home_page = "an-sinh-xa-hoi"
	ward_sidebar = (bootinfo.get("workspace_sidebar_item") or {}).get("social welfare")
	if not ward_sidebar:
		return
	ward_sidebar["label"] = "An sinh xã hội phường"
	if is_admin():
		return
	allowed_by_role = {
		OFFICER: {"an-sinh-xa-hoi", "Household", "Citizen", "Target Group Assignment", "Household Classification", "Support Program", "Eligibility Run", "Eligibility Result", "Verification Case", "Approval Batch", "Policy", "Policy Version", "Policy Rule", "Target Group", "Support Application"},
		VERIFIER: {"an-sinh-xa-hoi", "Household", "Citizen", "Target Group Assignment", "Household Classification", "Verification Case", "Support Application"},
		LEADER: {"an-sinh-xa-hoi", "Support Program", "Eligibility Run", "Eligibility Result", "Verification Case", "Approval Batch", "Policy", "Policy Version", "Policy Rule", "Target Group", "bao-cao-tai-chinh", "Support Application"},
		FINANCE: {"an-sinh-xa-hoi", "Disbursement", "bao-cao-tai-chinh", "Support Application"},
	}
	allowed = set().union(*(links for role, links in allowed_by_role.items() if role in roles))
	filtered, section = [], None
	for item in ward_sidebar["items"]:
		if item["type"] == "Section Break":
			section = item.copy()
			continue
		if item.get("link_to") not in allowed:
			continue
		if section is not None:
			if not filtered or filtered[-1] is not section:
				filtered.append(section)
			section = None
		filtered.append(item)
	ward_sidebar["items"] = filtered
