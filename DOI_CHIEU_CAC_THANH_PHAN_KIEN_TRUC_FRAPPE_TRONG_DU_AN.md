# Đối chiếu các thành phần kiến trúc Frappe với dự án An sinh xã hội

Tài liệu này giải thích 9 thành phần trong bảng kiến trúc được cung cấp và chỉ ra chúng xuất hiện ở đâu trong dự án. Các tên như **Request Queue** và **Multi-Tenant Layer** là cách chia theo chức năng; chúng không nhất thiết là tên thư mục trong mã nguồn.

## 1. Sơ đồ tổng quan của dự án

```text
Người dùng (trình duyệt)
        ↓ HTTP
Frappe Desk / Form / Page / JavaScript       ← Viewing I/O Interface
        ↓ frappe.call() hoặc lưu DocType
Frappe web + quyền + API của social_welfare   ← Xử lý yêu cầu trực tiếp
        ↓
Controller / nghiệp vụ / Frappe ORM
        ↓
MariaDB (bản ghi của site development.localhost)

Bench quản lý web, socketio, watch, schedule, worker.
Redis cache và Redis queue hỗ trợ Frappe; worker dùng Redis queue cho việc nền.
```

**Phân biệt:** Yêu cầu HTTP thông thường được web process xử lý trực tiếp. `redis-queue` phục vụ công việc nền; tên `QUEUED` của một hồ sơ nghiệp vụ chưa đủ để kết luận công việc đã được đưa vào Redis.

## 2. Đối chiếu từng thành phần

| Thành phần trong hình | Vai trò | Biểu hiện trong dự án | Mức độ hiện tại |
|---|---|---|---|
| **Viewing I/O Interface** | Giao diện vào/ra cho người dùng | Frappe Desk; trang `an-sinh-xa-hoi`; form và list của DocType; JavaScript gọi API | Đang dùng |
| **Request Queue** | Hàng đợi công việc nền | Dịch vụ `redis-queue` và tiến trình `bench worker` | Hạ tầng có sẵn; luồng rà soát hiện chạy trực tiếp |
| **Configuration Layer** | Cấu hình Bench, site và app | `common_site_config.json`, `site_config.json`, `hooks.py`, `Procfile` | Đang dùng |
| **Multi-Tenant Layer** | Tách cấu hình và dữ liệu theo site | `sites/development.localhost/`; `installed_apps` của site gồm Frappe, ERPNext, `social_welfare` | Hiện có một site phát triển |
| **Scheduling Layer** | Kích hoạt tác vụ theo lịch | `schedule: bench schedule` và `worker: bench worker` trong `Procfile` | Tiến trình có; app chưa khai báo lịch riêng |
| **Prerequisites** | Dịch vụ và công cụ cần để chạy | MariaDB, Redis cache/queue; Node.js cho tài nguyên giao diện | MariaDB/Redis có trong Compose; Nginx không được cấu hình cho môi trường dev này |
| **Bench** | Quản lý môi trường Frappe, app và site | Thư mục `development/frappe-bench/`, lệnh `bench`, `Procfile` | Đang dùng |
| **Dependencies** | Công cụ và thư viện phục vụ cài đặt/phát triển | Git, Python, pip; `pyproject.toml` của app yêu cầu Python ≥ 3.14 | Được khai báo/sử dụng trong môi trường phát triển |
| **OS Layer** | Hệ điều hành chạy các tiến trình | Máy làm việc macOS; Dev Container dùng môi trường Linux | Cấu hình phát triển hiện tại |

### 2.1. Viewing I/O Interface — giao diện người dùng

- Trang tổng quan ở `social_welfare/social_welfare/page/an_sinh_xa_hoi/` hiển thị số liệu, công việc theo vai trò và nút mở danh sách.
- Các form DocType như `household/household.js` và `support_program/support_program.js` hiển thị thao tác theo hồ sơ.
- Ví dụ trang tổng quan gọi `social_welfare.api.dashboard` bằng `frappe.call()`, rồi nhận dữ liệu để vẽ các thẻ trên màn hình.

**Đường dẫn tham khảo:** `development/frappe-bench/apps/social_welfare/social_welfare/social_welfare/page/an_sinh_xa_hoi/an_sinh_xa_hoi.js`, `development/frappe-bench/apps/social_welfare/social_welfare/api.py`.

