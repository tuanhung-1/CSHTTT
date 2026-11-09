# Kịch bản demo và kiểm thử toàn bộ ứng dụng An sinh xã hội phường

Tài liệu này dùng để:

- demo chức năng trước giảng viên;
- giúp thành viên nhóm nhập một bộ dữ liệu thống nhất;
- kiểm tra luồng xuyên suốt từ dữ liệu dân cư đến rà soát, xác minh, phê duyệt, chi trả và báo cáo;
- kiểm tra phân quyền của bốn vai trò nghiệp vụ.

Toàn bộ tên người, địa chỉ, căn cứ và mã trong tài liệu là **dữ liệu giả lập**. Không dùng để ra quyết định hoặc chi trả thực tế.

Ứng dụng sử dụng **ERPNext/Frappe và MariaDB**. Dữ liệu nằm trong database của từng site, không tự đi theo Git.

Kịch bản dưới đây dùng ngày demo `2026-11-09`. Yêu cầu xác minh gửi trực tiếp từ hộ lấy ngày hiện tại làm ngày cần xác minh. Nếu chạy vào ngày khác, hãy thay **ngày chốt chương trình bằng ngày chạy demo** và điều chỉnh toàn bộ khoảng hiệu lực chính sách, chương trình, phân loại, kết luận và gán nhóm để cùng bao phủ ngày đó. Nếu không đồng bộ ngày, kết luận âm về nhóm có thể không áp dụng cho lần rà soát.

---

## 1. Phạm vi chức năng được kiểm tra

| Phân hệ | Nội dung kiểm tra |
|---|---|
| Hộ gia đình | Tạo hộ, giao người xác minh, cập nhật địa bàn, lưu lịch sử |
| Công dân | Tạo chủ hộ và thành viên, tự tính số thành viên, liên kết chủ hộ |
| Phân loại hộ | Tạo kỳ phân loại có hiệu lực, chống chồng lấn, giữ lịch sử |
| Nhóm đối tượng | Tạo danh mục nhóm; chỉ gán nhóm mới sau khi có kết luận xác minh |
| Hồ sơ xác minh | Officer gửi yêu cầu; Reviewer được giao ghi kết luận và căn cứ |
| Chính sách | Tạo chính sách, phiên bản, quy tắc; Manager kích hoạt phiên bản |
| Chương trình hỗ trợ | Chọn đối tượng, chính sách, ngày chốt, hình thức và mức hỗ trợ |
| Rà soát hàng loạt | Quét đối tượng, sinh ba kết quả và giải thích từng điều kiện |
| Đợt trình duyệt | Chọn đối tượng đủ điều kiện, điều chỉnh có lý do, trình lãnh đạo |
| Phê duyệt | Manager phê duyệt, từ chối hoặc yêu cầu bổ sung cả đợt |
| Chi trả | Tạo khoản chi sau phê duyệt; Finance xác nhận đã chi |
| Báo cáo tài chính | Tổng đã duyệt, đã chi, chờ chi và số liệu theo chương trình/tháng |
| Hồ sơ đơn lẻ cũ | Kiểm tra workflow cũ từ Draft đến Paid để bảo đảm tương thích |
| Phân quyền | Menu, danh sách, nút thao tác và truy cập trực tiếp theo vai trò |

Luồng chính để demo là:

`Dữ liệu dân cư → Xác minh → Gán nhóm → Chính sách → Chương trình → Rà soát → Xác minh bổ sung → Rà soát lại → Đợt trình → Phê duyệt → Chi trả → Báo cáo`

---

## 2. Chuẩn bị môi trường

### 2.1. Sau khi pull code

Trong terminal **bên trong container**, tại `/workspace/development/frappe-bench`:

```bash
bench --site development.localhost backup --with-files
bench --site development.localhost migrate
bench build --app social_welfare
bench --site development.localhost clear-cache
bench use development.localhost
bench start
```

Nếu `bench start` báo cổng `8000` đã được dùng, không chạy thêm tiến trình. Kiểm tra tiến trình hiện có hoặc mở thẳng:

`http://development.localhost:8000/desk/an-sinh-xa-hoi`

Sau `migrate`, đăng xuất, đăng nhập lại và nhấn `Ctrl + Shift + R`.

### 2.2. Tài khoản

Mỗi người tự tạo tài khoản trên site của mình. Không ghi mật khẩu vào Git hoặc tài liệu.

| Tài khoản gợi ý | Role duy nhất cần gán | Vai trò trong demo |
|---|---|---|
| `officer@example.com` | `Social Welfare Officer` | Cán bộ an sinh nhập dữ liệu, gửi xác minh, rà soát và trình |
| `reviewer@example.com` | `Social Welfare Reviewer` | Người xác minh các hộ được giao |
| `manager@example.com` | `Social Welfare Manager` | Lãnh đạo kích hoạt chính sách và quyết định đợt trình |
| `finance@example.com` | `Social Welfare Finance` | Cán bộ tài chính xác nhận chi và xem báo cáo |

Không dùng `Administrator` để chứng minh phân quyền. Administrator có quyền đặc biệt của Frappe.

### 2.3. Quy ước mã dữ liệu demo

Trước khi nhập, tìm mã trong danh sách tương ứng. Nếu mã đã tồn tại từ lần demo trước, thay hậu tố `2026` bằng `2026-R2` cho **toàn bộ mã có liên quan**.

