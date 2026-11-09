function render_ward_batch_summary(frm) {
    const items = frm.doc.items || [];
    const chosen = items.filter(item => item.selection_status === "SELECTED");
    const removed = items.filter(item => item.selection_status === "REMOVED");
    const amount = chosen.reduce((sum, item) => sum + Number(item.proposed_amount || 0), 0);
    const active = {DRAFT: 2, RETURNED: 2, SUBMITTED: 3, APPROVED: 4, REJECTED: 3}[frm.doc.status] ?? 2;
    const descriptions = {
        DRAFT: "Kiểm tra danh sách và kinh phí. Lưu thay đổi rồi trình lãnh đạo.",
        RETURNED: "Lãnh đạo yêu cầu bổ sung. Đọc ý kiến, đưa về nháp, sửa và trình lại.",
        SUBMITTED: "Danh sách đã khóa để lãnh đạo xem và quyết định cả đợt.",
        APPROVED: "Đợt đã được phê duyệt. Các khoản chi đang chờ cán bộ tài chính xác nhận.",
        REJECTED: "Đợt đã bị từ chối. Xem ý kiến quyết định bên dưới.",
    };
    frm.fields_dict.ward_flow_panel.$wrapper.html(wardUI.journey({
        active, eyebrow: "ĐỢT TRÌNH DUYỆT", title: frm.is_new() ? "Đợt trình mới" : frm.doc.name,
        description: descriptions[frm.doc.status] || "Kiểm tra thông tin của đợt trình.",
        meta: [{label: "Chương trình", value: frm.doc.support_program || "Chưa chọn"}, {label: "Lần rà soát", value: frm.doc.eligibility_run || "Chưa chọn"}, {label: "Trạng thái", value: wardUI.label(frm.doc.status || "DRAFT")}],
    }));
    const note = frm.doc.decision_note ? `<div class="ward-decision-note"><strong>Ý kiến của lãnh đạo</strong><p>${wardUI.escape(frm.doc.decision_note)}</p></div>` : "";
    const incomplete = removed.filter(item => !item.change_reason).length;
    frm.fields_dict.ward_batch_summary.$wrapper.html(`<div class="ward-summary-grid ward-summary-grid-three">
        ${wardUI.metric("Đối tượng đề xuất", chosen.length, "positive")}
        ${wardUI.metric("Đã loại khỏi đợt", removed.length, "warning")}
        ${wardUI.metric("Tổng tiền đề xuất", `${amount.toLocaleString("vi-VN")} ₫`)}
    </div>${note}
    ${incomplete ? `<p class="ward-help-note ward-help-warning">${incomplete} dòng đã loại chưa có lý do thay đổi. Hãy bổ sung trước khi lưu.</p>` : ""}
    <p class="ward-help-note">Số liệu trên tính từ các dòng đang hiển thị; lưu đợt trước khi trình. Bấm mã <strong>Kết quả rà soát</strong> trong bảng để xem căn cứ từng đối tượng.</p>
    <div class="ward-related"><div><strong>Căn cứ của đợt trình</strong><span>Mở lần rà soát để xem toàn bộ đối tượng và lý do xét.</span></div>
        ${frm.doc.eligibility_run ? '<button type="button" class="btn btn-default ward-open-source-run">Xem lần rà soát →</button>' : ""}</div>`);
    frm.fields_dict.ward_batch_summary.$wrapper.find(".ward-open-source-run").on("click", () => frappe.set_route("Form", "Eligibility Run", frm.doc.eligibility_run));
}

frappe.ui.form.on("Approval Batch", {
    refresh(frm) {
        frm.fields_dict.items?.grid.update_docfield_property("selection_status", "options", [
            {value: "SELECTED", label: "Được chọn"},
            {value: "REMOVED", label: "Đã loại khỏi đợt"},
        ]);
        render_ward_batch_summary(frm);
        if (frm.is_new()) {
            wardUI.mountActions(frm, []);
            return;
        }
        const officer = frappe.session.user === "Administrator" || frappe.user_roles.includes("Social Welfare Officer");
        const leader = frappe.session.user === "Administrator" || frappe.user_roles.includes("Social Welfare Manager");
        frm.set_intro({DRAFT: "Cán bộ kiểm tra từng dòng, chỉnh mức hỗ trợ hoặc loại dòng có lý do, lưu rồi trình lãnh đạo.", SUBMITTED: "Đợt đã trình; lãnh đạo quyết định cả danh sách.", APPROVED: "Đợt đã duyệt; các khoản chi đang chờ tài chính xác nhận.", RETURNED: "Đợt bị trả lại; đưa về bản nháp để bổ sung.", REJECTED: "Đợt đã bị từ chối."}[frm.doc.status] || "", "blue");
        const actions = [];
        if (frm.doc.status === "DRAFT" && officer) actions.push({
            label: "Trình lãnh đạo", kind: "primary", onClick: async () => {
                if (frm.is_dirty()) return frappe.msgprint("Hãy lưu các thay đổi trong danh sách trước khi trình.");
                await frappe.call({method: "social_welfare.bulk.submit_batch", args: {name: frm.doc.name}});
                frm.reload_doc();
            },
        });
        if (frm.doc.status === "RETURNED" && officer) actions.push({
            label: "Đưa về bản nháp", kind: "primary", onClick: async () => {
                await frappe.call({method: "social_welfare.bulk.reset_batch", args: {name: frm.doc.name}});
                frm.reload_doc();
            },
        });
        if (frm.doc.status === "SUBMITTED" && leader) {
            for (const [label, decision, kind] of [["Phê duyệt đợt", "APPROVED", "primary"], ["Yêu cầu bổ sung", "RETURNED", "secondary"], ["Từ chối đợt", "REJECTED", "danger"]]) {
                actions.push({label, kind, onClick: () => frappe.prompt({fieldname: "note", fieldtype: "Small Text", label: "Ý kiến quyết định", reqd: 1}, async values => {
                    await frappe.call({method: "social_welfare.bulk.decide_batch", args: {name: frm.doc.name, decision, note: values.note}});
                    frm.reload_doc();
                }, label, "Xác nhận")});
            }
        }
        wardUI.mountActions(frm, actions, {
            DRAFT: "Kiểm tra danh sách và lưu mọi thay đổi trước khi trình.",
            SUBMITTED: "Đọc danh sách và ý kiến trước khi quyết định.",
            RETURNED: "Đưa về nháp để bổ sung danh sách và trình lại.",
        }[frm.doc.status]);
    },
    items_add(frm) { render_ward_batch_summary(frm); },
    items_remove(frm) { render_ward_batch_summary(frm); },
});

frappe.ui.form.on("Approval Batch Item", {
    selection_status(frm) { render_ward_batch_summary(frm); },
    proposed_amount(frm) { render_ward_batch_summary(frm); },
    change_reason(frm) { render_ward_batch_summary(frm); },
});
