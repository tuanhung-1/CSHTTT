frappe.ui.form.on("Target Group Assignment", {
    refresh(frm) {
        frm.set_intro("Bản gán nhóm mới cần hồ sơ xác minh đã kết luận. Chọn hồ sơ để hệ thống điền nhóm và khoảng hiệu lực đã xác nhận; bản đã lưu được giữ làm lịch sử.", "blue");
        if (frm.is_new()) return;
        frm.disable_form();
        if (frm.doc.status === "ACTIVE" && (frappe.session.user === "Administrator" || frappe.user_roles.includes("Social Welfare Manager"))) {
            frm.add_custom_button("Hủy hiệu lực", () => frappe.prompt({fieldname: "reason", fieldtype: "Small Text", label: "Lý do hủy", reqd: 1}, async values => {
                await frappe.call({method: "social_welfare.api.void_target_group_assignment", args: {name: frm.doc.name, reason: values.reason}});
                frm.reload_doc();
            }, "Hủy hiệu lực nhóm đối tượng", "Xác nhận"));
        }
    },
    setup(frm) {
        frm.set_query("verification_case", () => {
            const filters = {question_type: "TARGET_GROUP", status: "COMPLETED", conclusion: "CONFIRMED"};
            if (frm.doc.citizen) filters.citizen = frm.doc.citizen;
            if (frm.doc.household) filters.household = frm.doc.household;
            if (frm.doc.target_group) filters.target_group = frm.doc.target_group;
            return {filters};
        });
    },
    verification_case(frm) {
        if (!frm.is_new() || !frm.doc.verification_case) return;
        frappe.db.get_value("Verification Case", frm.doc.verification_case,
            ["target_group", "verified_from", "verified_to", "household", "citizen"]).then(({message: row}) => {
            if (!row || (row.citizen || null) !== (frm.doc.citizen || null) || (row.household || null) !== (frm.doc.household || null)) return;
            frm.set_value({target_group: row.target_group, valid_from: row.verified_from, valid_to: row.verified_to});
        });
    },
});
