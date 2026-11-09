(() => {
    const labels = {
        Household: "Hộ gia đình", Citizen: "Công dân", Both: "Hộ và công dân", CASH: "Hỗ trợ tiền", IN_KIND: "Hỗ trợ hiện vật",
        CLASSIFICATION: "Phân loại hộ", TARGET_GROUP: "Nhóm đối tượng", RESIDENCY: "Địa bàn cư trú", DUPLICATE: "Khoản hỗ trợ trước đó", OTHER: "Thông tin khác",
        EQ: "Bằng", IN: "Thuộc một trong", EXISTS: "Có dữ liệu", NOT_EXISTS: "Không có dữ liệu",
        NEED_VERIFICATION: "Cần xác minh", FAIL: "Không đạt", PASS: "Đạt", UNKNOWN: "Thiếu dữ liệu",
        ELIGIBLE: "Đủ điều kiện", NOT_ELIGIBLE: "Không đủ điều kiện",
        DRAFT: "Bản nháp", ACTIVE: "Đang hiệu lực", EXPIRED: "Hết hiệu lực", VOID: "Đã hủy hiệu lực",
        NOT_RUN: "Chưa rà soát", QUEUED: "Đang chờ rà soát", RUNNING: "Đang rà soát", COMPLETED: "Đã hoàn tất",
        SUBMITTED: "Đã trình lãnh đạo", APPROVED: "Đã phê duyệt", REJECTED: "Đã từ chối", RETURNED: "Yêu cầu bổ sung",
        SELECTED: "Được chọn", REMOVED: "Đã loại khỏi đợt", PENDING: "Chờ chi", PAID: "Đã chi", FAILED: "Thất bại", CANCELLED: "Đã hủy",
        AWAITING_REVIEW: "Chờ xác minh", CONFIRMED: "Đã xác nhận", NOT_CONFIRMED: "Không xác nhận", INSUFFICIENT: "Chưa đủ căn cứ",
        Draft: "Nháp", Submitted: "Đã tiếp nhận", Reviewing: "Đang xác minh", "Pending Approval": "Chờ lãnh đạo duyệt",
        Returned: "Yêu cầu bổ sung", Approved: "Đã phê duyệt", Rejected: "Đã từ chối", Paid: "Đã xác nhận chi",
        poor: "Hộ nghèo", near_poor: "Hộ cận nghèo", disaster: "Ảnh hưởng thiên tai", policy: "Diện chính sách", other: "Khác",
        "Poor Household": "Hộ nghèo", "Near-poor Household": "Hộ cận nghèo", EXISTING: "Đã có khoản hỗ trợ",
    };
    const fieldsByDoctype = {
        "Policy": ["policy_type"],
        "Policy Version": ["status"],
        "Policy Rule": ["condition_type", "operator", "missing_behavior"],
        "Support Program": ["beneficiary_type", "target_group", "support_type", "screening_status"],
        "Target Group Assignment": ["status"],
        "Verification Case": ["status", "beneficiary_type", "question_type", "conclusion"],
        "Eligibility Run": ["status"],
        "Eligibility Result": ["beneficiary_type", "result_status"],
        "Approval Batch": ["status"],
        "Disbursement": ["beneficiary_type", "support_type", "status"],
        "Support Application": ["beneficiary_type"],
    };
    const label = value => labels[value] || value || "";
    const reason = value => String(value || "").replace(/\b(PASS|FAIL|UNKNOWN)\b/g, code => label(code));
    const escape = value => frappe.utils.escape_html(String(value == null ? "" : value));
    const displayValue = value => String(value || "").split(",").map(part => label(part.trim())).join(", ") || "Chưa có dữ liệu";
    const steps = ["Cấu hình", "Rà soát", "Lập đợt trình", "Lãnh đạo duyệt", "Chi trả"];

    function journey({active, eyebrow, title, description, meta = []}) {
        return `<section class="ward-journey" aria-label="Tiến độ xử lý">
            <div class="ward-journey-head"><div><span class="ward-journey-eyebrow">${escape(eyebrow)}</span><h2>${escape(title)}</h2><p>${escape(description)}</p></div>
            <span class="ward-journey-stage">Bước ${Math.min(active + 1, steps.length)} / ${steps.length}</span></div>
            <ol class="ward-journey-steps">${steps.map((step, index) => `<li class="${index < active ? "is-done" : index === active ? "is-current" : "is-future"}" ${index === active ? 'aria-current="step"' : ""}><span class="ward-journey-number">${index < active ? "✓" : index + 1}</span><span>${step}</span></li>`).join("")}</ol>
            ${meta.length ? `<div class="ward-journey-meta">${meta.map(item => `<span><strong>${escape(item.label)}</strong> ${escape(item.value)}</span>`).join("")}</div>` : ""}
        </section>`;
    }

    function metric(labelText, value, tone = "neutral") {
        return `<div class="ward-metric ward-tone-${tone}"><span>${escape(labelText)}</span><strong>${escape(value)}</strong></div>`;
    }

    function status(value) {
        const tone = {ELIGIBLE: "positive", APPROVED: "positive", PAID: "positive", PASS: "positive", NOT_ELIGIBLE: "negative", REJECTED: "negative", FAIL: "negative", NEED_VERIFICATION: "warning", UNKNOWN: "warning", RETURNED: "warning"}[value] || "neutral";
        return `<span class="ward-status ward-tone-${tone}">${escape(label(value))}</span>`;
    }

    function localizeForm(frm) {
        for (const fieldname of fieldsByDoctype[frm.doctype] || []) {
            const control = frm.fields_dict[fieldname];
            if (!control || control.df.fieldtype !== "Select") continue;
            if (!control._wardOriginalOptions) {
                control._wardOriginalOptions = typeof control.df.options === "string"
                    ? control.df.options.split("\n")
                    : (control.df.options || []).map(option => typeof option === "string" ? option : option.value);
            }
            control.df.options = control._wardOriginalOptions.map(value => ({value, label: label(value)}));
            control.refresh();
        }
    }

    function mountActions(frm, actions, description) {
        const field = frm.fields_dict.ward_action_panel;
        if (!field) return;
        frm.toggle_display("ward_action_panel", Boolean(actions.length));
        if (!actions.length) return;
        const e = frappe.utils.escape_html;
        field.$wrapper.html(`<div class="ward-inline-actions"><div class="ward-inline-actions-copy"><strong>Thao tác tiếp theo</strong>${description ? `<span>${e(description)}</span>` : ""}</div><div class="ward-inline-actions-buttons"></div></div>`);
        const $buttons = field.$wrapper.find(".ward-inline-actions-buttons");
        for (const action of actions) {
            const $button = $('<button type="button"></button>')
                .addClass(`btn ${action.kind === "primary" ? "btn-primary" : action.kind === "danger" ? "btn-danger" : "btn-default"}`)
                .text(action.label).prop("disabled", Boolean(action.disabled))
                .appendTo($buttons);
            $button.on("click", async () => {
                $button.prop("disabled", true);
                try { await action.onClick(); } finally { $button.prop("disabled", Boolean(action.disabled)); }
            });
        }
    }

    window.wardUI = {label, reason, displayValue, escape, journey, metric, status, localizeForm, mountActions};
    $(document).on("form-refresh.ward-ui", (_event, frm) => {
        if (frm) localizeForm(frm);
    });
})();
