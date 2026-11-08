frappe.pages["an-sinh-xa-hoi"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({ parent: wrapper, title: "An sinh xã hội phường", single_column: true });
    const escape = frappe.utils.escape_html;
    const stateLabels = { Draft: "Nháp", Submitted: "Đã tiếp nhận", Reviewing: "Đang xác minh", "Pending Approval": "Chờ lãnh đạo duyệt", Returned: "Yêu cầu bổ sung", Approved: "Đã phê duyệt", Rejected: "Từ chối", Paid: "Đã xác nhận chi" };
    const roleLabels = { "Social Welfare Officer": "Cán bộ an sinh", "Social Welfare Reviewer": "Người xác minh", "Social Welfare Manager": "Lãnh đạo phường", "Social Welfare Finance": "Cán bộ tài chính" };
    const root = $('<div class="ward-app" aria-live="polite"></div>').appendTo(page.main);
    page.add_inner_button("Làm mới", () => wrapper.load_ward_dashboard());
    wrapper.load_ward_dashboard = async () => {
        root.html('<div class="ward-empty">Đang tải công việc của bạn…</div>');
        try {
            const { message: data } = await frappe.call("social_welfare.api.dashboard");
            root.html(`
                <section class="ward-hero">
                    <div><div class="ward-eyebrow">QUẢN LÝ AN SINH CẤP PHƯỜNG</div>
                    <h1>Trung tâm an sinh xã hội</h1>
                    <p>Tra cứu hộ gia đình, theo dõi phân loại theo thời kỳ và xử lý hồ sơ theo nhiệm vụ.</p>
                    <div class="ward-role-list">${frappe.session.user === "Administrator" ? '<span>Quản trị hệ thống</span>' : data.roles.filter(role => roleLabels[role]).map(role => `<span>${escape(roleLabels[role])}</span>`).join("")}</div></div>
                    <div class="ward-hero-mark" aria-hidden="true">AS<br><small>AN SINH XÃ HỘI</small></div>
                </section>
                <section class="ward-cards" aria-label="Các phân hệ">${data.cards.map((card, index) => `
                    <button class="ward-card" data-doctype="${escape(card.doctype)}">
                        <span class="ward-card-index">0${index + 1}</span><strong>${Number(card.count).toLocaleString("vi-VN")}</strong>
                        <span class="ward-card-label">${escape(card.label)}</span><span class="ward-card-link">Xem danh sách →</span>
                    </button>`).join("")}</section>
                <div class="ward-body"><section class="ward-work"><div class="ward-section-title"><h2>Công việc cần xử lý</h2><span>Theo vai trò của bạn</span></div>
                    ${data.tasks.map(task => `<article class="ward-task"><div class="ward-task-heading"><h3>${escape(task.title)}</h3><button class="btn btn-sm btn-default ward-all" data-states="${escape(JSON.stringify(task.states))}">Xem tất cả →</button></div>
                    ${task.items.length ? `<div class="ward-task-list">${task.items.map(item => `<button class="ward-task-row" data-application="${escape(item.name)}"><div><strong>${escape(item.name)}</strong><small>${escape(item.household)} · ${escape(item.program)}</small></div><span class="ward-state">${escape(stateLabels[item.workflow_state] || item.workflow_state)}</span></button>`).join("")}</div>` : '<p class="ward-empty">Chưa có hồ sơ cần xử lý ở bước này.</p>'}</article>`).join("") || '<p class="ward-empty">Vai trò hiện tại chưa có hàng đợi xử lý.</p>'}
                </section><aside class="ward-side"><h2>Thao tác nhanh</h2>
                    ${data.can_create ? '<button class="btn btn-primary btn-block ward-new-household">+ Tiếp nhận hộ gia đình</button><button class="btn btn-default btn-block ward-new-application">+ Lập hồ sơ hỗ trợ</button>' : '<p>Chọn công việc được giao để mở hồ sơ và thực hiện bước xử lý.</p>'}
                    <div class="ward-guidance"><h3>Lưu lịch sử có căn cứ</h3><p>Mỗi kỳ phân loại được lưu riêng, có khoảng hiệu lực và căn cứ. Dữ liệu cũ chưa rõ thời gian cần được rà soát trước khi sử dụng.</p></div>
                    <div class="ward-guidance"><h3>Đúng người, đúng bước</h3><p>Tiếp nhận → Xác minh → Lãnh đạo phê duyệt → Tài chính xác nhận chi.</p><small>Xác nhận chi hiện là ghi nhận trạng thái, chưa thay thế chứng từ và đối soát.</small></div>
                </aside></div>`);
            root.find("[data-doctype]").on("click", function () { frappe.set_route("List", this.dataset.doctype); });
            root.find("[data-application]").on("click", function () { frappe.set_route("Form", "Support Application", this.dataset.application); });
            root.find(".ward-all").on("click", function () { frappe.route_options = { workflow_state: ["in", JSON.parse(this.dataset.states)] }; frappe.set_route("List", "Support Application"); });
            root.find(".ward-new-household").on("click", () => frappe.new_doc("Household"));
            root.find(".ward-new-application").on("click", () => frappe.new_doc("Support Application"));
        } catch (error) {
            root.html('<div class="ward-empty">Không tải được công việc. Hãy kiểm tra kết nối và chọn Làm mới.</div>');
        }
    };
};
frappe.pages["an-sinh-xa-hoi"].on_page_show = wrapper => {
    frappe.app.sidebar?.show_sidebar_for_module("Social Welfare");
    wrapper.load_ward_dashboard?.();
};
