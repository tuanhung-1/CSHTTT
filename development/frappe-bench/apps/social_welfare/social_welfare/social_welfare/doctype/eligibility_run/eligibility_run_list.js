frappe.listview_settings["Eligibility Run"] = {
    formatters: {status: value => frappe.utils.escape_html(wardUI.label(value))},
};
