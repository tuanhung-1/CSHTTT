# Bàn giao ứng dụng an sinh xã hội phường

Cập nhật: **08/11/2026**, múi giờ Việt Nam.

Hướng dẫn cập nhật giữa hai máy: [CODE_FIRST.md](CODE_FIRST.md).

Kịch bản nhập dữ liệu, demo và kiểm thử xuyên suốt hiện tại: [HUONG_DAN_DEMO_VA_TEST_TOAN_BO.md](HUONG_DAN_DEMO_VA_TEST_TOAN_BO.md).

Dự án chỉ dùng **ERPNext/Frappe + MariaDB**. Các mục Odoo/PostgreSQL trong tài liệu nghiên cứu cũ không phải kiến trúc triển khai của app này.

## 1. Source và Git

- Máy phát triển: `D:\IT_THANG_23T_DT3\CSHTTT\erpnext-system`.
- Repo nhóm: `https://github.com/tuanhung-1/CSHTTT.git`, nhánh **thang**.
- `origin` là repo nhóm; `upstream` là repo `frappe/frappe_docker`.
- Mốc đã push trước đợt sửa hiện tại: **ad616e5**. Các thay đổi lịch sử phân loại, quyền và giao diện được thực hiện sau mốc này; kiểm tra `git status`/`git log` để biết phần nào đã commit và push.
- Source app được theo dõi trực tiếp trong repo gốc, không dùng submodule.
- Metadata Git riêng của app trước đây đã được giữ ngoài repo tại `D:\IT_THANG_23T_DT3\CSHTTT\social_welfare.git.backup-20261108`.

```bash
git clone -b thang --single-branch https://github.com/tuanhung-1/CSHTTT.git
cd CSHTTT
```

Nhánh mang lịch sử Frappe Docker, có thể không chung gốc với main của repo nhóm. Không force-push hoặc ghi đè nhánh chung.

## 2. Môi trường đã kiểm tra

| Thành phần | Phiên bản hoặc cấu hình |
|---|---|
| Frappe | 16.35.0, version-16 |
| ERPNext | 16.36.0, version-16 |
| social_welfare | 0.0.1; yêu cầu Python >= 3.14 |
| MariaDB | mariadb:11.8 |
| Redis | redis-cache và redis-queue |
| Dev Container | frappe/bench:latest; chưa pin runtime |
| Site phát triển | development.localhost |
| Cổng web / realtime / watcher | 8000 / 9000 / 6787 |

Các container Odoo/PostgreSQL khác trên máy không tham gia app này.

## 3. Vị trí mã nguồn

App: `development/frappe-bench/apps/social_welfare/`. Các đường dẫn dưới đây tính từ thư mục app:

| Đường dẫn | Trách nhiệm |
|---|---|
| social_welfare/hooks.py | App route, fixtures, hooks quyền và migration |
| social_welfare/permissions.py | Phạm vi reviewer, chặn xóa, trang chủ theo role |
| social_welfare/api.py | Dashboard, lịch sử hộ, hủy hiệu lực có lý do |
| social_welfare/migrations.py | Hook cài đặt/nâng cấp, tạo role từ source và cập nhật quyền |
| social_welfare/patches/v0_1/ | Patch chuyển phân loại cũ, đăng ký trong patches.txt và ghi Patch Log |
| social_welfare/social_welfare/doctype/ | Schema, controller, form JS và test |
| social_welfare/social_welfare/page/an_sinh_xa_hoi/ | Trang chủ nghiệp vụ |
| social_welfare/workspace_sidebar/social_welfare.json | Menu tiếng Việt |
| social_welfare/fixtures/ | Role và workflow |
| social_welfare/translations/vi.csv | Bản dịch thuật ngữ khi dùng ngôn ngữ tiếng Việt |
| social_welfare/tests/test_ward_workflow.py | Test lịch sử, quyền và workflow |

README và các thư mục docs/overrides/images/resources/tests ở gốc chủ yếu thuộc Frappe Docker. Test nghiệp vụ nằm trong app, không phải tests/ ở gốc.

## 4. Dữ liệu và chức năng hiện có

### Công dân và hộ

- Citizen: mã tự sinh CT-000001, định danh, họ tên, ngày sinh, giới tính, điện thoại, quan hệ và liên kết hộ.
- Chuẩn hóa/chặn trùng định danh; cảnh báo khả năng trùng tên/ngày sinh hoặc điện thoại; chặn ngày sinh tương lai.
- Mỗi hộ tối đa một công dân quan hệ Head. Chủ hộ được chọn phải thuộc hộ, không được chuyển hộ khi vẫn là chủ hộ.
- Household: mã tự sinh HH-2026-00001, chủ hộ, địa chỉ, tổ dân phố, số thành viên, thu nhập bình quân và người được giao xác minh.
- Số thành viên tính từ Citizen; thu nhập không âm.
- Household, Citizen, Support Program có cờ lưu trữ. Role nghiệp vụ không được xóa; controller cũng chặn xóa cứng.