### 2.2. Request Queue — yêu cầu trực tiếp và công việc nền

Có hai đường xử lý cần tách rõ:

1. **Yêu cầu trực tiếp:** trình duyệt gọi API, web process thực hiện và trả kết quả. Nút **Chạy rà soát hàng loạt** gọi `social_welfare.eligibility.screen_program()` theo cách này.
2. **Công việc nền:** Frappe có `redis-queue` và `bench worker` để nhận các việc được đưa vào hàng đợi. Mã app `social_welfare` hiện không gọi `frappe.enqueue()` cho luồng rà soát.

Trong `screen_program()`, hồ sơ `Eligibility Run` được tạo với trạng thái `QUEUED`, rồi chuyển sang `RUNNING` và `COMPLETED` ngay trong lời gọi xử lý đó. Đây là **trạng thái nghiệp vụ**, không phải bằng chứng rằng hàm đã chạy qua Redis queue. Các mục “hàng đợi công việc” trên dashboard cũng là danh sách hồ sơ cần xử lý theo vai trò, không phải Redis queue.

**Đường dẫn tham khảo:** `development/frappe-bench/Procfile`, `development/frappe-bench/apps/social_welfare/social_welfare/eligibility.py`, `development/frappe-bench/apps/social_welfare/social_welfare/social_welfare/doctype/support_program/support_program.js`.

### 2.3. Configuration Layer — cấu hình

| Vị trí | Chức năng trong dự án |
|---|---|
| `sites/common_site_config.json` | Thiết lập dùng chung, ví dụ site mặc định, cổng web và địa chỉ Redis |
| `sites/development.localhost/site_config.json` | Cấu hình riêng của site và danh sách app được cài trên site |
| `apps/social_welfare/social_welfare/hooks.py` | Đăng ký app, tài nguyên giao diện, quyền, sự kiện và fixture |
| `Procfile` | Khai báo các tiến trình web, socketio, watch, schedule, worker |
| `.devcontainer/docker-compose.yml` | Khai báo container Frappe, MariaDB và Redis cho môi trường dev |

Các tệp cấu hình site có thể chứa thông tin kết nối; khi đưa vào slide chỉ trình bày **tên mục cấu hình và chức năng**.

### 2.4. Multi-Tenant Layer — nhiều site

- Bench có thể chứa nhiều site; mỗi site có cấu hình, dữ liệu và danh sách app đã cài riêng.
- Trong workspace hiện tại, site nghiệp vụ được quan sát là `development.localhost`; `installed_apps` của site này gồm `frappe`, `erpnext`, `social_welfare`.
- `sites/apps.txt` liệt kê các app có sẵn trong Bench. Danh sách này khác với danh sách app đã cài trên một site cụ thể.
- Vì hiện chỉ thấy **một site phát triển**, phần nhiều site là khả năng của kiến trúc Frappe, chưa phải tính năng đã demo bằng hai site của dự án.

**Đường dẫn tham khảo:** `development/frappe-bench/sites/apps.txt`, `development/frappe-bench/sites/development.localhost/site_config.json`.

### 2.5. Scheduling Layer — tác vụ theo lịch

- `Procfile` khai báo `schedule: bench schedule` và `worker: bench worker`.
- Trong `social_welfare/hooks.py`, phần mẫu `scheduler_events` hiện được **comment**, chưa khai báo tác vụ theo lịch riêng của app.
- Các thao tác quan trọng của ứng dụng như chạy rà soát, ghi kết luận và duyệt đợt hiện được kích hoạt từ người dùng qua giao diện/API.

Vì vậy khi trình bày, có thể nói **hạ tầng scheduler/worker đã có**, còn **nghiệp vụ an sinh hiện chủ yếu chạy theo thao tác người dùng**.

### 2.6. Prerequisites — dịch vụ và công cụ hỗ trợ

- **MariaDB 11.8:** lưu bản ghi DocType của site; được khai báo bằng service `mariadb` trong `.devcontainer/docker-compose.yml`.
- **Redis:** hai service `redis-cache` và `redis-queue` trong Compose; `common_site_config.json` trỏ đến chúng.
- **Node.js:** dùng cho công cụ build/watch tài nguyên giao diện của Frappe; mã nguồn Frappe có `package.json`, Bench có tiến trình `watch`.
- **Nginx:** thường xuất hiện trong sơ đồ triển khai Frappe, nhưng **không có service Nginx** trong Compose phát triển của dự án. Ở đây `Procfile` dùng `bench serve --port 8000` cho web. Không nên mô tả Nginx là thành phần đang chạy trong bản dev này.

