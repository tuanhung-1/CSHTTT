# Bàn giao dự án ERPNext / Social Welfare

Cập nhật: **08/11/2026**, múi giờ Việt Nam.

Tài liệu này ghi lại hiện trạng đã kiểm tra trên máy đang phát triển, để thành viên khác và Codex đọc trước khi làm tiếp. Các mục “đã có trong code”, “đã kiểm tra chạy” và “chưa làm” được ghi riêng để tránh hiểu nhầm mức độ hoàn thành.

## 1. Mục tiêu và nền tảng thống nhất

- Xây dựng hệ thống quản lý an sinh xã hội cấp phường.
- Nền tảng sử dụng: **Frappe + ERPNext**, app nghiệp vụ tự viết tên **`social_welfare`**.
- Thư mục dự án trên máy hiện tại: `D:\IT_THANG_23T_DT3\CSHTTT\erpnext-system`.
- Mục tiêu bàn giao tiếp theo: đưa đầy đủ code lên một nhánh riêng trong repo nhóm để bạn khác pull về tiếp tục phát triển.
- Repo nhóm được người dùng cung cấp: `https://github.com/tuanhung-1/CSHTTT.git`.
- Nhánh bàn giao đã tạo: **`thang`**, dùng để push vào repo nhóm.

Trong dự án có thư mục `odoo-reference`, và trên máy có container Odoo/PostgreSQL đang chạy cho môi trường khác. App `social_welfare` hiện tại sử dụng API, DocType và công cụ Bench của Frappe; không dùng Odoo làm nền tảng chạy.

## 2. Cấu trúc cần đọc

```text
erpnext-system/
├── PROJECT_HANDOFF.md          # Tài liệu bàn giao này
├── README.md                   # README gốc của Frappe Docker
├── compose.yaml                # Cấu hình Compose nền cho triển khai
├── pwd.yml                     # ERPNext demo riêng
├── .devcontainer/              # Cấu hình môi trường phát triển cục bộ
├── development/
│   └── frappe-bench/
│       ├── apps/
│       │   ├── frappe/          # Framework
│       │   ├── erpnext/         # ERPNext
│       │   └── social_welfare/  # App nghiệp vụ của nhóm
│       ├── sites/              # Site, cấu hình và file dữ liệu cục bộ
│       ├── env/                # Môi trường Python cục bộ
│       └── logs/               # Log cục bộ
├── overrides/                  # Các biến thể Docker Compose
├── images/                     # Dockerfile/Containerfile
├── resources/                  # Script và cấu hình hỗ trợ container
└── tests/                      # Test của Frappe Docker
```

Các đường dẫn trong app dưới đây được tính từ:

```text
development/frappe-bench/apps/social_welfare/
```

| Đường dẫn | Nội dung |
|---|---|
| `pyproject.toml` | Metadata, yêu cầu Python, cấu hình Ruff |
| `social_welfare/__init__.py` | Phiên bản app và kiểm tra quyền vào app |
| `social_welfare/hooks.py` | Đăng ký app trên màn hình Apps, khai báo fixtures |
| `social_welfare/social_welfare/doctype/` | Schema JSON, controller Python, JS và test nghiệp vụ |
| `social_welfare/social_welfare/workspace/social_welfare/social_welfare.json` | Workspace và lối tắt tới 4 DocType |
| `social_welfare/fixtures/` | Role, trạng thái, hành động và workflow hồ sơ |
| `social_welfare/public/images/social-welfare.svg` | Logo app |

## 3. Chức năng đã có trong mã nguồn

### Citizen — Công dân

- Các trường chính: mã công dân, CCCD/giấy tờ định danh, họ tên, ngày sinh, giới tính, quan hệ với chủ hộ, điện thoại, hộ gia đình.
- Tự sinh mã dạng `CT-000001` khi bỏ trống.
- Chuẩn hóa số định danh: bỏ khoảng trắng, chuyển chữ cái sang chữ hoa; chặn trùng nếu có nhập số định danh.
- Chặn ngày sinh trong tương lai.
- Cảnh báo khả năng trùng theo họ tên + ngày sinh, hoặc theo số điện thoại; đây là cảnh báo, không phải chặn lưu.
- Mỗi hộ chỉ có tối đa một công dân mang quan hệ `Head`.
- Không cho chuyển một công dân đang được hộ chọn làm chủ hộ sang hộ khác.
- Cập nhật số thành viên của hộ khi thêm, sửa, chuyển hộ hoặc xóa công dân.

