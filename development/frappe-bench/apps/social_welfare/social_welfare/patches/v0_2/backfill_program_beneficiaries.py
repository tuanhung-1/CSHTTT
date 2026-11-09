"""Keep existing household programs and applications usable after adding citizen support."""

import frappe


def execute():
	frappe.db.sql("UPDATE `tabSupport Program` SET beneficiary_type='Household' WHERE beneficiary_type IS NULL OR beneficiary_type=''")
	frappe.db.sql("UPDATE `tabSupport Program` SET support_type='CASH' WHERE support_type IS NULL OR support_type=''")
	frappe.db.sql("UPDATE `tabSupport Program` SET screening_status='NOT_RUN' WHERE screening_status IS NULL OR screening_status=''")
	frappe.db.sql("UPDATE `tabSupport Application` SET beneficiary_type='Household' WHERE beneficiary_type IS NULL OR beneficiary_type=''")
