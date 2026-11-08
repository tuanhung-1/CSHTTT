// Copyright (c) 2026, Student Project and contributors
// For license information, please see license.txt

frappe.ui.form.on("Household", {
	setup(frm) {
		frm.set_query("head_citizen", () => ({
			filters: {
				household: frm.doc.name,
			},
		}));
	},
});
