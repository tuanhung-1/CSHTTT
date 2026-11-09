frappe.pages["bao-cao-tai-chinh"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({ parent: wrapper, title: "Báo cáo tài chính an sinh", single_column: true });
    const root = $('<div class="ward-finance"></div>').appendTo(page.main);
    const escape = frappe.utils.escape_html;
    const money = value => `${Number(value || 0).toLocaleString("vi-VN")} ₫`;
    const label = (text, value, footnote) => `<article class="ward-finance-kpi"><span>${text}</span><strong>${money(value)}</strong><small>${footnote}</small></article>`;
    wrapper.load_ward_finance = async () => {
        root.html('<p class="ward-finance-empty">Đang tải số liệu…</p>');
        try {
            const { message: data } = await frappe.call("social_welfare.bulk.financial_report");
            const maximum = Math.max(1, ...data.months.map(row => Number(row.amount)));
            root.html(`<header class="ward-finance-hero"><span>BÁO CÁO AN SINH PHƯỜNG</span><h1>Tình hình chi hỗ trợ</h1><p>Số liệu từ các đợt đã được lãnh đạo phê duyệt. “Đã chi” chỉ tính khoản được cán bộ tài chính xác nhận.</p></header>
                <section class="ward-finance-kpis">${label("Đã duyệt", data.totals.approved, "Tổng mức hỗ trợ tiền của đợt đã duyệt")}${label("Đã chi", data.totals.paid, `${data.totals.paid_count} khoản đã xác nhận`)}${label("Chờ chi", data.totals.pending, `${data.totals.pending_count} khoản đang chờ`)}</section>
                <div class="ward-finance-grid"><section class="ward-finance-panel"><h2>Chi thực tế theo tháng</h2>${data.months.length ? `<div class="ward-finance-chart">${data.months.map(row => `<div class="ward-finance-bar-row"><span>${escape(row.month)}</span><div class="ward-finance-track"><div style="width:${Math.max(3, Number(row.amount) / maximum * 100)}%"></div></div><strong>${money(row.amount)}</strong></div>`).join("")}</div>` : '<p class="ward-finance-empty">Chưa có khoản chi tiền được xác nhận.</p>'}</section>
                <section class="ward-finance-panel"><h2>Theo chương trình</h2>${data.programs.length ? `<div class="table-responsive"><table class="table table-bordered"><thead><tr><th>Chương trình</th><th>Đã duyệt</th><th>Đã chi</th><th>Chờ chi</th><th>Số khoản đã chi</th></tr></thead><tbody>${data.programs.map(row => `<tr><td>${escape(row.label)}</td><td>${money(row.approved)}</td><td>${money(row.paid)}</td><td>${money(row.pending)}</td><td>${row.paid_count}</td></tr>`).join("")}</tbody></table></div>` : '<p class="ward-finance-empty">Chưa có đợt hỗ trợ được duyệt.</p>'}</section></div>
                <p class="ward-finance-note">${escape(data.legacy_note)} Hỗ trợ hiện vật được đếm theo số khoản, không cộng vào tổng tiền.</p>`);
        } catch (error) {
            root.html('<p class="ward-finance-empty">Không tải được báo cáo. Hãy kiểm tra quyền hoặc kết nối và chọn Làm mới.</p>');
        }
    };
    page.add_inner_button("Làm mới", wrapper.load_ward_finance);
};
frappe.pages["bao-cao-tai-chinh"].on_page_show = wrapper => {
    frappe.app.sidebar?.show_sidebar_for_module("Social Welfare");
    wrapper.load_ward_finance?.();
};
