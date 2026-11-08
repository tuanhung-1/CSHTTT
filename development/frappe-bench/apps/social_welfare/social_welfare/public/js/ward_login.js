// Brand the public login page without replacing Frappe's authentication forms.
(function () {
    function setText(selector, value) {
        document.querySelectorAll(selector).forEach(element => {
            element.textContent = value;
        });
    }

    function renderWardLogin() {
        if (document.body.dataset.path !== "login") return;

        const sections = document.querySelector(".page_content > div");
        if (!sections || sections.classList.contains("ward-login-shell")) return;

        sections.classList.add("ward-login-shell");
        const introduction = document.createElement("aside");
        introduction.className = "ward-login-intro";
        introduction.setAttribute("aria-label", "Giới thiệu hệ thống an sinh xã hội");
        introduction.innerHTML = `
            <div class="ward-login-brand">
                <img src="/assets/social_welfare/images/social-welfare.svg" alt="" width="48" height="48">
                <div><strong>An sinh xã hội phường</strong><span>Hệ thống quản lý hồ sơ</span></div>
            </div>
            <div class="ward-login-message">
                <span class="ward-login-kicker">KHÔNG GIAN LÀM VIỆC THỐNG NHẤT</span>
                <h1>Phục vụ người dân<br><em>rõ ràng trong từng bước.</em></h1>
                <p>Quản lý hộ gia đình, lịch sử phân loại và hồ sơ hỗ trợ trên một hệ thống dành cho cán bộ phường.</p>
            </div>
            <div class="ward-login-process" aria-label="Quy trình xử lý hồ sơ">
                <span><b>01</b> Tiếp nhận</span><i aria-hidden="true"></i>
                <span><b>02</b> Xác minh</span><i aria-hidden="true"></i>
                <span><b>03</b> Phê duyệt và chi trả</span>
            </div>
            <p class="ward-login-intro-note">Truy cập dành cho tài khoản được phân quyền. Mỗi vai trò sẽ nhìn thấy công việc phù hợp sau khi đăng nhập.</p>`;
        sections.prepend(introduction);

        document.querySelectorAll(".ward-login-shell .page-card-head").forEach(header => {
            const logo = header.querySelector(".app-logo");
            if (logo) {
                logo.src = "/assets/social_welfare/images/social-welfare.svg";
                logo.alt = "Biểu trưng An sinh xã hội phường";
            }
        });

        setText(".for-login .page-card-head h4, .for-email-login .page-card-head h4", "Đăng nhập hệ thống");
        setText(".for-login .page-card-subtitle, .for-email-login .page-card-subtitle", "Chào mừng bạn trở lại. Nhập tài khoản được cấp để tiếp tục.");
        setText(".for-login label[for='login_email'], .for-email-login label[for='login_email']", "Email hoặc tên đăng nhập");
        setText(".for-login label[for='login_password'], .for-email-login label[for='login_password']", "Mật khẩu");
        setText(".for-login .btn-login:not(.btn-ldap-login), .for-email-login .btn-login:not(.btn-ldap-login)", "Đăng nhập");
        setText(".forgot-password-message a", "Quên mật khẩu?");
        setText(".for-forgot .page-card-head h4", "Khôi phục mật khẩu");
        setText(".for-forgot .page-card-subtitle", "Nhập email tài khoản để nhận liên kết đặt lại mật khẩu.");
        setText(".for-forgot .sign-up-message a", "Quay lại đăng nhập");
        setText(".for-login-with-email-link .page-card-head h4", "Đăng nhập bằng email");
        setText(".for-login-with-email-link .page-card-subtitle", "Nhận liên kết đăng nhập qua email tài khoản.");

        document.querySelectorAll("#login_email").forEach(input => {
            input.placeholder = "Email hoặc tên đăng nhập";
        });
        document.querySelectorAll("#login_password").forEach(input => {
            input.placeholder = "Nhập mật khẩu";
        });
        document.title = "Đăng nhập | An sinh xã hội phường";
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", renderWardLogin, { once: true });
    } else {
        renderWardLogin();
    }
})();
