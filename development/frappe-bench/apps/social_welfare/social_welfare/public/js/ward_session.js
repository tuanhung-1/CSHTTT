(() => {
    let loggingOut = false;

    function resetButton() {
        loggingOut = false;
        $(".ward-session-logout").prop("disabled", false);
    }

    function logout() {
        if (loggingOut) return;
        loggingOut = true;
        $(".ward-session-logout").prop("disabled", true);
        frappe.call({
            method: "logout",
            freeze: true,
            freeze_message: "Đang đăng xuất…",
        }).then(response => {
            if (response.exc) {
                resetButton();
                return;
            }
            frappe.app.logged_out = true;
            if (window.cur_frm?.beforeUnloadListener) {
                removeEventListener("beforeunload", cur_frm.beforeUnloadListener, { capture: true });
            }
            window.location.assign("/login");
        }).catch(resetButton);
    }

    function mountLogout(event, frm) {
        if (!frappe.session || frappe.session.user === "Guest") return;
        const actions = frm?.page?.page_actions || $(frappe.container?.page).find(".page-head .page-actions").first();
        if (!actions.length || actions.find(".ward-session-logout").length) return;
        $('<button type="button" class="btn btn-default btn-sm ward-session-logout" aria-label="Đăng xuất tài khoản" title="Đăng xuất tài khoản">Đăng xuất</button>')
            .prop("disabled", loggingOut)
            .on("click", () => {
                if (window.cur_frm?.is_dirty()) {
                    frappe.confirm("Hồ sơ có thay đổi chưa lưu. Bạn muốn đăng xuất và bỏ các thay đổi này?", logout);
                } else {
                    logout();
                }
            }).prependTo(actions);
    }

    $(document).on("page-change.ward-session form-refresh.ward-session", mountLogout);
    frappe.router.on("change", () => requestAnimationFrame(mountLogout));
    frappe.after_ajax(mountLogout);
    $(mountLogout);
})();