| Loại dữ liệu | Mã dùng trong kịch bản |
|---|---|
| Nhóm đối tượng | `DEMO_DISASTER_AFFECTED` |
| Chính sách | `DEMO-POLICY-DISASTER-2026` |
| Chương trình hàng loạt | `DEMO-FULL-HH-2026` |
| Chương trình đơn lẻ cũ | `DEMO-LEGACY-POOR-2026` |
| Hộ gia đình | `DEMO-HH-01` đến `DEMO-HH-06` |
| Công dân | Để hệ thống tự sinh mã hoặc dùng `DEMO-CT-01` đến `DEMO-CT-06` |

Tạo một bảng ghi kết quả khi demo:

| Dữ liệu | Mã thực tế được tạo |
|---|---|
| Policy Version | `PV-_____` |
| Lần rà soát 1 | `ER-_____` |
| Lần rà soát 2 | `ER-_____` |
| Đợt trình | `AB-_____` |
| Hồ sơ xác minh của hộ 03 | `VC-_____` |
| Hồ sơ xác minh địa bàn hộ 05 | `VC-_____` |

---

## 3. Bộ dữ liệu hộ và kết quả mong đợi

Năm hộ đầu dùng cho luồng rà soát hàng loạt. Hộ thứ sáu dùng cho workflow đơn lẻ cũ.

| Mã hộ | Chủ hộ giả lập | Tổ dân phố ban đầu | Nhóm tại lần rà soát 1 | Kết quả lần 1 | Xử lý giữa hai lần | Kết quả lần 2 |
|---|---|---|---|---|---|---|
| `DEMO-HH-01` | Nguyễn Minh An | `Tổ 01` | Đã xác nhận và gán | Đủ điều kiện | Không đổi | Đủ điều kiện |
| `DEMO-HH-02` | Trần Thị Bình | `Tổ 01` | Reviewer xác nhận **không thuộc nhóm** | Không đủ điều kiện | Không đổi | Không đủ điều kiện |
| `DEMO-HH-03` | Lê Văn Cường | `Tổ 02` | Chưa có dữ liệu | Cần xác minh | Xác nhận và gán nhóm | Đủ điều kiện |
| `DEMO-HH-04` | Phạm Thị Dung | `Tổ 03` | Đã xác nhận và gán | Không đủ điều kiện | Không đổi | Không đủ điều kiện |
| `DEMO-HH-05` | Võ Văn Em | Để trống | Đã xác nhận và gán | Cần xác minh | Xác minh địa bàn, cập nhật `Tổ 02` | Đủ điều kiện |
| `DEMO-HH-06` | Đặng Thị Phương | `Tổ 01` | Không cần cho luồng cũ | Không tham gia chương trình chính | Tạo phân loại Hộ nghèo | Dùng cho hồ sơ đơn lẻ |

Lưu ý: rà soát hàng loạt xét **toàn bộ hộ chưa lưu trữ trên site**, không chỉ năm hộ demo. Khi kiểm tra, dùng ô tìm kiếm để lọc các mã bắt đầu bằng `DEMO-HH-`.

---

## 4. Giai đoạn A — Nhập dữ liệu dân cư

Thực hiện bằng tài khoản **Officer**.

### 4.1. Tạo sáu hộ gia đình

Vào **Hộ gia đình → Add Household**. Với mỗi hộ, nhập:

| Trường | HH-01 | HH-02 | HH-03 | HH-04 | HH-05 | HH-06 |
|---|---|---|---|---|---|---|
| Mã hộ gia đình | `DEMO-HH-01` | `DEMO-HH-02` | `DEMO-HH-03` | `DEMO-HH-04` | `DEMO-HH-05` | `DEMO-HH-06` |
| Họ tên chủ hộ | Nguyễn Minh An | Trần Thị Bình | Lê Văn Cường | Phạm Thị Dung | Võ Văn Em | Đặng Thị Phương |
| Tổ dân phố | `Tổ 01` | `Tổ 01` | `Tổ 02` | `Tổ 03` | Để trống | `Tổ 01` |
| Địa chỉ | `01 Đường Demo, phường Minh An` | `02 Đường Demo, phường Minh An` | `03 Đường Demo, phường Minh An` | `04 Đường Demo, phường Minh An` | Để trống | `06 Đường Demo, phường Minh An` |
| Thu nhập bình quân | `800000` | `900000` | `850000` | `950000` | `700000` | `650000` |
| Người được giao xác minh | `reviewer@example.com` | `reviewer@example.com` | `reviewer@example.com` | `reviewer@example.com` | `reviewer@example.com` | `reviewer@example.com` |
| Đã lưu trữ | Không chọn | Không chọn | Không chọn | Không chọn | Không chọn | Không chọn |

Ở bước tạo hộ, để trống **Công dân làm chủ hộ**. Lưu hộ trước rồi mới thêm công dân.

Kết quả mong đợi:

- hộ lưu thành công;
- số thành viên ban đầu bằng `0`;
- Reviewer được giao hợp lệ;
- Reviewer khác không được thấy hộ nếu không được giao.

### 4.2. Tạo công dân làm chủ hộ

Mở từng hộ và bấm **Thêm công dân vào hộ**.

| Hộ | Họ và tên | Ngày sinh | Giới tính | Quan hệ với chủ hộ |
|---|---|---|---|---|
| `DEMO-HH-01` | Nguyễn Minh An | `1980-03-15` | Nam | Chủ hộ |
| `DEMO-HH-02` | Trần Thị Bình | `1982-07-20` | Nữ | Chủ hộ |
| `DEMO-HH-03` | Lê Văn Cường | `1978-11-10` | Nam | Chủ hộ |
| `DEMO-HH-04` | Phạm Thị Dung | `1985-01-25` | Nữ | Chủ hộ |
| `DEMO-HH-05` | Võ Văn Em | `1975-09-05` | Nam | Chủ hộ |
| `DEMO-HH-06` | Đặng Thị Phương | `1984-06-18` | Nữ | Chủ hộ |

