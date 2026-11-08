"""One-time, post-schema conversion of undated legacy classifications."""

import frappe


def execute():
	for household in frappe.get_all("Household", fields=["name", "poverty_status"]):
		if household.poverty_status and not frappe.db.exists(
			"Household Classification", {"household": household.name, "is_legacy": 1}
		):
			doc = frappe.get_doc(
				{
					"doctype": "Household Classification",
					"household": household.name,
					"classification": household.poverty_status,
					"period": "Dữ liệu trước chuyển đổi",
					"basis": "Giá trị poverty_status cũ; chưa có căn cứ về thời gian hiệu lực.",
					"notes": "Cần cán bộ rà soát và tạo kỳ có căn cứ. Không dùng bản này để xét điều kiện hiện tại.",
					"is_legacy": 1,
				}
			)
			previous_flag = frappe.flags.social_welfare_legacy_migration
			frappe.flags.social_welfare_legacy_migration = True
			try:
				doc.insert(ignore_permissions=True)
			finally:
				frappe.flags.social_welfare_legacy_migration = previous_flag
