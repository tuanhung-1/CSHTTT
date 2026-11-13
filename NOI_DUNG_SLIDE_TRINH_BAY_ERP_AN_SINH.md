# Nội dung slide: Kiến trúc và thiết kế hệ thống ERP quản lý an sinh xã hội

> **Một file dùng cho buổi trình bày.** Gồm 16 slide chính (khoảng 14–17 phút) và 2 phụ lục. Chép phần **Trên slide** vào PowerPoint; dùng phần **Lời trình bày** làm ghi chú thuyết minh. Thay `[Tên nhóm]`, `[Lớp]` bằng thông tin của nhóm. Mọi số liệu ở ví dụ demo là **giả lập**.

---

## Slide 1 — Trang bìa

**Trên slide**

- **KIẾN TRÚC VÀ THIẾT KẾ HỆ THỐNG ERP QUẢN LÝ AN SINH XÃ HỘI**
- Frappe Framework · ERPNext · Ứng dụng `social_welfare`
- Nhóm: `[Tên nhóm]` · Lớp: `[Lớp]`

**Lời trình bày:** Nội dung hôm nay đi từ nền tảng Frappe/ERPNext, các tầng xử lý và DocType đến cách những thành phần đó phục vụ quy trình an sinh xã hội cấp phường.

---

## Slide 2 — Bài toán và mục tiêu thiết kế

**Trên slide**

- Quản lý thống nhất thông tin hộ, công dân, chính sách và hỗ trợ.
- Theo dõi trách nhiệm của từng vai trò và căn cứ của từng quyết định.
- Kết nối quy trình: **dữ liệu → rà soát → xác minh → phê duyệt → ghi nhận chi → báo cáo**.

**Lời trình bày:** Thiết kế theo hướng ERP giúp các bước sử dụng chung dữ liệu, liên kết hồ sơ với nhau và giữ lịch sử xử lý. Quyết định phê duyệt vẫn do người có thẩm quyền thực hiện.

---

## Slide 3 — Frappe, ERPNext và ứng dụng của nhóm

**Trên slide**

```text
Frappe Framework  (nền tảng ứng dụng)
├── ERPNext         (ứng dụng ERP chuẩn)
└── social_welfare  (ứng dụng an sinh do nhóm phát triển)
```

| Thành phần | Vai trò trong dự án |
|---|---|
| **Frappe** | DocType, form/list, API, quyền truy cập, workflow |
| **ERPNext** | Ứng dụng ERP cài cùng môi trường Bench |
| **social_welfare** | 17 DocType, 4 vai trò và quy trình nghiệp vụ an sinh |

**Lời trình bày:** ERPNext và `social_welfare` là hai app chạy trên Frappe trong cùng Bench. Nhóm xây dựng dữ liệu, giao diện và xử lý nghiệp vụ an sinh trong app `social_welfare`.

---

## Slide 4 — Cấu trúc môi trường `frappe-bench`

**Trên slide**

```text
development/frappe-bench/
├── apps/
│   ├── frappe/            Khung Frappe
│   ├── erpnext/           Ứng dụng ERPNext
│   └── social_welfare/    Mã nguồn của đề tài
├── sites/                 Cấu hình site, tệp tải lên, tài nguyên
├── config/                Cấu hình tiến trình
├── env/                   Môi trường Python
└── logs/                  Nhật ký chạy
```

**Lời trình bày:** Nhóm phát triển chủ yếu trong `apps/social_welfare`. Bản ghi nghiệp vụ nằm ở MariaDB; thư mục `sites` chứa cấu hình và tệp của site. Mã nguồn đưa lên Git tách khỏi dữ liệu vận hành.

---

## Slide 5 — Các tầng xử lý của hệ thống

**Trên slide**

| Tầng logic | Nhiệm vụ | Vị trí tiêu biểu |
|---|---|---|
| **1. Giao diện** | Hiển thị form, nhận thao tác | `page/`, `doctype/*/*.js`, `public/js/` |
| **2. Điểm vào và quyền** | Nhận yêu cầu, kiểm tra người dùng | `frappe.call`, `hooks.py`, `permissions.py` |
| **3. Nghiệp vụ** | Rà soát, xác minh, duyệt, tạo khoản chi | `eligibility.py`, `verification.py`, `bulk.py`, controller `*.py` |
| **4. Dữ liệu** | Định nghĩa và lưu hồ sơ | DocType `*.json`, Frappe ORM, MariaDB |