### Lịch sử phân loại mới

- DocType **Household Classification** lưu hộ, phân loại, kỳ, khoảng hiệu lực, căn cứ, minh chứng và ghi chú.
- Giữ mã nội bộ Poor Household/Near-poor Household/Normal để tương thích; giao diện diễn giải tiếng Việt.
- Kỳ mới bắt buộc có ngày bắt đầu/kết thúc và căn cứ. Không chấp nhận ngày ngược hoặc khoảng chồng lấn, kể cả ngày biên.
- Khóa hàng Household trong transaction để tuần tự hóa insert các kỳ của cùng hộ.
- Bản đã lưu không được sửa nội dung hoặc xóa. Khi có sai sót, lãnh đạo dùng **Hủy hiệu lực**, bắt buộc lý do; giữ bản gốc, người và thời điểm hủy. Cán bộ tạo bản thay thế sau đó.
- Bản đã hủy không làm căn cứ hiện tại và không chặn kỳ thay thế.
- Phân loại hiện tại được truy vấn theo ngày, không lấy một nhãn cache có thể hết hạn.
- Trường poverty_status cũ được giữ nhưng ẩn và chặn sửa. Patch v0_1 đăng ký ở patches.txt sao chép giá trị cũ sang bản is_legacy=1, không tự gán ngày hiệu lực. Patch được ghi nhận một lần trong Patch Log; không còn quét/chuyển dữ liệu mỗi after_migrate. Hook after_install xử lý trường hợp cài app lần đầu.
- Bản legacy hiển thị **cần rà soát**, không dùng làm căn cứ hiện tại. Trên máy này đã chuyển 3 giá trị cũ thành 3 bản legacy; không tự phân loại mới cho hộ.

### Chương trình và hồ sơ hỗ trợ

- Support Program: mã/tên, mô tả, ngày, mức hỗ trợ, nhóm đối tượng, cờ hoạt động/lưu trữ; kiểm tra số tiền và khoảng ngày.
- Support Application: hộ/chương trình, ngày, số tiền đề nghị/phê duyệt, lý do, kết quả xác minh, ý kiến lãnh đạo và ghi chú chi.
- Mã tự sinh APP-2026-00001, bắt đầu Draft; tiền không âm.
- Ràng buộc cũ một hộ/một hồ sơ/cùng chương trình vẫn còn; chưa phải chống trùng chi theo nhiều đợt.
- Chương trình poor/near_poor kiểm tra **lịch sử hiệu lực tại ngày hồ sơ**, không lấy nhãn legacy. Hiện vẫn là kiểm tra khi lưu, chưa phải Rule Engine ba kết quả.
- Người trình, người/thời điểm quyết định và xác nhận chi do server ghi.
- Server kiểm soát trường được sửa theo vai trò và trạng thái, kể cả khi gọi API trực tiếp.

## 5. Ma trận quyền hiện tại

| Role | Hộ và công dân | Lịch sử phân loại | Chương trình | Hồ sơ hỗ trợ |
|---|---|---|---|---|
| Social Welfare Officer — cán bộ an sinh | Tạo/xem/sửa/lưu trữ; phân công | Xem/thêm kỳ; không sửa/xóa bản đã lưu | Tạo/xem/sửa/lưu trữ | Lập/sửa nháp, bổ sung, chuyển xác minh |
| Social Welfare Reviewer — người xác minh | Chỉ đọc hộ được giao và công dân trong hộ đó | Chỉ đọc hộ được giao | Đọc | Chỉ hộ được giao; ghi xác minh, trình lãnh đạo |
| Social Welfare Manager — lãnh đạo | Đọc | Đọc; hủy hiệu lực có lý do qua thao tác riêng | Đọc | Nhập ý kiến/số tiền tại bước chờ duyệt; quyết định |
| Social Welfare Finance — tài chính | Đọc hộ; không được đọc Citizen | Không có quyền | Đọc | Ghi chú/xác nhận chi sau phê duyệt |

Giữ ID Reviewer/Manager để dùng tài khoản cũ. Administrator có quyền quản trị đặc biệt của Frappe, không dùng để kiểm chứng quyền cán bộ.