Các trường khác:

| Trường | Cách nhập |
|---|---|
| Mã công dân | Để trống cho hệ thống tự sinh |
| Số định danh / CCCD | Để trống; không dùng CCCD thật |
| Số điện thoại | Để trống hoặc dùng số giả lập |
| Hộ gia đình | Nút từ hộ sẽ điền sẵn |
| Đã lưu trữ | Không chọn |

Sau khi lưu, mở lại hộ. Kết quả mong đợi:

- số thành viên bằng `1`;
- công dân được liên kết làm chủ hộ;
- tên chủ hộ đồng bộ;
- một hộ không thể có hai công dân cùng quan hệ Chủ hộ.

Để demo số thành viên, thêm một thành viên vào `DEMO-HH-01`:

| Trường | Dữ liệu |
|---|---|
| Họ và tên | Nguyễn Thị Lan |
| Ngày sinh | `1983-08-22` |
| Giới tính | Nữ |
| Quan hệ với chủ hộ | Vợ/chồng |
| Hộ gia đình | `DEMO-HH-01` |

Kết quả mong đợi: số thành viên của `DEMO-HH-01` bằng `2`.

### 4.3. Tạo kỳ phân loại hộ cho `DEMO-HH-06`

Mở `DEMO-HH-06` → **Thêm kỳ phân loại**.

| Trường | Dữ liệu |
|---|---|
| Hộ gia đình | `DEMO-HH-06` |
| Phân loại | Hộ nghèo (`Poor Household`) |
| Kỳ phân loại | `DEMO-2026` |
| Hiệu lực từ | `2026-01-01` |
| Hiệu lực đến | `2026-12-31` |
| Căn cứ phân loại | `Biên bản rà soát hộ nghèo DEMO số 06/2026` |
| Tệp minh chứng | Có thể để trống khi demo |
| Ghi chú | `Dữ liệu giả lập phục vụ kiểm thử` |

Kết quả mong đợi:

- kỳ phân loại xuất hiện trong lịch sử hộ;
- bản đã lưu không sửa/xóa trực tiếp;
- thử tạo thêm một kỳ cùng hộ từ `2026-06-01` đến `2026-12-31` phải bị chặn vì chồng lấn.

---

## 5. Giai đoạn B — Danh mục nhóm và xác minh trước rà soát

### 5.1. Tạo danh mục nhóm đối tượng

Officer vào **Danh mục nhóm đối tượng → Add Target Group**.

| Trường | Dữ liệu |
|---|---|
| Mã nhóm | `DEMO_DISASTER_AFFECTED` |
| Tên nhóm đối tượng | `DEMO Hộ bị ảnh hưởng thiên tai` |
| Mô tả | `Nhóm giả lập phục vụ demo quy trình xác minh và hỗ trợ` |
| Đang áp dụng | Chọn |

Danh mục nhóm chỉ định nghĩa tên nhóm; nó không tự chứng minh hộ thuộc nhóm.

### 5.2. Gửi yêu cầu xác minh trực tiếp từ hộ

Với `DEMO-HH-01`, `DEMO-HH-02`, `DEMO-HH-04`, `DEMO-HH-05`:

1. Officer mở hộ.
2. Tại **Nhóm đối tượng chính sách của hộ**, bấm **Gửi xác minh nhóm**.
3. Chọn nhóm `DEMO_DISASTER_AFFECTED`.
4. Nhập lý do: `Đối chiếu biên bản khảo sát ảnh hưởng thiên tai phục vụ DEMO ngày 09/11/2026`.
5. Bấm **Gửi cho người xác minh**.

Kết quả mong đợi: mỗi hộ có một `Verification Case` ở trạng thái **Chờ xác minh**, được giao cho `reviewer@example.com`.

### 5.3. Reviewer ghi kết luận

Đăng nhập **Reviewer** → **Hồ sơ xác minh**. Reviewer chỉ thấy yêu cầu được giao.

#### Hộ 01, 04 và 05 — xác nhận thuộc nhóm

Mở từng hồ sơ và bấm **Ghi kết luận xác minh**:

| Trường | Dữ liệu |
|---|---|
| Kết luận | Xác nhận có căn cứ (`CONFIRMED`) |
| Nhóm được xác minh từ ngày | `2026-01-01` |
| Nhóm được xác minh đến ngày | `2026-12-31` |
| Nội dung kết luận | `Đã đối chiếu biên bản khảo sát DEMO; hộ có ghi nhận ảnh hưởng thiên tai.` |
| Căn cứ xác minh | `Biên bản khảo sát DEMO-BB-2026, dữ liệu giả lập` |
| Tệp minh chứng riêng tư | Có thể để trống; nếu tải thì chọn tệp riêng tư do Reviewer tải lên |

#### Hộ 02 — xác nhận không thuộc nhóm

| Trường | Dữ liệu |
|---|---|
| Kết luận | Xác nhận không thuộc / không đúng (`NOT_CONFIRMED`) |
| Ngày hiệu lực | Để trống |
| Nội dung kết luận | `Không tìm thấy căn cứ xác nhận hộ bị ảnh hưởng thiên tai tại ngày chốt.` |
| Căn cứ xác minh | `Đối chiếu biên bản DEMO-BB-2026 và danh sách khảo sát giả lập` |

Kết quả mong đợi:

- trạng thái hồ sơ thành **Đã hoàn tất**;
- hệ thống ghi người và thời điểm kết luận;
- kết luận không sửa trực tiếp;
- Reviewer không thể kết luận hồ sơ được giao cho người khác.

