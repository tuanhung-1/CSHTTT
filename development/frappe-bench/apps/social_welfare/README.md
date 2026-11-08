### Social Welfare

Ward-level social welfare management system

### Installation

App này nằm trong monorepo ERPNext/MariaDB của nhóm. Đọc [hướng dẫn code-first](../../../../CODE_FIRST.md) và [tài liệu bàn giao](../../../../PROJECT_HANDOFF.md).

Khi Bench đã đăng ký package `social_welfare` và site đã được tạo:

```bash
cd /workspace/development/frappe-bench
bench --site development.localhost install-app social_welfare
bench --site development.localhost migrate
```

Lệnh trên không tạo môi trường Bench mới. Không dùng `bench get-app` trỏ vào repo monorepo gốc; đây không phải repository độc lập của riêng app. User và dữ liệu nghiệp vụ do mỗi máy tự tạo.

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/social_welfare
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
