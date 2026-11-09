frappe.listview_settings["Approval Batch"] = {
    formatters: {status: value => frappe.utils.escape_html(wardUI.label(value))},
};