### 5.4. Officer gán nhóm đã xác minh

Đăng nhập lại Officer. Với hộ 01, 04 và 05:

1. Mở hộ → **Gán nhóm đã xác minh**.
2. Chọn đúng `Hồ sơ xác minh` vừa hoàn tất.
3. Hệ thống điền nhóm và khoảng hiệu lực.
4. Kiểm tra:
   - Nhóm: `DEMO_DISASTER_AFFECTED`;
   - Hiệu lực từ: `2026-01-01`;
   - Hiệu lực đến: `2026-12-31`.
5. Lưu.

Không gán nhóm cho hộ 02. Không xử lý hộ 03 ở giai đoạn này.

Kết quả mong đợi:

- bản gán nhóm dẫn chiếu hồ sơ xác minh;
- không thể dùng hồ sơ của hộ khác;
- không thể mở rộng ngày hiệu lực ngoài thời gian Reviewer xác nhận;
- lịch sử gán nhóm đã lưu không sửa/xóa trực tiếp.

---

## 6. Giai đoạn C — Tạo chính sách và quy tắc

### 6.1. Tạo chính sách

Officer vào **Chính sách → Add Policy**.

| Trường | Dữ liệu |
|---|---|
| Mã chính sách | `DEMO-POLICY-DISASTER-2026` |
| Tên chính sách | `DEMO Chính sách hỗ trợ hộ ảnh hưởng thiên tai 2026` |
| Nội dung chính sách | `Chính sách giả lập dùng để demo hệ thống, không phải văn bản pháp lý` |
| Loại đối tượng | Hộ gia đình |
| Đang áp dụng | Chọn |

### 6.2. Tạo phiên bản chính sách

Officer vào **Phiên bản chính sách → Add Policy Version**.

| Trường | Dữ liệu |
|---|---|
| Chính sách | `DEMO-POLICY-DISASTER-2026` |
| Số phiên bản | `1` |
| Hiệu lực từ | `2026-01-01` |
| Hiệu lực đến | `2026-12-31` |
| Căn cứ pháp lý | `DEMO-VB-01/2026 - văn bản giả lập` |
| Văn bản chính sách | Có thể để trống |
| Trạng thái | Bản nháp (`DRAFT`) |

Lưu và ghi lại mã `PV-_____`.

### 6.3. Tạo ba quy tắc

Khi phiên bản còn **Bản nháp**, Officer tạo ba `Policy Rule`:

| Trường | Quy tắc 1 | Quy tắc 2 | Quy tắc 3 |
|---|---|---|---|
| Phiên bản chính sách | `PV-_____` | `PV-_____` | `PV-_____` |
| Mã điều kiện | `DEMO-AFFECTED` | `DEMO-AREA` | `DEMO-NO-DUP` |
| Tên điều kiện | Có ghi nhận ảnh hưởng thiên tai | Thuộc địa bàn hỗ trợ | Chưa nhận hỗ trợ trùng |
| Loại điều kiện | Nhóm đối tượng | Địa bàn cư trú | Khoản hỗ trợ trước đó |
| Phép kiểm tra | Bằng (`EQ`) | Thuộc một trong (`IN`) | Không có dữ liệu (`NOT_EXISTS`) |
| Giá trị yêu cầu | `DEMO_DISASTER_AFFECTED` | `Tổ 01,Tổ 02` | Để trống |
| Khi thiếu dữ liệu | Cần xác minh | Cần xác minh | Cần xác minh |
| Thứ tự kiểm tra | `10` | `20` | `30` |
| Bắt buộc | Chọn | Chọn | Chọn |
| Giải thích | `Đối chiếu nhóm đã xác minh` | `Phạm vi DEMO gồm Tổ 01 và Tổ 02` | `Không hỗ trợ trùng trong cùng chương trình` |

Ý nghĩa nhanh:

| Mã | Nghĩa nghiệp vụ |
|---|---|
| `EQ` | Giá trị thực tế phải bằng giá trị yêu cầu |
| `IN` | Giá trị thực tế phải thuộc một trong các giá trị ngăn cách bằng dấu phẩy |
| `NOT_EXISTS` | Không được có bản ghi/khoản hỗ trợ trước đó |
| `NEED_VERIFICATION` | Nếu thiếu dữ liệu thì đưa vào hàng đợi xác minh |

### 6.4. Manager kích hoạt phiên bản

Đăng nhập Manager, mở `PV-_____`, đổi trạng thái từ **Bản nháp** sang **Đang hiệu lực** và lưu.

Kết quả mong đợi:

- hệ thống tự ghi người và thời điểm phê duyệt;
- phiên bản cần ít nhất một quy tắc mới được kích hoạt;
- chỉ Manager hoặc Administrator được kích hoạt;
- quy tắc của phiên bản đã kích hoạt không sửa được;
- muốn thay chính sách phải tạo phiên bản mới.

---

## 7. Giai đoạn D — Tạo chương trình hỗ trợ

Officer vào **Chương trình hỗ trợ → Add Support Program**.

| Trường | Dữ liệu |
|---|---|
| Mã chương trình | `DEMO-FULL-HH-2026` |
| Tên chương trình | `DEMO Hỗ trợ hộ ảnh hưởng thiên tai 2026` |
| Mô tả | `Chương trình giả lập để demo toàn bộ luồng nghiệp vụ` |
| Đối tượng nhận hỗ trợ | Hộ gia đình |
| Nhóm hộ tương thích dữ liệu cũ | Ảnh hưởng thiên tai (`disaster`) |
| Phiên bản chính sách | `PV-_____` đã kích hoạt |
| Ngày chốt xét hưởng | `2026-11-09` |
| Ngày bắt đầu | `2026-01-01` |
| Ngày kết thúc | `2026-12-31` |
| Hình thức hỗ trợ | Hỗ trợ tiền |
| Mức hỗ trợ | `2000000` |
| Ngân sách dự kiến | `10000000` |
| Đang triển khai | Chọn |
| Đã lưu trữ | Không chọn |

