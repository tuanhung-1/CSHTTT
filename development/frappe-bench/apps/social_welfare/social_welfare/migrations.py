"""Install/migrate hooks for source-controlled application configuration."""

import json
from pathlib import Path

import frappe


def before_migrate():
	# New sites need these roles before DocType permissions and workflow sync.
	roles = json.loads(Path(frappe.get_app_path("social_welfare", "fixtures", "role.json")).read_text())
	for role in roles:
		if not frappe.db.exists("Role", role["role_name"]):
			frappe.get_doc(role).insert(ignore_permissions=True)


def after_migrate():
	# Reset only this app's DocPerm rows, so existing sites receive the new matrix.
	from frappe.permissions import reset_perms

	for doctype in (
		"Household",
		"Citizen",
		"Support Program",
		"Support Application",
		"Household Classification",
		"Target Group",
		"Target Group Assignment",
		"Policy",
		"Policy Version",
		"Policy Rule",
		"Eligibility Run",
		"Eligibility Result",
		"Verification Case",
		"Approval Batch",
		"Disbursement",
	):
		reset_perms(doctype)
	frappe.clear_cache()


def after_install():
	# Frappe marks patches complete on first install rather than executing them.
	from social_welfare.patches.v0_1.migrate_legacy_classifications import execute
	from social_welfare.patches.v0_2.backfill_program_beneficiaries import execute as backfill_beneficiaries

	execute()
	backfill_beneficiaries()
	after_migrate()
