frappe.ui.form.on("Disbursement", {
    refresh(frm) {
        frm.set_intro("Chỉ khoản chi từ đợt đã phê duyệt mới được xác nhận. Đã chi là ghi nhận nghiệp vụ, không tự chuyển tiền.", "blue");
        if (!frm.is_new() && frm.doc.status === "PENDING" && (frappe.session.user === "Administrator" || frappe.user_roles.includes("Social Welfare Finance"))) {
            wardUI.mountActions(frm, [{label: "Xác nhận đã chi", kind: "primary", onClick: () => frappe.prompt([
                {fieldname: "payment_note", fieldtype: "Small Text", label: "Ghi chú xác nhận chi", reqd: 1},
                {fieldname: "receipt_file", fieldtype: "Attach", label: "Tệp biên nhận"},
            ], async values => {
                await frappe.call({method: "social_welfare.bulk.confirm_disbursement", args: {name: frm.doc.name, payment_note: values.payment_note, receipt_file: values.receipt_file}});
                frm.reload_doc();
            }, "Xác nhận chi trả", "Xác nhận")}], "Kiểm tra đối tượng, số tiền và chứng từ trước khi xác nhận.");
        } else {
            wardUI.mountActions(frm, []);
        }
    },
});
