frappe.ui.form.on("Citizen", {
	refresh(frm) {
		if (frm.is_new()) {
			frm.set_intro("Tạo và lưu Hộ gia đình trước, sau đó thêm công dân vào hộ. Nếu đây là công dân đầu tiên và là chủ hộ, chọn quan hệ Chủ hộ.", "blue");
			if (frappe.model.can_create("Household")) {
				frm.add_custom_button("Tạo hộ gia đình trước", () => frappe.new_doc("Household"));
			}
		} else if (frm.doc.household) {
			frm.add_custom_button("Xem hộ gia đình", () => frappe.set_route("Form", "Household", frm.doc.household));
		}
	},
});
