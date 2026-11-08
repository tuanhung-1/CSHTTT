import frappe

__version__ = "0.0.1"


def has_app_permission():
	if frappe.session.user == "Administrator":
		return True

	allowed_roles = {
		"Social Welfare Officer",
		"Social Welfare Reviewer",
		"Social Welfare Manager",
	}
	return bool(allowed_roles.intersection(frappe.get_roles()))
