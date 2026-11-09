frappe.ui.form.on("Support Program", {
    refresh(frm) {
        const individual = frm.doc.beneficiary_type === "Citizen";
        frm.toggle_display("target_group_ref", individual);
        frm.toggle_display("target_group", !individual);
        const officer = frappe.session.user === "Administrator" || frappe.user_roles.includes("Social Welfare Officer");
        const ready = !frm.is_new() && Boolean(frm.doc.policy_version) && frm.doc.active && !frm.doc.is_archived;
        const audience = wardUI.label(frm.doc.beneficiary_type || "Household");
        const target = individual ? frm.doc.target_group_ref : wardUI.label(frm.doc.target_group);
        const note = ready
            ? `Chương trình dành cho ${audience.toLowerCase()}. Mỗi lần rà soát sử dụng dữ liệu tại ngày chốt và giữ lại kết quả để đối chiếu.`
            : "Hoàn thiện đối tượng, phiên bản chính sách đang hiệu lực và trạng thái triển khai trước khi rà soát.";
        frm.set_intro(note, "blue");
        const flow = frm.fields_dict.ward_flow_panel.$wrapper;
        const e = wardUI.escape;
        const render = (run, batch) => {
            const active = batch ? ({DRAFT: 2, RETURNED: 2, SUBMITTED: 3, APPROVED: 4, REJECTED: 3}[batch.status] ?? 2) : run ? 1 : 0;
            const description = batch
                ? `Lần rà soát mới nhất đã có đợt trình ${wardUI.label(batch.status).toLowerCase()}.`
                : run ? `Lần rà soát mới nhất ${wardUI.label(run.status).toLowerCase()}. Xem kết quả trước khi lập đợt trình.`
                    : "Chưa có lần rà soát nào. Cấu hình chương trình rồi chạy rà soát hàng loạt.";
            flow.html(wardUI.journey({active, eyebrow: "CHƯƠNG TRÌNH HỖ TRỢ", title: frm.doc.program_name || "Chương trình mới", description,
                meta: [
                    {label: "Đối tượng", value: audience},
                    {label: "Nhóm áp dụng", value: target || "Theo quy tắc chính sách"},
                    {label: "Ngày chốt", value: frm.doc.cutoff_date || "Chưa chọn"},
                ]}) + `<div class="ward-related">
                <div><strong>Hồ sơ liên quan</strong><span>Đi theo thứ tự từ lần rà soát đến quyết định.</span></div>
                ${run ? `<button type="button" class="btn btn-default ward-open-run">Lần rà soát mới nhất · ${e(run.name)} →</button>` : '<span class="ward-related-empty">Chưa có lần rà soát</span>'}
                ${batch ? `<button type="button" class="btn btn-default ward-open-batch">Đợt trình · ${e(batch.name)} →</button>` : ""}
            </div>`);
            flow.find(".ward-open-run").on("click", () => frappe.set_route("Form", "Eligibility Run", run.name));
            flow.find(".ward-open-batch").on("click", () => frappe.set_route("Form", "Approval Batch", batch.name));
        };
        render(null, null);
        if (!frm.is_new()) {
            const programName = frm.doc.name;
            frappe.db.get_list("Eligibility Run", {fields: ["name", "status"], filters: {support_program: programName}, order_by: "creation desc", limit: 1})
                .then(async runs => {
                    if (frm.doc.name !== programName || !runs?.length) return;
                    const batches = await frappe.db.get_list("Approval Batch", {fields: ["name", "status"], filters: {eligibility_run: runs[0].name}, order_by: "creation desc", limit: 1});
                    if (frm.doc.name === programName) render(runs[0], batches?.[0]);
                })
                .catch(() => { if (frm.doc.name === programName) render(null, null); });
        }
        wardUI.mountActions(frm, officer && !frm.is_new() ? [{
            label: "Chạy rà soát hàng loạt", kind: "primary", disabled: !ready,
            onClick: () => frappe.confirm("Chạy rà soát và lưu một lần kết quả mới cho chương trình này?", async () => {
                if (frm.is_dirty()) return frappe.msgprint("Hãy lưu chương trình trước khi rà soát.");
                const {message: name} = await frappe.call({method: "social_welfare.eligibility.screen_program", args: {program_name: frm.doc.name}, freeze: true, freeze_message: "Đang rà soát đối tượng…"});
                frappe.set_route("Form", "Eligibility Run", name);
            }),
        }] : [], ready ? "Tạo một lần rà soát mới; lịch sử cũ được giữ nguyên." : "Cần lưu chương trình đang triển khai và chọn phiên bản chính sách.");
    },
    beneficiary_type(frm) {
        frm.set_value("target_group_ref", null);
        frm.set_value("target_group", null);
        frm.trigger("refresh");
    },
});
