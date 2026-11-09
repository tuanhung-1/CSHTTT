frappe.listview_settings["Policy Version"] = {
    formatters: {status: value => frappe.utils.escape_html(wardUI.label(value))},
};
