frappe.listview_settings["Policy Rule"] = {
    formatters: {
        condition_type: value => frappe.utils.escape_html(wardUI.label(value)),
        operator: value => frappe.utils.escape_html(wardUI.label(value)),
        missing_behavior: value => frappe.utils.escape_html(wardUI.label(value)),
    },
};
