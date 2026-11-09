frappe.pages["an-sinh-xa-hoi"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({parent: wrapper, title: "Công việc an sinh", single_column: true});
    const root = $('<div class="ward-app" aria-live="polite"></div>').appendTo(page.main);
    const escape = frappe.utils.escape_html;
    const roleLabels = {
        "Social Welfare Officer": "Cán bộ an sinh", "Social Welfare Reviewer": "Người xác minh",
        "Social Welfare Manager": "Lãnh đạo phường", "Social Welfare Finance": "Cán bộ tài chính",
    };
    const list = (doctype, filters = {}) => {
        frappe.route_options = Object.keys(filters).length ? filters : null;
        frappe.set_route("List", doctype);
    };
    page.add_inner_button("Làm mới", () => wrapper.load_ward_dashboard());
    wrapper.load_ward_dashboard = async () => {
        root.html('<p class="ward-empty">Đang tải công việc của bạn…</p>');
        try {
            const {message: data} = await frappe.call("social_welfare.api.dashboard");
            const roles = data.roles.filter(role => roleLabels[role]);
            root.html(`
                <section class="ward-hero">
                    <div><div class="ward-eyebrow">AN SINH XÃ HỘI PHƯỜNG</div>
                    <h1>${escape(data.home_title)}</h1>
                    <p>Chọn công việc cần xử lý hoặc mở một danh sách để xem hồ sơ theo quyền của bạn.</p>
                    <div class="ward-role-list">${frappe.session.user === "Administrator" ? '<span>Quản trị hệ thống</span>' : roles.map(role => `<span>${escape(roleLabels[role])}</span>`).join("")}</div></div>
                    <div class="ward-hero-mark" aria-hidden="true">AS<br><small>AN SINH XÃ HỘI</small></div>
                </section>
                <section class="ward-cards" aria-label="Tổng quan công việc">${data.overview.map((card, index) => `
                    <button class="ward-card" data-doctype="${escape(card.doctype)}" data-filters="${escape(JSON.stringify(card.filters || {}))}">
                        <span class="ward-card-index">${String(index + 1).padStart(2, "0")}</span><strong>${Number(card.count).toLocaleString("vi-VN")}</strong>
                        <span class="ward-card-label">${escape(card.label)}</span><span class="ward-card-link">Mở danh sách →</span>
                    </button>`).join("")}</section>
                <div class="ward-body"><section class="ward-work"><div class="ward-section-title"><h2>Công việc cần xử lý</h2><span>Chỉ hiển thị việc thuộc vai trò của bạn</span></div>
                    ${data.queues.length ? data.queues.map(queue => `<article class="ward-task"><div class="ward-task-heading"><h3>${escape(queue.title)}</h3><button class="btn btn-sm btn-default ward-all" data-doctype="${escape(queue.doctype)}" data-filters="${escape(JSON.stringify(queue.filters || {}))}">Xem tất cả →</button></div>
                    ${queue.items.length ? `<div class="ward-task-list">${queue.items.map(item => `<button class="ward-task-row" data-doctype="${escape(queue.doctype)}" data-name="${escape(item.name)}"><div><strong>${escape(item.name)}</strong><small>${escape(item.subtitle || "")}</small></div><span class="ward-state">${escape(wardUI.label(item.status))}</span></button>`).join("")}</div>` : '<p class="ward-empty">Hiện chưa có mục nào cần xử lý.</p>'}</article>`).join("") : '<p class="ward-empty">Hiện chưa có hàng đợi cho vai trò này.</p>'}
                </section><aside class="ward-side"><h2>Thao tác nhanh</h2>
                    ${data.quick_actions.map((action, index) => `<button class="btn ${index === 0 ? "btn-primary" : "btn-default"} btn-block ward-quick-action" data-target="${escape(action.target)}" data-type="${escape(action.type)}" data-filters="${escape(JSON.stringify(action.filters || {}))}">${escape(action.label)}</button>`).join("")}
                    <div class="ward-guidance"><h3>Luồng hỗ trợ</h3><p>Tiếp nhận dữ liệu → Rà soát → Lập đợt trình → Lãnh đạo quyết định → Tài chính xác nhận chi.</p></div>
                </aside></div>`);
            root.find(".ward-card,.ward-all").on("click", function () { list(this.dataset.doctype, JSON.parse(this.dataset.filters)); });
            root.find(".ward-task-row").on("click", function () { frappe.set_route("Form", this.dataset.doctype, this.dataset.name); });
            root.find(".ward-quick-action").on("click", function () {
                const {target, type, filters} = this.dataset;
                if (type === "new") frappe.new_doc(target);
                else if (type === "page") frappe.set_route(target);
                else list(target, JSON.parse(filters));
            });
        } catch (error) {
            root.html('<p class="ward-empty">Không tải được công việc. Hãy kiểm tra kết nối và chọn Làm mới.</p>');
        }
    };
};
frappe.pages["an-sinh-xa-hoi"].on_page_show = wrapper => {
    frappe.app.sidebar?.show_sidebar_for_module("Social Welfare");
    wrapper.load_ward_dashboard?.();
};
