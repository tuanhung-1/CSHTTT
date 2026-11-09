frappe.listview_settings["Disbursement"] = {
    formatters: {
        beneficiary_type: value => frappe.utils.escape_html(wardUI.label(value)),
        support_type: value => frappe.utils.escape_html(wardUI.label(value)),
        status: value => frappe.utils.escape_html(wardUI.label(value)),
    },
};