Cán bộ chọn **Người được giao xác minh** trên hộ. Chưa giao thì reviewer không thấy hộ/hồ sơ đó. Giới hạn có hiệu lực với list, dashboard và đọc trực tiếp. Role có thể cộng gộp, nhưng người trình vẫn bị chặn tự quyết định hồ sơ mình trình.

Sau migrate, Custom DocPerm của 5 DocType thuộc app được reset để dùng ma trận source. Không chỉ chỉnh quyền thủ công ở một máy; cần sửa source và test.

### Workflow

| Từ | Hành động | Đến | Vai trò |
|---|---|---|---|
| Draft | Submit | Submitted | Cán bộ an sinh |
| Submitted | Start Review | Reviewing | Người xác minh được giao |
| Reviewing | Complete Verification | Pending Approval | Người xác minh; phải có kết quả |
| Pending Approval | Approve | Approved | Lãnh đạo; có ý kiến, không phải người trình |
| Pending Approval | Reject | Rejected | Lãnh đạo; có lý do |
| Pending Approval | Return for Supplement | Returned | Lãnh đạo; có ý kiến bổ sung |
| Returned hoặc Rejected | Reset to Draft | Draft | Cán bộ an sinh |
| Approved | Mark as Paid | Paid | Tài chính; có ghi chú chi |

Tất cả vẫn có docstatus=0. **Paid chỉ là xác nhận trạng thái có người/thời gian**, chưa có chứng từ, giao dịch ngân hàng, Disbursement hay đối soát riêng.

## 6. Giao diện và tài khoản

- Trang chủ: **/desk/an-sinh-xa-hoi**; app roles dùng trang này làm home. Admin có thể mở trực tiếp URL.
- Có nút **Đăng xuất** ở góc trên bên phải trên các màn hình Desk, kể cả trang quản trị. Nút kết thúc phiên phía server và về /login; khi hồ sơ chưa lưu thì hỏi trước khi bỏ thay đổi. Mã dùng chung ở public/js/ward_session.js và public/css/ward_session.css.
- Có số liệu theo quyền, công việc theo vai trò, lối tắt tạo hồ sơ và menu nghiệp vụ tiếng Việt.
- Form hộ nhóm thông tin, có bảng lịch sử và nút Thêm kỳ phân loại. Form lịch sử có hướng dẫn và thao tác Hủy hiệu lực cho lãnh đạo.
- Form hỗ trợ có hướng dẫn bước tiếp theo. Nhãn trường dùng tiếng Việt; giao diện chung Frappe phụ thuộc ngôn ngữ người dùng.
- User trên site: Administrator, officer@example.com, reviewer@example.com, manager@example.com; Guest là tài khoản hệ thống.
- Đã đặt lại và kiểm tra mật khẩu trong phiên hỗ trợ; không ghi mật khẩu vào source/tài liệu.
- Đã có role tài chính, **chưa tự tạo tài khoản tài chính trên site phát triển**. Chưa tự phân công hộ cho reviewer.
- Tài khoản, mật khẩu và dữ liệu không đi theo Git. Máy nhận cần tạo/gán role hoặc restore backup riêng.

## 7. Chạy và nâng cấp môi trường đã có

Mở Docker Desktop, mở repo riêng trong VS Code rồi chọn **Dev Containers: Reopen in Container**. Nếu gặp lỗi workspace nhiều thư mục, dùng New Window → Open Folder, không mở file .code-workspace.

Trong terminal container:

```bash
cd /workspace/development/frappe-bench
bench --site development.localhost backup --with-files
bench --site development.localhost migrate
bench use development.localhost
bench start
```

Không chạy thêm bench start khi tiến trình cũ còn dùng cổng. Migrate có thể mất vài phút vì kiểm tra toàn bộ ERPNext qua bind mount Windows. Sau đổi menu/quyền, refresh cứng hoặc đăng xuất/đăng nhập lại.

Mở **http://development.localhost:8000/desk/an-sinh-xa-hoi**. Giữ Docker/Dev Container mở; cấu hình có shutdownAction=stopCompose.

Bench nền của phiên hỗ trợ trước đã được dừng để người dùng tự chạy bench start trong terminal. File /tmp/erpnext-bench-start.log chỉ là log lần chạy nền trước. Có container trợ giúp **erpnext-local-ports** đưa 8000/9000/6787 ra loopback máy khi không dùng VS Code forward; đây là helper cục bộ, không phải thành phần nghiệp vụ. Dừng helper nếu dùng VS Code forward và bị trùng cổng. Bench chưa được cấu hình tự chạy lại sau restart.

Backup trước nâng cấp nằm trong private/backups của site, tiền tố **20261108_155048-development_localhost**, gồm database, cấu hình và public/private files; không đưa lên Git.

### Máy mới