**Lời trình bày:** Đây là bốn tầng theo chức năng trong cùng hệ thống Frappe. Một tệp Python có thể tham gia nhiều tầng. Frappe cung cấp nền tảng chạy; Redis hỗ trợ bộ nhớ đệm và hàng đợi tác vụ. Các quy tắc quan trọng được kiểm tra ở máy chủ trước khi lưu.

---

## Slide 6 — DocType: thành phần thiết kế dữ liệu của Frappe

**Trên slide**

**DocType** mô tả một loại hồ sơ: trường dữ liệu, kiểu trường, liên kết, quyền và cách hiển thị.

| Ví dụ `Household` | Chức năng |
|---|---|
| `household.json` | Định nghĩa trường, form và quyền cơ bản |
| `household.py` | Kiểm tra dữ liệu khi tạo hoặc sửa hộ |
| `household.js` | Nút, hướng dẫn và tương tác trên biểu mẫu |

**Lời trình bày:** `Household` là một DocType cho hộ gia đình. Trường `assigned_verifier` liên kết đến tài khoản User; controller Python kiểm tra tài khoản được gán có vai trò Người xác minh. Frappe dựa vào định nghĩa DocType để cung cấp biểu mẫu và lưu bản ghi.

---

## Slide 7 — Các nhóm DocType của dự án

**Trên slide**

| Nhóm thiết kế | DocType tiêu biểu |
|---|---|
| Dân cư | `Household`, `Citizen`, `Household Classification` |
| Nhóm và chính sách | `Target Group`, `Target Group Assignment`, `Policy`, `Policy Version`, `Policy Rule` |
| Chương trình và rà soát | `Support Program`, `Eligibility Run`, `Eligibility Result` |
| Xác minh, phê duyệt, chi | `Verification Case`, `Approval Batch`, `Disbursement` |

**Lời trình bày:** Bảng có 14 DocType tiêu biểu. Tổng cộng app định nghĩa **17 DocType**. Hai bảng con là `Eligibility Rule Detail` và `Approval Batch Item`; `Support Application` là luồng hồ sơ đơn lẻ được giữ để tương thích. Cách chia này giúp tách dữ liệu nguồn, căn cứ xét hưởng và kết quả xử lý.

---

## Slide 8 — Các DocType liên kết với nhau như thế nào?

**Trên slide**

```text
Household ──< Citizen; Household ──< Household Classification
Policy ──< Policy Version ──< Policy Rule
Policy Version ──< Support Program ──< Eligibility Run ──< Eligibility Result
Eligibility Result ──→ Verification Case (nếu cần xác minh)
Eligibility Result ──→ Approval Batch Item ──→ Approval Batch ──< Disbursement
```

`──<` = một hồ sơ liên quan nhiều hồ sơ; `──→` = tham chiếu.

**Lời trình bày:** Một chương trình có thể chạy rà soát nhiều lần. Mỗi lần tạo kết quả theo hộ hoặc công dân; kết quả lưu đầu vào và đánh giá điều kiện của thời điểm đó. Đợt trình lấy các kết quả đủ điều kiện, rồi sinh khoản chi sau khi được duyệt. Yêu cầu xác minh cũng có thể được gửi trực tiếp từ hộ hoặc công dân, nên sơ đồ chỉ thể hiện các liên kết chính.

---

## Slide 9 — Hai kiểu trường liên kết cần nhớ

**Trên slide**

| Kiểu trường | Ý nghĩa | Ví dụ |
|---|---|---|
| **Link** | Tham chiếu một hồ sơ khác | `Citizen.household → Household` |
| **Table** | Danh sách dòng con trong một hồ sơ | `Eligibility Result.rule_details → Eligibility Rule Detail` |

- `Approval Batch.items → Approval Batch Item` là một bảng con khác.