### Household — Hộ gia đình

- Các trường chính: mã hộ, công dân làm chủ hộ, tên chủ hộ, địa chỉ, số thành viên, thu nhập bình quân, phân loại hộ.
- Tự sinh mã dạng `HH-2026-00001` khi bỏ trống; phần năm thay đổi theo thời điểm tạo.
- Thu nhập bình quân không được âm.
- Công dân được chọn làm chủ hộ phải thuộc chính hộ đó.
- Trường số thành viên được tính từ các bản ghi Citizen liên kết.
- Form lọc danh sách chọn chủ hộ theo hộ hiện tại.

### Support Program — Chương trình hỗ trợ

- Các trường chính: mã, tên, mô tả, ngày bắt đầu/kết thúc, mức hỗ trợ, nhóm đối tượng, cờ hoạt động.
- Mức hỗ trợ không được âm.
- Ngày bắt đầu không được sau ngày kết thúc.

### Support Application — Hồ sơ hỗ trợ

- Liên kết một hộ với một chương trình; lưu ngày hồ sơ, số tiền đề nghị/phê duyệt, lý do, ghi chú xét duyệt và trạng thái workflow.
- Tự sinh mã dạng `APP-2026-00001` khi bỏ trống.
- Hồ sơ mới phải bắt đầu ở `Draft`.
- Số tiền đề nghị và số tiền phê duyệt không được âm.
- Một hộ chỉ được có một hồ sơ cho cùng một chương trình.
- Chương trình có `target_group = poor` yêu cầu hộ thuộc `Poor Household`.
- Chương trình có `target_group = near_poor` yêu cầu hộ thuộc `Near-poor Household`.
- Các nhóm đối tượng khác chưa có điều kiện phân loại hộ tương ứng trong controller đã đọc.

Các mô tả trên được xác nhận bằng việc đọc code. Chưa kiểm thử đầy đủ từng chức năng qua giao diện trong phiên này.

## 4. Role và quyền đang định nghĩa

App có 3 role nghiệp vụ, lưu trong `social_welfare/fixtures/role.json`.

| Role | Citizen, Household, Support Application | Support Program |
|---|---|---|
| `Social Welfare Officer` | Tạo, đọc, sửa | Chỉ đọc |
| `Social Welfare Reviewer` | Tạo, đọc, sửa | Chỉ đọc |
| `Social Welfare Manager` | Tạo, đọc, sửa, xóa, import | Tạo, đọc, sửa, xóa, import |

Đây là quyền trong schema DocType; quyền sửa hồ sơ tại từng trạng thái còn chịu ràng buộc bởi workflow.

Hàm `has_app_permission()` cho phép `Administrator` hoặc người có ít nhất một trong 3 role trên vào app.

### Workflow hồ sơ

Fixture: `social_welfare/fixtures/zz_support_application_workflow.json`.

| Trạng thái hiện tại | Hành động | Trạng thái tiếp theo | Role thực hiện |
|---|---|---|---|
| Draft | Submit | Submitted | Officer hoặc Manager |
| Submitted | Start Review | Reviewing | Reviewer hoặc Manager |
| Reviewing | Approve | Approved | Reviewer hoặc Manager |
| Reviewing | Reject | Rejected | Reviewer hoặc Manager |
| Approved | Mark as Paid | Paid | Reviewer hoặc Manager |
| Rejected | Reset to Draft | Draft | Reviewer hoặc Manager |

Trong bảng, Officer/Reviewer/Manager là viết tắt của các role `Social Welfare ...` tương ứng.

Hiện tất cả các trạng thái workflow có `doc_status = 0`. Hành động `Submit` ở đây là chuyển trạng thái workflow, không phải chuyển document sang `docstatus = 1`.

`Mark as Paid` hiện là chuyển trạng thái hồ sơ. Chưa xác nhận có tích hợp thanh toán, bút toán hoặc giải ngân ERPNext; không coi trạng thái `Paid` là bằng chứng giao dịch đã được thực hiện.

## 5. Tài khoản thực tế trên máy hiện tại

Đã truy vấn database của site `development.localhost`:

| Tài khoản | Vai trò chính | Tình trạng |
|---|---|---|
| `Administrator` | Quản trị hệ thống | Đang bật |
| `officer@example.com` | Social Welfare Officer | Đang bật |
| `reviewer@example.com` | Social Welfare Reviewer | Đang bật |
| `manager@example.com` | Social Welfare Manager | Đang bật |
| `Guest` | Khách chưa đăng nhập | Tài khoản hệ thống |

- Đã thử đăng nhập 3 tài khoản nghiệp vụ bằng các mật khẩu do người dùng cung cấp trong cuộc trao đổi; tất cả đều trả HTTP 401, `Invalid login credentials`.
- Không ghi lại các mật khẩu đã thử vào tài liệu hoặc Git.
- Chưa xác định mật khẩu đúng, chưa đổi/reset mật khẩu nào và chưa kiểm tra đăng nhập thành công với Administrator.
- Các tài khoản này là dữ liệu của site cục bộ, **không tự xuất hiện khi người khác clone/pull code**.
- App chưa có fixture hoặc script tạo sẵn các tài khoản trên. Máy mới cần tạo tài khoản, gán role và đặt mật khẩu riêng.

## 6. Môi trường đã chạy thành công

Thông tin từ `bench --site development.localhost list-apps`:

| Thành phần | Phiên bản |
|---|---|
| Frappe | `16.35.0`, nhánh `version-16` |
| ERPNext | `16.36.0`, nhánh `version-16` |
| social_welfare | `0.0.1`, nhánh `version-16` |

- `pyproject.toml` của app yêu cầu **Python >= 3.14**.
- Dev Container dùng image `frappe/bench:latest`; tag này không cố định phiên bản runtime giữa các lần pull.
- MariaDB: image `mariadb:11.8`.
- Redis: hai service `redis-cache` và `redis-queue`, image `redis:alpine`.
- Site cục bộ: **`development.localhost`**.
- Cổng web: **8000**; realtime: **9000**; asset watcher: **6787**.
- Database host trong mạng container: `mariadb`.
- Redis dùng tên service trong mạng container, không phải `localhost`.

### Các việc đã thực hiện trong phiên hỗ trợ

1. Đọc cấu trúc, cấu hình Docker, app nghiệp vụ, quyền, workflow và các test hiện có.
2. Kiểm tra remote Git và tình trạng Git riêng của app.
3. Mở thư mục dự án bằng một cửa sổ VS Code riêng để tránh lỗi workspace nhiều thư mục.
4. Khởi động lại 4 container Dev Container đã có: `frappe`, `mariadb`, `redis-cache`, `redis-queue`.
5. Kết nối VS Code vào Dev Container.
6. Chạy `bench start` trong Bench hiện có.
7. Xác nhận site có đủ 3 app; trang `/login` trả HTTP **200**, `/api/method/ping` trả `{"message":"pong"}`.
8. Đọc danh sách user/role thực tế và thử đăng nhập theo yêu cầu.
9. Tạo tài liệu bàn giao này; không sửa logic nghiệp vụ.
10. Theo yêu cầu push tiếp theo: tạo nhánh `thang`, thêm repo nhóm làm `origin`, giữ Frappe Docker làm `upstream`, đưa source app và Dev Container vào phạm vi theo dõi Git. Xem mục 8 để biết cách kiểm tra remote sau khi push.

Bench trong phiên này được chạy nền bằng `docker exec`; log tại **`/tmp/erpnext-bench-start.log` bên trong container**. Tiến trình này không được cấu hình tự chạy lại sau khi container khởi động lại. Không chạy thêm một `bench start` nếu tiến trình cũ vẫn chiếm các cổng.

## 7. Chạy lại trên máy đã có môi trường và dữ liệu

### Cách dùng VS Code

1. Mở Docker Desktop, chờ Docker Engine sẵn sàng.
2. Mở một cửa sổ VS Code riêng, chọn **Open Folder** tới thư mục `erpnext-system`.
3. Dùng extension **Dev Containers** của Microsoft.
4. Chạy **Dev Containers: Reopen in Container**.
5. Trong terminal của container:

```bash
cd /workspace/development/frappe-bench
bench --site development.localhost list-apps
```

Nếu Bench chưa chạy:

```bash
bench use development.localhost
bench start
```

