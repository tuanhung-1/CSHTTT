frappe.listview_settings["Eligibility Result"] = {
    formatters: {
        beneficiary_type: value => frappe.utils.escape_html(wardUI.label(value)),
        result_status: value => frappe.utils.escape_html(wardUI.label(value)),
        reason_summary: value => frappe.utils.escape_html(wardUI.reason(value)),
    },
};