**Lời trình bày:** Khi mở file JSON của DocType, có thể thấy `fieldtype` là `Link` hoặc `Table` và `options` chỉ đến DocType liên quan. Đây là cách nhóm mô hình hóa quan hệ dữ liệu trên Frappe.

---

## Slide 10 — Một thao tác đi qua các tầng ra sao?

**Trên slide**

**Ví dụ: bấm “Chạy rà soát hàng loạt” trên Chương trình hỗ trợ**

```text
support_program.js  →  frappe.call()
       ↓
eligibility.py / screen_program(): kiểm tra vai trò, chương trình, chính sách
       ↓
Tính điều kiện → tạo Eligibility Run + Eligibility Result + chi tiết quy tắc
       ↓
Frappe lưu vào MariaDB → giao diện mở lần rà soát mới
```

**Lời trình bày:** Giao diện cho phép cán bộ bắt đầu thao tác; máy chủ kiểm tra quyền và tính kết quả. Mỗi lần chạy tạo hồ sơ mới để giữ lịch sử, không ghi đè kết quả rà soát cũ.

---

## Slide 11 — Phân quyền theo vai trò

**Trên slide**

| Vai trò | Trách nhiệm chính |
|---|---|
| Cán bộ an sinh | Nhập dữ liệu, gửi xác minh, rà soát, lập đợt trình |
| Người xác minh | Xem hộ được giao, ghi kết luận cho yêu cầu được giao |
| Lãnh đạo | Kích hoạt chính sách, duyệt/từ chối/trả lại đợt |
| Tài chính | Xác nhận khoản đã chi và xem báo cáo |

**Lời trình bày:** `hooks.py` đăng ký các hàm quyền, còn `permissions.py` giới hạn danh sách và truy cập trực tiếp theo vai trò. Người trình đợt không được tự duyệt đợt của mình. Không dùng tài khoản Administrator để chứng minh phân quyền nghiệp vụ.

---

## Slide 12 — Phân công hộ và hồ sơ xác minh

**Trên slide**

- `Household.assigned_verifier`: chọn tài khoản Người xác minh cho hộ.
- **Phân công** cho phép người đó xem hộ và nhận yêu cầu liên quan.
- `Verification Case`: yêu cầu xác minh một nội dung cụ thể, có người xử lý, kết luận và căn cứ.
- Sau kết luận, cán bộ cập nhật dữ liệu nguồn hoặc gán nhóm, rồi rà soát lại nếu cần.

**Lời trình bày:** Gán Người xác minh trên hộ chưa tạo ra một kết luận. Người xác minh chỉ ghi kết luận khi cán bộ gửi yêu cầu, chẳng hạn xác minh nhóm đối tượng hoặc địa bàn. Trên form Hộ gia đình hiện chưa có nút kết luận chung cho toàn bộ hộ.

---

## Slide 13 — Từ chính sách đến kết quả rà soát

**Trên slide**

- `Policy → Policy Version → Policy Rule`: lưu căn cứ, hiệu lực và điều kiện xét.
- `Support Program` chọn phiên bản chính sách và ngày chốt xét hưởng.
- `Eligibility Run` tạo `Eligibility Result` theo từng đối tượng.
- Ba kết quả: **Đủ điều kiện · Không đủ điều kiện · Cần xác minh**.

**Lời trình bày:** Ví dụ chương trình hỗ trợ thiên tai xét nhóm đã xác minh, địa bàn và hỗ trợ trùng. Khi thiếu dữ liệu quan trọng, kết quả là “Cần xác minh” và chưa thể vào đợt trình. Sau khi bổ sung dữ liệu, cán bộ chạy lần rà soát mới; lần cũ vẫn được giữ lại.

---

## Slide 14 — Đợt trình, khoản chi và báo cáo

**Trên slide**

```text
Kết quả đủ điều kiện → Approval Batch → Lãnh đạo phê duyệt
                                     ↓
                              Disbursement → Tài chính xác nhận
                                     ↓
                     Báo cáo: đã duyệt · đã chi · chờ chi
```

- Điều chỉnh số tiền hoặc loại dòng khỏi đợt phải có lý do.
- Khoản chi được tạo từ đợt đã phê duyệt.