### 2.7. Bench — công cụ điều phối

Bench là công cụ quản lý môi trường Frappe: tạo/quản lý site, cài app, migrate, build tài nguyên và chạy các tiến trình phát triển. Thư mục `development/frappe-bench/` chứa `apps/`, `sites/`, `env/`, `config/`, `logs/` và `Procfile`.

Các lệnh nhóm dùng trong tài liệu dự án:

```bash
cd development/frappe-bench
bench --site development.localhost migrate
bench build --app social_welfare
bench start
```

**Đường dẫn tham khảo:** `CODE_FIRST.md`, `development/frappe-bench/Procfile`.

### 2.8. Dependencies — phụ thuộc để phát triển

- **Git** quản lý mã nguồn; ba app nằm trong `apps/` và app `social_welfare` là mã của đề tài.
- **Python và pip** cài/chạy phần máy chủ. `apps/social_welfare/pyproject.toml` khai báo Python **≥ 3.14** cho app.
- **Node.js** phục vụ tài nguyên JavaScript/CSS, có thể trình bày cùng nhóm công cụ phát triển; nó không thay thế phần xử lý nghiệp vụ Python.
- `env/` là môi trường Python của Bench được tạo cho Dev Container; đường dẫn Python trong đó trỏ tới môi trường Linux của container.

### 2.9. OS Layer — hệ điều hành

Máy đang làm việc sử dụng **macOS**; dự án cấu hình **Dev Container** với service `frappe` để chạy công cụ Bench trong môi trường Linux. `.devcontainer/devcontainer.json` mở workspace tại `/workspace/development` và chuyển tiếp các cổng 8000 (web), 9000 (realtime), 6787 (asset watcher). Vì vậy các lệnh `bench` trong tài liệu được chạy **bên trong container**.

## 3. Ví dụ xuyên suốt để giải thích trên slide

**Cán bộ bấm “Chạy rà soát hàng loạt”:**

1. **Viewing I/O Interface:** `support_program.js` hiển thị nút và gửi `frappe.call()`.
2. **Điểm vào và phân quyền:** Frappe định tuyến đến API; `screen_program()` kiểm tra vai trò cán bộ, chương trình và phiên bản chính sách. Cách định tuyến và quyền được đăng ký qua cấu hình app.
3. **Business/Data:** `eligibility.py` tính từng điều kiện; Frappe ORM lưu `Eligibility Run` và `Eligibility Result` vào MariaDB.
4. **Response:** API trả mã lần rà soát; giao diện mở form kết quả mới.

Luồng này chạy trực tiếp trong request hiện tại. Nếu sau này muốn xử lý ở nền, nhóm cần thiết kế bước đưa việc vào Redis queue, worker xử lý và cơ chế theo dõi tiến độ/lỗi.

## 4. Nội dung ngắn để đưa vào một slide

**Tiêu đề:** *Các thành phần kiến trúc Frappe trong dự án An sinh xã hội*

```text
Người dùng → Frappe Desk → API + phân quyền → Python nghiệp vụ → MariaDB
                      Bench quản lý web / schedule / worker
                      Redis hỗ trợ cache và công việc nền
```

- `social_welfare` cung cấp giao diện, DocType và quy trình an sinh.
- Site hiện tại: `development.localhost`, cài Frappe, ERPNext và `social_welfare`.
- Scheduler/Redis queue có trong hạ tầng; luồng rà soát hiện chạy trực tiếp.
- Môi trường dev dùng `bench serve` và không khai báo Nginx.

**Câu nói gợi ý:** “Hình kiến trúc mô tả các khả năng của Frappe. Trong dự án, chúng tôi đã dùng giao diện Desk, cấu hình site, DocType, API và phân quyền. Bench cùng MariaDB/Redis cung cấp môi trường vận hành. Những phần như nhiều site, lịch chạy riêng và Nginx chưa được dùng trong bản demo hiện tại.”
