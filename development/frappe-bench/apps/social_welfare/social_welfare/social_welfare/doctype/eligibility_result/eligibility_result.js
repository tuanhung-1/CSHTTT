frappe.ui.form.on("Eligibility Result", {
    refresh(frm) {
        if (frm.is_new()) {
            wardUI.mountActions(frm, []);
            return;
        }
        const e = wardUI.escape;
        const details = frm.doc.rule_details || [];
        const result = frm.doc.result_status;
        const subject = frm.doc.citizen || frm.doc.household || frm.doc.name;
        const next = {
            ELIGIBLE: "Đối tượng đạt các điều kiện bắt buộc. Cán bộ có thể chọn kết quả này khi lập đợt trình; lãnh đạo vẫn quyết định ở bước sau.",
            NEED_VERIFICATION: "Dữ liệu còn thiếu hoặc cần xác minh. Kiểm tra hồ sơ gốc, bổ sung thông tin có căn cứ rồi chạy rà soát mới. Kết quả lần này được giữ nguyên.",
            NOT_ELIGIBLE: "Có ít nhất một điều kiện bắt buộc không đạt. Xem từng dòng bên dưới để biết dữ liệu nào không phù hợp.",
        };
        frm.fields_dict.ward_flow_panel.$wrapper.html(wardUI.journey({
            active: 1, eyebrow: "KẾT QUẢ RÀ SOÁT", title: subject,
            description: next[result] || "Xem dữ liệu và điều kiện đã dùng để đánh giá.",
            meta: [{label: "Kết quả", value: wardUI.label(result)}, {label: "Loại đối tượng", value: wardUI.label(frm.doc.beneficiary_type)}, {label: "Lần rà soát", value: frm.doc.eligibility_run}],
        }));
        frm.fields_dict.ward_result_details.$wrapper.html(`<section class="ward-result-explanation">
            <div class="ward-result-head"><div><span class="ward-journey-eyebrow">KẾT LUẬN CHO ĐỐI TƯỢNG</span><h3>${e(subject)}</h3></div>${wardUI.status(result)}</div>
            <p class="ward-result-reason">${e(wardUI.reason(frm.doc.reason_summary || "Chưa có lý do tóm tắt."))}</p>
            <div class="ward-result-hint">${e(next[result] || "")}</div>
            <div class="ward-result-table-title"><div><h4>Điều kiện đã xét</h4><p>Đối chiếu dữ liệu ghi nhận với yêu cầu của từng điều kiện tại thời điểm rà soát.</p></div><span>${details.length} điều kiện</span></div>
            ${details.length ? `<div class="table-responsive"><table class="table ward-results-table"><thead><tr><th>Điều kiện</th><th>Dữ liệu ghi nhận</th><th>Yêu cầu</th><th>Kết quả</th><th>Giải thích</th></tr></thead><tbody>
                ${details.map(row => `<tr><td><strong>${e(row.rule_name)}</strong></td><td>${e(wardUI.displayValue(row.actual_value))}</td><td>${e(row.expected_value ? wardUI.displayValue(row.expected_value) : "Không yêu cầu giá trị")}</td><td>${wardUI.status(row.evaluation)}</td><td>${e(row.reason || "")}</td></tr>`).join("")}
            </tbody></table></div>` : '<p class="ward-empty">Không có điều kiện chi tiết được lưu cho kết quả này.</p>'}
            ${frappe.model.can_read("Eligibility Run") ? `<div class="ward-related"><div><strong>Xem toàn bộ lần rà soát</strong><span>Đối chiếu với các đối tượng khác trong cùng lần.</span></div><button type="button" class="btn btn-default ward-back-run">Mở ${e(frm.doc.eligibility_run)} →</button></div>` : ""}
        </section>`);
        frm.fields_dict.ward_result_details.$wrapper.find(".ward-back-run").on("click", () => frappe.set_route("Form", "Eligibility Run", frm.doc.eligibility_run));
        const officer = frappe.session.user === "Administrator" || frappe.user_roles.includes("Social Welfare Officer");
        wardUI.mountActions(frm, officer && result === "NEED_VERIFICATION" ? [{
            label: "Gửi yêu cầu xác minh", kind: "primary", onClick: () => {
                const dialog = new frappe.ui.Dialog({title: "Yêu cầu xác minh dữ liệu", fields: [
                    {fieldname: "question_type", label: "Nội dung cần xác minh", fieldtype: "Select", reqd: 1,
                        options: [{value: "TARGET_GROUP", label: "Nhóm đối tượng"}, {value: "RESIDENCY", label: "Địa bàn cư trú"},
                            {value: "CLASSIFICATION", label: "Phân loại hộ"}, {value: "OTHER", label: "Thông tin khác"}]},
                    {fieldname: "target_group", label: "Nhóm đối tượng (nếu xác minh nhóm)", fieldtype: "Link", options: "Target Group"},
                    {fieldname: "request_note", label: "Vấn đề cần đối chiếu", fieldtype: "Small Text", reqd: 1},
                ], primary_action_label: "Gửi cho người xác minh", primary_action: async values => {
                    const {message: name} = await frappe.call({method: "social_welfare.verification.create_verification_request",
                        args: {eligibility_result: frm.doc.name, ...values}, freeze: true});
                    dialog.hide();
                    frappe.set_route("Form", "Verification Case", name);
                }});
                dialog.show();
            },
        }] : [], "Hộ cần được giao cho Người xác minh trước khi gửi yêu cầu; kết quả cũ được giữ nguyên.");
        const $history = frm.fields_dict.ward_verification_history.$wrapper;
        const resultName = frm.doc.name;
        $history.html('<p class="ward-help-note">Đang tải hồ sơ xác minh…</p>');
        frappe.db.get_list("Verification Case", {fields: ["name", "status", "question_type", "target_group", "conclusion", "assigned_reviewer"],
            filters: {eligibility_result: resultName}, order_by: "creation desc", limit: 100}).then(cases => {
            if (frm.doc.name !== resultName) return;
            $history.html(`<section class="ward-verification-history"><h4>Hồ sơ xác minh liên quan</h4>
                ${cases?.length ? `<div class="table-responsive"><table class="table ward-results-table"><thead><tr><th>Hồ sơ</th><th>Nội dung</th><th>Người xác minh</th><th>Trạng thái</th><th>Kết luận</th></tr></thead><tbody>
                ${cases.map(item => `<tr><td><button type="button" class="btn btn-xs btn-default ward-open-case" data-name="${e(item.name)}">${e(item.name)} →</button></td>
                    <td>${e(wardUI.label(item.question_type))}${item.target_group ? ` · ${e(item.target_group)}` : ""}</td><td>${e(item.assigned_reviewer)}</td>
                    <td>${wardUI.status(item.status)}</td><td>${item.conclusion ? wardUI.status(item.conclusion) : "—"}</td></tr>`).join("")}</tbody></table></div>`
                    : '<p class="ward-help-note">Chưa có hồ sơ xác minh cho kết quả này.</p>'}</section>`);
            $history.find(".ward-open-case").on("click", function () { frappe.set_route("Form", "Verification Case", this.dataset.name); });
        });
    },
});