**Lời trình bày:** Luồng này tách người lập danh sách, người quyết định và người xác nhận chi. “Đã chi” là xác nhận nghiệp vụ trong hệ thống; ứng dụng hiện chưa chuyển tiền qua ngân hàng hoặc đối soát tự động.

---

## Slide 15 — Ví dụ kết quả trên dữ liệu demo

**Trên slide**

| Hộ giả lập | Lần rà soát đầu | Sau xác minh/bổ sung dữ liệu |
|---|---|---|
| Hộ 01 | Đủ điều kiện | Giữ nguyên |
| Hộ 02 | Không đủ điều kiện | Giữ nguyên |
| Hộ 03 | Cần xác minh nhóm | Đủ điều kiện ở lần 2 |
| Hộ 04 | Không đủ điều kiện do ngoài địa bàn | Giữ nguyên |
| Hộ 05 | Cần xác minh địa bàn | Đủ điều kiện ở lần 2 |

**Lời trình bày:** Đây là kịch bản giả lập để minh họa ba trạng thái và việc lưu nhiều lần rà soát. Các hộ 01, 03 và 05 có thể được chọn vào đợt trình sau lần rà soát thứ hai. Số lượng hiển thị trên site có thể khác nếu đã có thêm dữ liệu khác.

---

## Slide 16 — Kết luận và phạm vi hiện tại

**Trên slide**

- Frappe cung cấp nền tảng; `social_welfare` tổ chức nghiệp vụ bằng DocType, API, quyền và giao diện riêng.
- Các tầng xử lý liên kết dữ liệu nguồn với kết quả rà soát, xác minh, quyết định và chi trả.
- Lịch sử được giữ theo kỳ phân loại, lần rà soát, hồ sơ xác minh và đợt trình.
- Hướng phát triển: xác minh tổng thể hộ, đối soát chi trả và tích hợp dữ liệu bên ngoài.

**Lời trình bày:** Điểm mạnh của thiết kế là có thể truy lại một kết quả từ dữ liệu và chính sách được dùng tại thời điểm xử lý. Phạm vi hiện tại là quản lý và ghi nhận quy trình; hệ thống chưa có kết luận chung cho toàn bộ hộ trên form Hộ gia đình hay tích hợp chuyển tiền tự động.

---

## Phụ lục A — Demo nhanh 2–3 phút

1. Mở `household.json`: chỉ ra trường `assigned_verifier` là `Link` đến `User`.
2. Mở `household.py`: chỉ ra bước kiểm tra tài khoản Người xác minh trong `validate_assignment_and_legacy()`.
3. Mở form Hộ gia đình: đối chiếu trường trong mã với màn hình.
4. Mở `support_program.js`: chỉ ra nút **Chạy rà soát hàng loạt** gọi `social_welfare.eligibility.screen_program`.
5. Mở `eligibility.py`, rồi mở **Lần rà soát** trên giao diện để xem ba trạng thái và lý do theo quy tắc.

> Chuẩn bị dữ liệu giả lập theo `HUONG_DAN_DEMO_VA_TEST_TOAN_BO.md`. Không đưa mật khẩu hoặc dữ liệu công dân thật lên slide.

## Phụ lục B — Bản đồ mã nguồn khi giảng viên hỏi

| Nội dung | Vị trí từ `development/frappe-bench/apps/social_welfare/` |
|---|---|
| Định nghĩa DocType và form | `social_welfare/social_welfare/doctype/` |
| Trang tổng quan và báo cáo | `social_welfare/social_welfare/page/` |
| Tài nguyên JS/CSS dùng chung | `social_welfare/public/` |
| API trang tổng quan | `social_welfare/api.py` |
| Rà soát và quy tắc | `social_welfare/eligibility.py` |
| Xác minh | `social_welfare/verification.py` |
| Đợt trình và chi trả | `social_welfare/bulk.py` |
| Phân quyền | `social_welfare/permissions.py` |
| Đăng ký app, quyền, sự kiện | `social_welfare/hooks.py` |

**Nguồn đối chiếu:** mã nguồn `social_welfare`, `HUONG_DAN_DEMO_VA_TEST_TOAN_BO.md` và `LUONG_RA_SOAT_HANG_LOAT.md`.