Kết quả mong đợi: đầu trang thể hiện bước **Cấu hình** và nút **Chạy rà soát hàng loạt**.

---

## 8. Giai đoạn E — Lần rà soát thứ nhất

### 8.1. Chạy rà soát

Officer mở chương trình `DEMO-FULL-HH-2026` và bấm **Chạy rà soát hàng loạt**.

Hệ thống tạo một `Eligibility Run`. Ghi lại mã `ER-_____`.

### 8.2. Kiểm tra màn hình lần rà soát

Màn hình phải có:

- tiến độ năm bước;
- bốn ô: tổng đã rà soát, đủ điều kiện, cần xác minh, không đủ điều kiện;
- bộ lọc ba kết quả;
- ô tìm kiếm;
- lý do tiếng Việt trên từng dòng;
- nút **Xem lý do**;
- ô chọn chỉ xuất hiện trên dòng đủ điều kiện.

Tìm từng mã `DEMO-HH-` và đối chiếu:

| Hộ | Kết quả mong đợi | Lý do chính |
|---|---|---|
| `DEMO-HH-01` | Đủ điều kiện | Có nhóm hợp lệ, thuộc Tổ 01, chưa hỗ trợ trùng |
| `DEMO-HH-02` | Không đủ điều kiện | Reviewer đã xác minh không thuộc nhóm tại ngày chốt |
| `DEMO-HH-03` | Cần xác minh | Chưa có dữ liệu nhóm và chưa có kết luận âm |
| `DEMO-HH-04` | Không đủ điều kiện | Có nhóm nhưng Tổ 03 ngoài phạm vi |
| `DEMO-HH-05` | Cần xác minh | Có nhóm nhưng thiếu địa bàn/địa chỉ |

Mở chi tiết từng kết quả. Kiểm tra bảng:

`Điều kiện → Dữ liệu ghi nhận → Yêu cầu → Đánh giá → Giải thích`

Kết quả cũ là ảnh chụp nghiệp vụ tại ngày chốt; không sửa trực tiếp.

---

## 9. Giai đoạn F — Xử lý các dòng cần xác minh

### 9.1. Hộ 03 — xác minh nhóm từ kết quả rà soát

Officer mở kết quả của `DEMO-HH-03`:

1. Bấm **Gửi yêu cầu xác minh**.
2. Nội dung cần xác minh: **Nhóm đối tượng**.
3. Nhóm: `DEMO_DISASTER_AFFECTED`.
4. Vấn đề cần đối chiếu: `Hộ chưa có dữ liệu nhóm tại ngày chốt; đề nghị đối chiếu biên bản khảo sát DEMO.`
5. Gửi.

Reviewer mở hồ sơ được giao và kết luận:

| Trường | Dữ liệu |
|---|---|
| Kết luận | Xác nhận có căn cứ |
| Từ ngày | `2026-01-01` |
| Đến ngày | `2026-12-31` |
| Nội dung | `Hộ có tên trong biên bản khảo sát ảnh hưởng thiên tai DEMO.` |
| Căn cứ | `Biên bản DEMO-BB-2026, dòng số 03` |

Officer quay lại `DEMO-HH-03` → **Gán nhóm đã xác minh** → chọn hồ sơ vừa hoàn tất → lưu.

### 9.2. Hộ 05 — xác minh địa bàn

Officer mở kết quả của `DEMO-HH-05`:

1. Bấm **Gửi yêu cầu xác minh**.
2. Nội dung cần xác minh: **Địa bàn cư trú**.
3. Không chọn nhóm đối tượng.
4. Vấn đề cần đối chiếu: `Hồ sơ đang thiếu tổ dân phố và địa chỉ tại ngày chốt.`

Reviewer kết luận:

| Trường | Dữ liệu |
|---|---|
| Kết luận | Xác nhận có căn cứ |
| Giá trị đã xác minh | `Tổ 02` |
| Nội dung | `Qua đối chiếu sổ cư trú DEMO, hộ thuộc Tổ 02.` |
| Căn cứ | `Sổ cư trú DEMO-SCT-02/2026` |

Officer mở `DEMO-HH-05` và cập nhật dữ liệu nguồn:

| Trường | Dữ liệu |
|---|---|
| Tổ dân phố | `Tổ 02` |
| Địa chỉ | `05 Đường Demo, phường Minh An` |

Kết quả mong đợi:

- hồ sơ xác minh hoàn tất vẫn liên kết với kết quả rà soát thứ nhất;
- kết quả rà soát thứ nhất vẫn là **Cần xác minh**;
- dữ liệu nguồn đã sẵn sàng cho một lần rà soát mới.

---

## 10. Giai đoạn G — Rà soát lại

Officer quay lại chương trình và bấm **Chạy rà soát hàng loạt** lần nữa. Ghi lại mã `ER-_____` mới.

Lọc các mã demo:

| Hộ | Kết quả lần 2 mong đợi |
|---|---|
| `DEMO-HH-01` | Đủ điều kiện |
| `DEMO-HH-02` | Không đủ điều kiện |
| `DEMO-HH-03` | Đủ điều kiện |
| `DEMO-HH-04` | Không đủ điều kiện |
| `DEMO-HH-05` | Đủ điều kiện |

Kiểm tra lịch sử:

