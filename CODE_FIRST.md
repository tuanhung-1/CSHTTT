# Hướng dẫn code-first cho nhóm

Dự án dùng **ERPNext/Frappe + MariaDB**. Hai máy dùng chung source trong Git, nhưng mỗi máy giữ database và dữ liệu riêng.

## 1. Những gì đi theo code

| Nội dung | Nơi sửa trong app social_welfare |
|---|---|
| Bảng, trường, liên kết và quyền | `social_welfare/social_welfare/doctype/<tên>/<tên>.json` |
| Kiểm tra và xử lý nghiệp vụ | Controller `.py` |
| Giao diện | Form/Page `.js`, `.css`, thư mục `public/` |
| Role và workflow | `social_welfare/fixtures/*.json`, khai báo trong `hooks.py` |
| Chuyển đổi dữ liệu cũ | File mới trong `social_welfare/patches/`, đăng ký ở `patches.txt` |

Không tự tạo/sửa bảng bằng SQL. Nếu dùng giao diện developer của Frappe, thay đổi phải được xuất về file trong app và kiểm tra bằng `git diff` trước khi commit.

## 2. Việc của người viết code

1. Sửa source và kiểm thử trên site test riêng.
2. Nếu thay đổi dữ liệu cũ: thêm **patch mới**; không sửa patch đã được nhóm sử dụng. Patch cần chạy lại an toàn và giữ dữ liệu người dùng.
3. Kiểm tra các file mới không bị `.gitignore` bỏ qua, rồi commit/push nhánh `thang`.

Schema được Frappe đồng bộ từ JSON; chỉ viết patch khi cần chuyển đổi dữ liệu hoặc xử lý nâng cấp đặc biệt. Patch sau schema đặt trong `[post_model_sync]` của `patches.txt`.

Đợt hiện tại có patch `social_welfare.patches.v0_1.migrate_legacy_classifications`: giữ phân loại cũ dưới dạng chưa rõ kỳ hiệu lực. Frappe ghi `Patch Log` để không chạy lại patch đã thành công. Trên site mới, hook cài đặt thực hiện phần khởi tạo cần thiết.

## 3. Việc của người nhận code

Áp dụng khi đã có Bench, site và app `social_welfare` được cài. Dừng `bench start` bằng **Ctrl+C** trước khi nâng cấp.

Ở thư mục repo trên máy nhận:

```bash
git pull --ff-only origin thang
```

Trong terminal container:

```bash
cd /workspace/development/frappe-bench
bench --site development.localhost backup --with-files
bench --site development.localhost migrate
bench --site development.localhost clear-cache
bench start
```

Thay `development.localhost` nếu site có tên khác. Khi đợt cập nhật yêu cầu build assets, chạy `bench build --app social_welfare` trước `bench start`.

Nếu migrate lỗi thì dừng, giữ log để sửa; không dùng `--skip-failing` để bỏ qua lỗi. Migrate lại sau khi sửa, không cần tạo lại database.

Mở `http://development.localhost:8000/desk/an-sinh-xa-hoi`, refresh bằng **Ctrl+Shift+R** để nhận giao diện mới.

## 4. Dữ liệu riêng của mỗi máy

Mỗi người tự tạo user, gán role, phân công hộ và nhập dữ liệu nghiệp vụ. Migration tạo/cập nhật cấu trúc và cấu hình app; không sao chép tài khoản, mật khẩu hoặc dữ liệu từ máy người viết code.

Migrate không tạo site mới hoặc tự cài app chưa có. Nếu thiếu site/app, cần chuẩn bị môi trường, tạo site bằng Bench và cài app trước. Không clone repo này bằng `bench get-app` như một app độc lập: source app nằm trong monorepo tại `development/frappe-bench/apps/social_welfare/`.

Không đưa database, `sites/`, backup, env hoặc mật khẩu lên Git. Không cần restore database của máy khác cho quy trình làm việc này.
