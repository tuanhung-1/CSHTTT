window.wardTargets = {
    render(frm, beneficiaryType) {
        const field = frm.fields_dict.target_group_history;
        if (!field) return;
        if (frm.is_new()) {
            field.$wrapper.html('<p class="text-muted">Lưu hồ sơ trước khi gán nhóm đối tượng.</p>');
            return;
        }
        if (!frappe.model.can_read("Target Group Assignment")) {
            frm.toggle_display("target_group_section", false);
            return;
        }
        const canAssign = frappe.model.can_create("Target Group Assignment");
        frappe.call({method: "social_welfare.api.target_group_history", args: {beneficiary_type: beneficiaryType, name: frm.doc.name}})
            .then(({message: rows}) => {
                const e = frappe.utils.escape_html;
                field.$wrapper.html(`${canAssign ? '<div class="ward-target-actions"><button type="button" class="btn btn-primary ward-request-target">Gửi xác minh nhóm</button><button type="button" class="btn btn-default ward-assign-target">Gán nhóm đã xác minh</button></div>' : ""}${rows.length ? `<div class="table-responsive"><table class="table table-bordered">
                    <thead><tr><th>Nhóm đối tượng</th><th>Hiệu lực</th><th>Xác minh</th><th>Trạng thái</th></tr></thead><tbody>
                    ${rows.map(row => `<tr><td><a href="/desk/target-group-assignment/${encodeURIComponent(row.name)}">${e(row.target_group)}</a></td>
                    <td>${e(frappe.datetime.str_to_user(row.valid_from))} – ${e(frappe.datetime.str_to_user(row.valid_to))}</td>
                    <td>${row.verification_case ? `<a href="/desk/verification-case/${encodeURIComponent(row.verification_case)}">${e(row.verification_case)}</a>` : "Bản ghi cũ"}</td>
                    <td>${row.status === "VOID" ? `Đã hủy: ${e(row.void_reason || "")}` : "Đang ghi nhận"}</td></tr>`).join("")}
                    </tbody></table></div>` : '<p class="text-muted">Chưa có nhóm đối tượng chính sách.</p>'}`);
                field.$wrapper.find(".ward-assign-target").on("click", () => frappe.new_doc("Target Group Assignment", {
                    [beneficiaryType === "Citizen" ? "citizen" : "household"]: frm.doc.name,
                }));
                field.$wrapper.find(".ward-request-target").on("click", () => {
                    const dialog = new frappe.ui.Dialog({title: "Yêu cầu xác minh nhóm đối tượng", fields: [
                        {fieldname: "target_group", label: "Nhóm cần xác minh", fieldtype: "Link", options: "Target Group", reqd: 1},
                        {fieldname: "request_note", label: "Lý do và nội dung cần đối chiếu", fieldtype: "Small Text", reqd: 1},
                    ], primary_action_label: "Gửi cho người xác minh", primary_action: async values => {
                        const {message: name} = await frappe.call({method: "social_welfare.verification.create_verification_request",
                            args: {beneficiary_type: beneficiaryType, beneficiary: frm.doc.name, question_type: "TARGET_GROUP", ...values}, freeze: true});
                        dialog.hide();
                        frappe.set_route("Form", "Verification Case", name);
                    }});
                    dialog.show();
                });
            });
    },
};