- lần rà soát 1 vẫn tồn tại;
- lần rà soát 2 có dữ liệu mới;
- một đối tượng có thể có kết quả khác nhau giữa hai lần vì dữ liệu nguồn đã được bổ sung;
- không có thao tác sửa kết quả cũ.

---

## 11. Giai đoạn H — Lập và trình đợt

### 11.1. Tạo đợt trình

Trong lần rà soát thứ hai:

1. Lọc **Đủ điều kiện**.
2. Tích `DEMO-HH-01`, `DEMO-HH-03`, `DEMO-HH-05`.
3. Bấm **Lập đợt trình (3 đã chọn)**.
4. Ghi lại mã `AB-_____`.

Đợt mới phải có:

- trạng thái **Bản nháp**;
- 3 đối tượng;
- 2.000.000 đồng mỗi hộ;
- tổng đề xuất 6.000.000 đồng;
- liên kết về lần rà soát gốc.

### 11.2. Kiểm tra thay đổi có lý do

Để demo kiểm soát thay đổi, sửa dòng `DEMO-HH-05`:

| Trường | Dữ liệu |
|---|---|
| Số tiền đề xuất | `1500000` |
| Lý do thay đổi | `Điều chỉnh mức đề xuất theo biên bản DEMO của đợt trình` |

Lưu. Tổng tiền phải thành `5.500.000 ₫`.

Có thể demo nhánh loại dòng bằng cách chọn **Đã loại khỏi đợt**; hệ thống bắt nhập lý do. Sau khi minh họa, đưa lại **Được chọn**, nhập một lý do mới và lưu.

### 11.3. Trình lãnh đạo

Officer bấm **Trình lãnh đạo**.

Kết quả mong đợi:

- trạng thái **Đã trình lãnh đạo**;
- hệ thống ghi cán bộ và thời điểm trình;
- danh sách bị khóa;
- cùng một kết quả đủ điều kiện không được đưa vào một đợt đang trình/đã duyệt khác.

---

## 12. Giai đoạn I — Lãnh đạo quyết định

Đăng nhập Manager → **Đợt trình duyệt** → mở `AB-_____`.

### Nhánh chính dùng khi demo

1. Kiểm tra chương trình, lần rà soát, danh sách và tổng tiền.
2. Bấm **Phê duyệt đợt**.
3. Ý kiến: `Đồng ý phê duyệt danh sách và mức hỗ trợ theo kết quả rà soát, xác minh và biên bản DEMO.`
4. Xác nhận.

Kết quả mong đợi:

- đợt thành **Đã phê duyệt**;
- tự sinh một `Disbursement` trạng thái **Chờ chi** cho mỗi dòng được chọn;
- người trình không được tự phê duyệt nếu có nhiều role.

### Hai nhánh phụ nên giải thích cho giảng viên

| Quyết định | Kết quả |
|---|---|
| Yêu cầu bổ sung | Đợt thành `RETURNED`; Officer đưa về nháp, bổ sung rồi trình lại |
| Từ chối đợt | Đợt thành `REJECTED`; không tạo khoản chi |

Để giữ một vòng demo hoàn chỉnh, chọn **Phê duyệt đợt**.

---

## 13. Giai đoạn J — Xác nhận chi trả

Đăng nhập Finance → **Khoản chi**. Lọc theo `Đợt phê duyệt = AB-_____`.

Mở từng khoản **Chờ chi** và bấm **Xác nhận đã chi**:

| Trường | Dữ liệu mẫu |
|---|---|
| Ghi chú xác nhận chi | `Đã đối chiếu danh sách được duyệt và ghi nhận chi trả trong buổi DEMO ngày 09/11/2026.` |
| Tệp biên nhận | Có thể để trống hoặc dùng tệp giả lập |

Nên xác nhận hai khoản trước, mở báo cáo để cho thấy cả **Đã chi** và **Chờ chi**. Sau đó xác nhận khoản cuối để kết thúc vòng.

Kết quả mong đợi:

- trạng thái khoản chuyển từ **Chờ chi** sang **Đã chi**;
- hệ thống ghi người và thời điểm xác nhận;
- Officer/Manager chỉ đọc khoản chi;
- thao tác là ghi nhận nghiệp vụ, không tự chuyển tiền ngân hàng.

---

## 14. Giai đoạn K — Báo cáo tài chính

Đăng nhập Finance hoặc Manager → **Báo cáo tài chính**.

Kiểm tra:

| Nội dung | Kết quả mong đợi |
|---|---|
| Đã duyệt | Tổng hỗ trợ tiền của các đợt đã được phê duyệt |
| Đã chi | Chỉ cộng khoản Finance đã xác nhận |
| Chờ chi | Khoản đã sinh nhưng chưa xác nhận |
| Theo tháng | Khoản đã chi được nhóm theo tháng xác nhận |
| Theo chương trình | Có dòng `DEMO Hỗ trợ hộ ảnh hưởng thiên tai 2026` |

Nếu xác nhận 2/3 khoản, báo cáo phải thể hiện đồng thời tiền đã chi và tiền chờ chi. Bấm **Làm mới** sau mỗi thay đổi.

---

## 15. Giai đoạn L — Kiểm tra workflow hồ sơ đơn lẻ cũ

Đây là luồng tương thích dữ liệu cũ, tách khỏi `Eligibility Run → Approval Batch → Disbursement`. Trạng thái `Paid` của luồng cũ không được cộng vào báo cáo tài chính mới.

### 15.1. Tạo chương trình đơn lẻ

Officer tạo chương trình:

