frappe.listview_settings["Support Application"] = {
    formatters: {
        workflow_state(value) { return wardUI.label(value); },
        beneficiary_type(value) { return wardUI.label(value); },
    },
};