Clone chưa tạo sẵn Bench, env, site hoặc database. Cài mới từ clone sạch vẫn cần hoàn thiện/kiểm chứng riêng; không bench init đè thư mục đang chứa source app.

Cần Bench dùng Python >=3.14, Frappe/ERPNext version-16; cài package app vào Bench; cấu hình MariaDB/Redis bằng tên service; tạo site/cài app; migrate/build assets khi cần; tạo user/gán role/phân công hộ.

pwd.yml tạo ERPNext demo riêng ở cổng 8080, không cài social_welfare. Shared Dev Container đã bỏ mount .ssh và thư mục Odoo reference của máy cá nhân.

## 8. Kiểm thử đã thực hiện

**16 test đạt** trên site riêng **test_ward.localhost**:

- 7 test cũ: công dân, chủ hộ, số thành viên, mã, định danh, thu nhập/ngày sinh và tạo hồ sơ.
- 9 test mới: kỳ hiệu lực và ngày biên; chồng lấn/ngày/căn cứ sai; lịch sử bất biến và hủy có truy vết; legacy và migration chạy lại; giới hạn reviewer qua list/đọc trực tiếp/dashboard; quyền và chặn xóa; hồ sơ dùng lịch sử hiệu lực; workflow bốn vai trò và giả mạo trường; chống tự phê duyệt khi có nhiều role.
- Test cũ đã chuyển sang IntegrationTestCase tương thích Frappe 16. Ruff check/format đã chạy; JSON và cú pháp JavaScript đã kiểm tra.
- Nút Đăng xuất đã kiểm tra trên trang chủ cán bộ, trang User/Administrator và màn hình 390px: về /login, API bảo vệ trả 403 sau logout; hủy xác nhận khi chưa lưu giữ nguyên phiên.
- Đã kiểm tra browser với đủ 4 vai trò trên site test: home, menu và các thẻ theo quyền; tài chính không thấy Citizen/lịch sử. Đã kiểm tra hai kỳ trên form hộ, form tạo phân loại và màn hình rộng 390px không tràn ngang. Không ghi nhận pageerror trong lần chạy cuối. Trên site phát triển cũng đã mở bằng 3 tài khoản hiện có.

Sau khi chuẩn bị site test đã cài app và bật allow_tests:

```bash
bench --site test_ward.localhost run-tests --app social_welfare --skip-before-tests
```

Không dùng --skip-test-records: phiên bản Frappe này báo deprecated và thoát sớm. Đọc tổng kết OK/FAILED trong log, không chỉ dựa exit code Bench. Không chạy test suite trên site chứa dữ liệu cần giữ.

## 9. Phần còn thiếu theo đề tài

- Nhóm đối tượng chính sách cho hộ/cá nhân.
- Policy/Version/Rule và khóa phiên bản đã dùng.
- Rule Engine ba kết quả, Eligibility Run/Result, snapshot và chi tiết điều kiện.
- Verification độc lập có phân công/hạn/minh chứng; hiện mới phân công theo hộ và ghi chú trên hồ sơ.
- Danh sách trình theo đợt, quyết định/ngoại lệ có lịch sử độc lập; hiện workflow theo từng hồ sơ.
- Disbursement/Benefit, tiền/hiện vật nhiều đợt, thất bại/hủy/đối soát và ràng buộc chống chi trùng.
- Báo cáo thực chi, export mẫu, AI/RAG có nguồn và fallback.
- Test restore backup, cài mới sạch và pin runtime.

Không coi dashboard là báo cáo tài chính, ghi chú là toàn bộ phân hệ xác minh, hoặc track_changes là audit đầy đủ.

## 10. Quy ước phát triển tiếp

- Theo nghiệp vụ tài liệu/Canva, nhưng chỉ dùng ERPNext/MariaDB.
- Sửa trong social_welfare, hạn chế thay core Frappe/ERPNext.
- Giữ lịch sử và căn cứ, không suy diễn hiệu lực/quyền hưởng từ nhãn legacy.
- Backup trước đổi schema/quyền trên site đang dùng; migration phải chạy lại được, test riêng và kiểm tra UI theo role.
- Không commit sites, env, node_modules, logs, database, backup, secret hoặc mật khẩu. .gitignore đã loại runtime.
- Cập nhật tài liệu khi thay cách chạy, nghiệp vụ hoặc mức độ kiểm chứng.

Prompt gợi ý cho Codex: Đọc PROJECT_HANDOFF.md, kiểm tra Git và source social_welfare. Giữ lịch sử phân loại, giới hạn reviewer theo hộ được giao và tách người trình/người duyệt/tài chính. Kiểm thử trên site riêng trước khi áp dụng lên site đang dùng.
