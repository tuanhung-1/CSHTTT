frappe.ui.form.on("Eligibility Run", {
    refresh(frm) {
        const e = wardUI.escape;
        const saved = !frm.is_new();
        const officer = frappe.session.user === "Administrator" || frappe.user_roles.includes("Social Welfare Officer");
        const canCreate = saved && frm.doc.status === "COMPLETED" && officer;
        const selected = new Set();
        frm.set_intro("Kết quả của lần rà soát được lưu theo dữ liệu và quy tắc tại ngày chốt. Đối tượng cần xác minh phải bổ sung dữ liệu nguồn rồi rà soát lại.", "blue");
        frm.fields_dict.ward_flow_panel.$wrapper.html(wardUI.journey({
            active: 1, eyebrow: "LẦN RÀ SOÁT", title: saved ? frm.doc.name : "Lần rà soát mới",
            description: frm.doc.status === "COMPLETED" ? "Đã hoàn tất. Đọc lý do, chọn đối tượng đủ điều kiện rồi lập đợt trình." : `Trạng thái: ${wardUI.label(frm.doc.status || "QUEUED")}. Danh sách chỉ dùng để lập đợt khi đã hoàn tất.`,
            meta: [{label: "Chương trình", value: frm.doc.support_program || "Chưa chọn"}, {label: "Ngày chốt", value: frm.doc.cutoff_date || "Chưa chọn"}, {label: "Trạng thái", value: wardUI.label(frm.doc.status || "QUEUED")}],
        }));
        const number = value => Number(value || 0).toLocaleString("vi-VN");
        const $summary = frm.fields_dict.ward_run_summary.$wrapper;
        $summary.html(`<div class="ward-summary-grid">
            ${wardUI.metric("Đã rà soát", number(frm.doc.total_count))}
            ${wardUI.metric("Đủ điều kiện", number(frm.doc.eligible_count), "positive")}
            ${wardUI.metric("Cần xác minh", number(frm.doc.need_verification_count), "warning")}
            ${wardUI.metric("Không đủ điều kiện", number(frm.doc.not_eligible_count), "negative")}
        </div><p class="ward-help-note">Chỉ dòng <strong>Đủ điều kiện</strong> có thể đưa vào đợt trình. Dòng <strong>Cần xác minh</strong> không tự được phê duyệt.</p>
        <div class="ward-related"><div><strong>Điều hướng theo luồng</strong><span>Quay lại chương trình hoặc mở đợt trình của lần rà soát này.</span></div>
        ${frm.doc.support_program ? '<button type="button" class="btn btn-default ward-open-program">Mở chương trình →</button>' : ""}<span class="ward-batch-link"></span></div>`);
        $summary.find(".ward-open-program").on("click", () => frappe.set_route("Form", "Support Program", frm.doc.support_program));
        if (!saved) {
            wardUI.mountActions(frm, []);
            frm.fields_dict.result_preview.$wrapper.empty();
            return;
        }
        wardUI.mountActions(frm, canCreate ? [{
            label: "Lập đợt trình (0 đã chọn)", kind: "primary", disabled: true,
            onClick: async () => {
                if (!selected.size) return frappe.msgprint("Hãy chọn ít nhất một đối tượng đủ điều kiện.");
                const {message: name} = await frappe.call({method: "social_welfare.bulk.create_batch", args: {run_name: frm.doc.name, selected_results: [...selected]}, freeze: true});
                frappe.set_route("Form", "Approval Batch", name);
            },
        }] : [], "Chọn từng đối tượng đủ điều kiện sau khi đã xem lý do.");
        const $preview = frm.fields_dict.result_preview.$wrapper;
        $preview.html('<p class="ward-empty">Đang tải danh sách kết quả…</p>');
        const runName = frm.doc.name;
        frappe.db.get_list("Approval Batch", {fields: ["name", "status"], filters: {eligibility_run: runName}, order_by: "creation desc", limit: 1}).then(batches => {
            if (frm.doc.name !== runName || !batches?.length) return;
            const batch = batches[0];
            const $link = $summary.find(".ward-batch-link");
            $link.html(`<button type="button" class="btn btn-default">Đợt trình ${e(batch.name)} · ${e(wardUI.label(batch.status))} →</button>`);
            $link.find("button").on("click", () => frappe.set_route("Form", "Approval Batch", batch.name));
        });
        frappe.call({method: "social_welfare.eligibility.get_run_results", args: {run_name: runName}}).then(({message: rows}) => {
            if (frm.doc.name !== runName) return;
            rows = rows || [];
            let filter = "ALL";
            let search = "";
            const options = [
                ["ALL", "Tất cả", rows.length],
                ["ELIGIBLE", "Đủ điều kiện", rows.filter(row => row.result_status === "ELIGIBLE").length],
                ["NEED_VERIFICATION", "Cần xác minh", rows.filter(row => row.result_status === "NEED_VERIFICATION").length],
                ["NOT_ELIGIBLE", "Không đủ điều kiện", rows.filter(row => row.result_status === "NOT_ELIGIBLE").length],
            ];
            const updateAction = () => {
                frm.fields_dict.ward_action_panel.$wrapper.find(".ward-inline-actions-buttons .btn")
                    .text(`Lập đợt trình (${selected.size} đã chọn)`).prop("disabled", selected.size === 0);
            };
            const render = () => {
                const shown = rows.filter(row => (filter === "ALL" || row.result_status === filter)
                    && (!search || `${row.citizen || row.household} ${row.reason_summary || ""}`.toLocaleLowerCase("vi").includes(search)));
                $preview.html(`<section class="ward-results"><div class="ward-results-head"><div><h3>Danh sách đã rà soát</h3><p>Chọn bộ lọc để tập trung vào nhóm cần xử lý.</p></div>
                    <label class="ward-search-label">Tìm đối tượng hoặc lý do<input type="search" class="form-control ward-result-search" value="${e(search)}" placeholder="Nhập mã hoặc lý do…"></label></div>
                    <div class="ward-filter-tabs" role="group" aria-label="Lọc kết quả">${options.map(([key, label, count]) => `<button type="button" class="ward-filter-tab ${filter === key ? "is-active" : ""}" data-filter="${e(key)}" aria-pressed="${filter === key}">${e(label)} <strong>${count}</strong></button>`).join("")}</div>
                    ${shown.length ? `<div class="table-responsive"><table class="table ward-results-table"><thead><tr><th>${canCreate ? "Chọn" : ""}</th><th>Đối tượng</th><th>Đánh giá</th><th>Lý do</th><th></th></tr></thead><tbody>
                        ${shown.map(row => `<tr><td>${canCreate && row.result_status === "ELIGIBLE" ? `<input class="ward-result-select" type="checkbox" value="${e(row.name)}" aria-label="Chọn ${e(row.citizen || row.household)}" ${selected.has(row.name) ? "checked" : ""}>` : ""}</td>
                        <td><strong>${e(row.citizen || row.household)}</strong><small>${e(wardUI.label(row.beneficiary_type))}</small></td>
                        <td>${wardUI.status(row.result_status)}</td><td>${e(wardUI.reason(row.reason_summary))}</td>
                        <td><button type="button" class="btn btn-xs btn-default ward-open-result" data-name="${e(row.name)}">Xem lý do →</button></td></tr>`).join("")}
                    </tbody></table></div>` : '<div class="ward-empty ward-results-empty">Không có đối tượng phù hợp với bộ lọc.</div>'}
                    <div class="ward-results-footer">Hiển thị ${shown.length} / ${rows.length} kết quả · ${selected.size} đối tượng đã chọn để lập đợt.</div>
                </section>`);
                $preview.find(".ward-result-search").on("input", function () {
                    search = this.value.toLocaleLowerCase("vi");
                    const start = this.selectionStart;
                    render();
                    const input = $preview.find(".ward-result-search")[0];
                    input.focus();
                    input.setSelectionRange(start, start);
                });
                $preview.find(".ward-filter-tab").on("click", function () { filter = this.dataset.filter; render(); });
                $preview.find(".ward-result-select").on("change", function () {
                    if (this.checked) selected.add(this.value); else selected.delete(this.value);
                    $preview.find(".ward-results-footer").text(`Hiển thị ${shown.length} / ${rows.length} kết quả · ${selected.size} đối tượng đã chọn để lập đợt.`);
                    updateAction();
                });
                $preview.find(".ward-open-result").on("click", function () { frappe.set_route("Form", "Eligibility Result", this.dataset.name); });
            };
            render();
            if (canCreate) updateAction();
        }).catch(() => $preview.html('<p class="ward-empty">Không tải được danh sách kết quả. Hãy làm mới trang.</p>'));
    },
});