Mở **http://development.localhost:8000/login**. Giữ Docker và cửa sổ Dev Container đang mở; cấu hình hiện tại có `shutdownAction: stopCompose`.

### Nếu VS Code báo lỗi workspace

Thông báo đã gặp:

```text
You need to first save your workspace in a folder containing all its workspace folders.
```

Cách xử lý đã dùng: mở **New Window → Open Folder → erpnext-system**, thay vì mở workspace nhiều thư mục hoặc file `.code-workspace`, rồi Reopen in Container.

### Nếu lỗi bind mount

Bản cấu hình cục bộ ban đầu có mount thư mục anh em `../social-welfare-system` và thư mục `.ssh` của máy cá nhân. Bản cấu hình được bàn giao đã bỏ hai mount này cùng kết nối SQLTools chứa thông tin đăng nhập cục bộ, để máy nhận không phụ thuộc các đường dẫn đó. Container đang chạy có thể vẫn giữ mount cũ đến lần tạo lại tiếp theo.

### Phân biệt cấu hình demo

`docker compose -f pwd.yml up -d` tạo một môi trường ERPNext demo riêng, cổng **8080**. Nó không thay thế môi trường phát triển đang có `social_welfare`. Mật khẩu Administrator khai báo trong demo không chứng minh mật khẩu của site `development.localhost`.

## 8. Git: nhánh bàn giao và thay đổi đóng gói

Tại thời điểm ghi tài liệu:

```text
Repo gốc: erpnext-system
Nhánh bàn giao: thang
Remote origin: https://github.com/tuanhung-1/CSHTTT.git
Remote upstream: https://github.com/frappe/frappe_docker.git
```

- Source `social_welfare` được theo dõi trực tiếp trong repo gốc, ở `development/frappe-bench/apps/social_welfare/`; không dùng submodule.
- Metadata Git riêng của app đã được di chuyển ra ngoài repo, tại `D:\IT_THANG_23T_DT3\CSHTTT\social_welfare.git.backup-20261108` trên máy phát triển. Đây là bản sao lưu lịch sử và index cũ, không chứa bản sao working tree và không được đưa lên GitHub.
- Các thay đổi trước đây chưa commit trong Git riêng của app được đưa vào bản bàn giao: `__init__.py`, `hooks.py`, fixtures, logo, DocType, workspace.
- `.gitignore` gốc đã cho phép source app và hai file cấu hình `.devcontainer/devcontainer.json`, `.devcontainer/docker-compose.yml` đi theo Git, vẫn bỏ qua phần runtime Bench, dữ liệu site, env và cache.
- Không thay đổi nhánh `main` hoặc `feat/odoo` của repo nhóm.

Trước khi đóng gói, Git gốc báo sạch vì source app bị ignore và có Git lồng nhau. Hai vấn đề này đã được xử lý cho nhánh bàn giao. Vẫn cần kiểm tra danh sách file mỗi lần commit để tránh bỏ sót source hoặc đưa dữ liệu cục bộ lên.

### Người nhận tải nhánh bàn giao

```bash
git clone --branch thang --single-branch https://github.com/tuanhung-1/CSHTTT.git
cd CSHTTT
```

Nếu đã clone repo và working tree không có thay đổi cần xử lý:

```bash
git fetch origin
git switch thang
git pull --ff-only origin thang
```

Đọc `PROJECT_HANDOFF.md` trước khi chạy môi trường. Không cần `git submodule update` cho app này. Kiểm tra nhánh trên remote bằng `git ls-remote --heads origin thang`; chỉ coi push hoàn tất khi remote có commit tương ứng.

Các file Compose có giá trị mật khẩu mặc định dùng cho phát triển/demo; người nhận cần cấu hình phù hợp với môi trường của mình. Đây không phải mật khẩu đã xác nhận cho các user nghiệp vụ.

Repo nhóm đã được khởi tạo riêng với README; lịch sử Frappe Docker có thể không chung gốc với `main` của repo nhóm. Chọn cách tích hợp trước khi mở Pull Request; không tự force-push hoặc ghi đè nhánh chung.

### Những gì không đi theo Git

- Database MariaDB, Docker volumes.
- User, mật khẩu, hồ sơ công dân/hộ gia đình và dữ liệu nghiệp vụ đang nhập trên site.
- Môi trường Python `env/`, `node_modules/`, cache, log.
- `sites/*/site_config.json`, khóa mã hóa và thông tin kết nối bí mật.