| Trường | Dữ liệu |
|---|---|
| Mã chương trình | `DEMO-LEGACY-POOR-2026` |
| Tên chương trình | `DEMO Hồ sơ đơn lẻ hộ nghèo 2026` |
| Đối tượng | Hộ gia đình |
| Nhóm hộ | Hộ nghèo (`poor`) |
| Ngày bắt đầu / kết thúc | `2026-01-01` / `2026-12-31` |
| Ngày chốt | `2026-11-09` |
| Hình thức | Hỗ trợ tiền |
| Mức hỗ trợ | `1000000` |
| Đang triển khai | Chọn |

Luồng đơn lẻ không cần chạy rà soát hàng loạt cho phần test này.

### 15.2. Tạo hồ sơ hỗ trợ

Officer vào **Hồ sơ hỗ trợ đơn lẻ → Add Support Application**:

| Trường | Dữ liệu |
|---|---|
| Mã hồ sơ | Để trống |
| Đối tượng | Hộ gia đình |
| Hộ | `DEMO-HH-06` |
| Chương trình | `DEMO-LEGACY-POOR-2026` |
| Ngày hồ sơ | `2026-11-09` |
| Số tiền đề nghị | `1000000` |
| Lý do đề nghị | `Đề nghị hỗ trợ hộ nghèo theo dữ liệu DEMO` |

Lưu rồi thực hiện workflow:

| Vai trò | Trạng thái trước | Thao tác và dữ liệu | Trạng thái sau |
|---|---|---|---|
| Officer | Nháp | `Submit` | Đã tiếp nhận |
| Reviewer | Đã tiếp nhận | `Start Review` | Đang xác minh |
| Reviewer | Đang xác minh | Nhập kết quả: `Đã đối chiếu kỳ phân loại DEMO-2026`; `Complete Verification` | Chờ lãnh đạo duyệt |
| Manager | Chờ lãnh đạo duyệt | Số tiền `1000000`; ý kiến `Đồng ý theo hồ sơ DEMO`; `Approve` | Đã phê duyệt |
| Finance | Đã phê duyệt | Ghi chú `Đã ghi nhận chi trả hồ sơ đơn lẻ DEMO`; `Mark as Paid` | Đã xác nhận chi |

Kiểm tra thêm: Reviewer phải là người được giao trên `DEMO-HH-06`.

---

## 16. Checklist phân quyền

Đăng xuất và đăng nhập từng tài khoản. Không chỉ đổi role trên cùng một user.

### Officer

- [ ] Thấy Hộ gia đình, Công dân, Chương trình, Rà soát, Kết quả, Hồ sơ xác minh, Đợt trình.
- [ ] Tạo/sửa hộ và công dân.
- [ ] Gửi yêu cầu xác minh.
- [ ] Không có nút ghi kết luận Reviewer.
- [ ] Không có nút phê duyệt đợt của Manager.
- [ ] Không có nút xác nhận đã chi của Finance.

### Reviewer

- [ ] Chỉ thấy hộ và hồ sơ xác minh được giao.
- [ ] Không tạo/sửa dữ liệu hộ, công dân hoặc nhóm.
- [ ] Có nút **Ghi kết luận xác minh** trên hồ sơ được giao.
- [ ] Không mở được hồ sơ xác minh được giao cho Reviewer khác bằng URL trực tiếp.
- [ ] Không xem được toàn bộ `Eligibility Run` của chương trình.

### Manager

- [ ] Xem chính sách, phiên bản, kết quả, hồ sơ xác minh và đợt trình.
- [ ] Kích hoạt phiên bản chính sách.
- [ ] Có ba quyết định trên đợt đã trình.
- [ ] Không sửa danh sách của đợt đã trình.
- [ ] Không ghi kết luận thay Reviewer.

### Finance

- [ ] Thấy Khoản chi và Báo cáo tài chính.
- [ ] Có nút **Xác nhận đã chi** trên khoản `PENDING`.
- [ ] Không thấy chức năng tạo hộ/công dân, chính sách, rà soát hoặc phê duyệt.

---

## 17. Kiểm tra các trường hợp bị chặn

| Thao tác thử | Kết quả đúng |
|---|---|
| Tạo công dân trước khi có hộ | Bị yêu cầu chọn hộ |
| Tạo hai chủ hộ trong cùng hộ | Bị chặn |
| Tạo hai kỳ phân loại chồng nhau | Bị chặn |
| Gán nhóm không có hồ sơ xác minh | Bị chặn |
| Dùng hồ sơ xác minh của hộ khác để gán nhóm | Bị chặn |
| Gán ngày ngoài khoảng Reviewer xác nhận | Bị chặn |
| Đổi Reviewer khi hộ còn hồ sơ xác minh đang chờ | Bị chặn |
| Reviewer kết luận hồ sơ người khác | Bị từ chối quyền |
| Kích hoạt phiên bản không có quy tắc | Bị chặn |
| Officer kích hoạt phiên bản chính sách | Bị từ chối quyền |
| Chọn dòng Cần xác minh để lập đợt | Không có ô chọn / máy chủ từ chối |
| Trình đợt có dòng tiền bằng 0 | Bị chặn |
| Loại dòng nhưng không nhập lý do | Bị chặn |
| Người trình tự phê duyệt | Bị chặn |
| Xác nhận lại khoản đã chi | Bị chặn |
| Xóa lịch sử phân loại, gán nhóm, kết quả hoặc đợt trình | Bị chặn |

---

## 18. Kịch bản thuyết trình ngắn 12–15 phút

