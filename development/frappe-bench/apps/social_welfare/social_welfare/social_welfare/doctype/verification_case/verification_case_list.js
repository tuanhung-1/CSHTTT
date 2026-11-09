frappe.listview_settings["Verification Case"] = {
    formatters: {
        status: value => frappe.utils.escape_html(wardUI.label(value)),
        question_type: value => frappe.utils.escape_html(wardUI.label(value)),
        conclusion: value => frappe.utils.escape_html(wardUI.label(value)),
        beneficiary_type: value => frappe.utils.escape_html(wardUI.label(value)),
    },
};