## 9. Máy mới sau khi pull: chưa phải chỉ cần bench start

Quy trình khởi động ở mục 7 chỉ áp dụng khi đã có Bench, dependencies, site và database. **Chưa thực hiện kiểm chứng cài mới từ một bản clone sạch** trong phiên này.

Sau khi hoàn tất đóng gói Git, cần viết và thử quy trình bootstrap trên máy sạch:

1. Có Docker, VS Code và Dev Containers; clone đúng repo/nhánh.
2. Có cấu hình Dev Container dùng chung, không phụ thuộc đường dẫn cá nhân.
3. Khởi tạo Bench và lấy Frappe/ERPNext nhánh `version-16`, dùng Python phù hợp với app.
4. Đưa source `social_welfare` vào Bench và cài package/dependencies; không mặc định rằng copy thư mục app là đủ.
5. Cấu hình MariaDB, Redis theo tên service của Compose.
6. Tạo site mới, cài `erpnext` và `social_welfare`; hoặc khôi phục backup được chia sẻ riêng nếu cần dữ liệu cũ.
7. Đồng bộ schema/fixtures, build assets, tạo user và gán role.
8. Kiểm tra đăng nhập, quyền và workflow bằng tài khoản thực tế.

Tên site trên máy nhận có thể khác; thay `development.localhost` trong các lệnh cho đúng. Không sao chép mật khẩu hoặc cấu hình site cá nhân để mặc định cho cả nhóm.

## 10. Test và mức độ kiểm chứng

Test nghiệp vụ hiện có trong source:

- `test_citizen.py`: chủ hộ duy nhất, số thành viên, ràng buộc chủ hộ khi chuyển hộ, thu nhập âm, ngày sinh tương lai, tự sinh mã, chuẩn hóa/trùng số định danh, trùng mã.
- `test_support_application.py`: tự sinh mã hồ sơ và trạng thái ban đầu Draft.
- `tests/` ở gốc thuộc Frappe Docker, khác với test của app nghiệp vụ.

**Chưa chạy test suite trong phiên hỗ trợ này.** Chỉ đã kiểm tra app được cài, HTTP trang đăng nhập, API ping và các lần đăng nhập nêu trên. Chưa xác nhận toàn bộ workflow, phân quyền và cài đặt trên máy mới hoạt động đúng.

Khi cần kiểm thử, dùng site test riêng đã cài đủ app và cấu hình cho phép chạy test theo Frappe. Ví dụ, sau khi đã chuẩn bị site test:

```bash
bench --site <test-site> run-tests --app social_welfare
```

Không tự chạy test trên site đang chứa dữ liệu cần giữ.

## 11. Thứ tự làm tiếp cho thành viên và Codex

1. Đọc tài liệu này, kiểm tra lại `git status`, `git remote -v` và nhánh hiện tại ở repo gốc; app được theo dõi trực tiếp trong repo này.
2. Xác nhận đã tải đúng nhánh `thang`, có source app, fixtures và cấu hình Dev Container.
3. Thử clone/cài mới và bổ sung hướng dẫn bootstrap có thể tái lập.
4. Khôi phục quyền đăng nhập cho các user thử nghiệm theo yêu cầu của người quản lý; không tự đoán hoặc thay mật khẩu hàng loạt.
5. Kiểm thử quyền của 3 role, chuyển trạng thái hồ sơ và các ràng buộc dữ liệu.
6. Tiếp tục tính năng mới theo yêu cầu nhóm, ưu tiên sửa trong app `social_welfare`; xem xét kỹ trước khi thay đổi framework `frappe` hoặc core `erpnext`.
7. Cập nhật tài liệu này khi thay đổi cách chạy, role, workflow, Git hoặc phạm vi đã kiểm chứng. Không đưa mật khẩu vào tài liệu.

Prompt gợi ý để người nhận bắt đầu với Codex:

> Đọc PROJECT_HANDOFF.md, sau đó kiểm tra hiện trạng repo và app social_welfare. Dự án dùng Frappe/ERPNext. Xác định những phần đã có và phần còn thiếu để chạy trên máy này, rồi tiếp tục công việc theo yêu cầu của tôi. Không mặc định tài khoản hoặc database trên máy cũ đã đi theo Git.