| Thời lượng | Nội dung trình bày |
|---|---|
| 1 phút | Đăng nhập Officer, giới thiệu trang công việc và menu theo vai trò |
| 2 phút | Mở hộ 01, công dân, lịch sử phân loại/nhóm và hồ sơ xác minh |
| 2 phút | Mở chính sách, phiên bản và ba quy tắc; giải thích `EQ`, `IN`, `NOT_EXISTS` |
| 3 phút | Mở lần rà soát 1, lọc ba kết quả, mở chi tiết lý do |
| 2 phút | Mở hồ sơ xác minh hộ 03/05 và so sánh với lần rà soát 2 |
| 2 phút | Mở đợt trình bằng Manager và phê duyệt |
| 2 phút | Mở khoản chi bằng Finance, xác nhận một khoản và làm mới báo cáo |
| 1 phút | Đăng nhập lại Officer/Reviewer để chứng minh menu và nút khác nhau |

Thông điệp nên nhấn mạnh:

1. Quy tắc xét hưởng được cấu hình và có phiên bản, không viết cứng theo từng hồ sơ.
2. Mỗi lần rà soát lưu ảnh chụp dữ liệu và lý do; kết quả cũ không bị sửa.
3. Reviewer ghi kết luận và căn cứ độc lập; Officer không tự xác minh nhóm.
4. Người trình, người duyệt và người xác nhận chi là các vai trò khác nhau.
5. Báo cáo chỉ coi khoản được Finance xác nhận là đã chi.

---

## 19. Phiếu ghi kết quả cho thành viên nhóm

| STT | Chức năng | Người test | Kết quả | Mã hồ sơ / ảnh minh chứng | Ghi chú lỗi |
|---:|---|---|---|---|---|
| 1 | Tạo hộ và công dân | | ☐ Đạt ☐ Không đạt | | |
| 2 | Kỳ phân loại hộ | | ☐ Đạt ☐ Không đạt | | |
| 3 | Gửi yêu cầu xác minh | | ☐ Đạt ☐ Không đạt | | |
| 4 | Reviewer ghi kết luận | | ☐ Đạt ☐ Không đạt | | |
| 5 | Gán nhóm đã xác minh | | ☐ Đạt ☐ Không đạt | | |
| 6 | Tạo/kích hoạt chính sách | | ☐ Đạt ☐ Không đạt | | |
| 7 | Rà soát lần 1 | | ☐ Đạt ☐ Không đạt | | |
| 8 | Xử lý cần xác minh | | ☐ Đạt ☐ Không đạt | | |
| 9 | Rà soát lần 2 | | ☐ Đạt ☐ Không đạt | | |
| 10 | Lập và trình đợt | | ☐ Đạt ☐ Không đạt | | |
| 11 | Lãnh đạo quyết định | | ☐ Đạt ☐ Không đạt | | |
| 12 | Finance xác nhận chi | | ☐ Đạt ☐ Không đạt | | |
| 13 | Báo cáo tài chính | | ☐ Đạt ☐ Không đạt | | |
| 14 | Workflow đơn lẻ cũ | | ☐ Đạt ☐ Không đạt | | |
| 15 | Phân quyền bốn tài khoản | | ☐ Đạt ☐ Không đạt | | |

---

## 20. Xử lý lỗi thường gặp khi demo

| Hiện tượng | Cách xử lý |
|---|---|
| Không thấy giao diện/schema mới | Chạy `bench --site development.localhost migrate`, `clear-cache`, đăng nhập lại và `Ctrl + Shift + R` |
| `docker: command not found` | Bạn đang ở trong container; chạy trực tiếp lệnh `bench ...` |
| `ERR_CONNECTION_REFUSED` | Kiểm tra Docker/Dev Container và tiến trình `bench start` |
| Reviewer không thấy hộ | Kiểm tra trường **Người được giao xác minh** trên hộ |
| Không gửi được yêu cầu xác minh | Hộ chưa có Reviewer hợp lệ hoặc đã có yêu cầu cùng nội dung đang chờ |
| Không gán được nhóm | Chưa chọn hồ sơ `COMPLETED + CONFIRMED`, sai đối tượng/nhóm hoặc ngày vượt khoảng xác minh |
| Không kích hoạt được phiên bản | Chưa có quy tắc, chính sách đang tắt, chồng khoảng hiệu lực hoặc tài khoản không phải Manager |
| Kết quả demo nhiều hơn 5 hộ | Đây là đúng: hệ thống rà soát toàn bộ hộ chưa lưu trữ; dùng ô tìm `DEMO-HH-` |
| Không lập được đợt | Chưa chọn dòng đủ điều kiện hoặc kết quả đã nằm trong đợt đang trình/đã duyệt |
| Báo cáo chưa đổi | Bấm **Làm mới**; chỉ khoản `PAID` mới tính là đã chi |

---

## 21. Điều kiện hoàn thành một vòng demo

Một vòng được xem là hoàn tất khi:

- [ ] Có dữ liệu hộ và công dân giả lập đầy đủ.
- [ ] Có hồ sơ xác minh với kết luận và căn cứ.
- [ ] Bản gán nhóm mới dẫn chiếu kết luận xác minh.
- [ ] Chính sách có phiên bản `ACTIVE` và đủ ba quy tắc.
- [ ] Có hai lần rà soát để chứng minh lịch sử và thay đổi sau xác minh.
- [ ] Lần rà soát thứ hai có ít nhất một dòng đủ điều kiện để lập đợt.
- [ ] Đợt được Manager phê duyệt.
- [ ] Khoản chi được Finance xác nhận.
- [ ] Báo cáo thể hiện đúng đã duyệt, đã chi và chờ chi.
- [ ] Bốn tài khoản chỉ thấy và thực hiện đúng chức năng của mình.

Không đưa database, thư mục `sites`, backup, tài khoản thật, mật khẩu hoặc giấy tờ người dân lên Git.
