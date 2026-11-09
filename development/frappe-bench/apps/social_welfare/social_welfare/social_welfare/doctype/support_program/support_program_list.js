frappe.listview_settings["Support Program"] = {
    formatters: {
        beneficiary_type: value => frappe.utils.escape_html(wardUI.label(value)),
        target_group: value => frappe.utils.escape_html(wardUI.label(value)),
        screening_status: value => frappe.utils.escape_html(wardUI.label(value)),
        support_type: value => frappe.utils.escape_html(wardUI.label(value)),
    },
};
