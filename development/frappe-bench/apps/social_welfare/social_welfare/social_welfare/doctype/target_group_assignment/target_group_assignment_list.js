frappe.listview_settings["Target Group Assignment"] = {
    formatters: {status: value => frappe.utils.escape_html(wardUI.label(value))},
};
