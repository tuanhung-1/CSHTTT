# Hướng dẫn nhập dữ liệu mẫu và xử lý một vòng hồ sơ an sinh

Tài liệu này dành cho người mới nhận source `social_welfare`. Dữ liệu bên dưới là **giả lập để thực hành**, không phải hồ sơ người dân thật. Hai máy dùng database riêng; tài khoản, mật khẩu và dữ liệu mẫu **không tự đi theo Git**. Cách cài và cập nhật app xem [CODE_FIRST.md](CODE_FIRST.md).

## 0. Chuẩn bị tài khoản và site

Bạn tự tạo bốn **System User** trên site của mình, bật tài khoản và gán mỗi người một role tương ứng:

| Người thực hiện | Role cần gán | Việc trong vòng mẫu |
|---|---|---|
| Cán bộ an sinh | `Social Welfare Officer` | Tạo hộ, công dân, phân loại, chương trình, hồ sơ và trình xác minh |
| Người xác minh | `Social Welfare Reviewer` | Nhận hồ sơ của hộ được giao và ghi kết quả xác minh |
| Lãnh đạo phường | `Social Welfare Manager` | Phê duyệt, từ chối hoặc yêu cầu bổ sung |
| Cán bộ tài chính | `Social Welfare Finance` | Xác nhận trạng thái chi trả |

Không cần dùng email hoặc mật khẩu giống máy người viết code. Để thử phân quyền đúng, dùng **bốn tài khoản khác nhau**; người trình không được tự duyệt hồ sơ của mình. Đăng nhập tài khoản Cán bộ an sinh, mở `/desk/an-sinh-xa-hoi`, rồi nhập theo thứ tự dưới đây. Nếu site đã có mã `DEMO-POOR-2026`, đổi mã chương trình để tránh trùng.

## 1. Tạo hộ gia đình

Vào **Hộ gia đình → Thêm mới**. Hộ được tạo trước công dân; ô **Công dân làm chủ hộ** có thể để trống ở bước này.

| Trường trên form | Dữ liệu mẫu / cách điền |
|---|---|
| Mã hộ gia đình | Để trống; hệ thống tự tạo |
| Họ tên chủ hộ | `Nguyễn Văn An` |
| Công dân làm chủ hộ | Để trống khi tạo hộ |
| Tổ dân phố | `Tổ dân phố 1` |
| Địa chỉ | `12 Đường Hoa Sen, phường Minh An` |
| Đã lưu trữ | Không chọn |
| Số thành viên | Tự tính; ban đầu là `0` |
| Thu nhập bình quân | `700000` |
| Người được giao xác minh | Chọn **tài khoản Người xác minh do bạn tự tạo** |
| Phân loại cũ (chưa rõ kỳ hiệu lực) | Trường ẩn/chỉ đọc; không nhập |
| Lịch sử phân loại | Hệ thống hiển thị; chưa có ở bước này |

Bấm **Lưu**. Ghi nhớ **mã hộ** được tạo; ở các bước sau, hãy chọn đúng hộ này. Kết quả mong đợi: hộ lưu thành công, số thành viên `0`, chưa có công dân làm chủ hộ.

## 2. Thêm công dân vào hộ

Trong hộ vừa lưu, bấm **Thêm công dân vào hộ**. Tạo công dân đầu tiên:

| Trường trên form | Dữ liệu mẫu / cách điền |
|---|---|
| Mã công dân | Để trống; hệ thống tự tạo |
| Số định danh / CCCD | Để trống; không dùng CCCD thật |
| Họ và tên | `Nguyễn Văn An` |
| Ngày sinh | `15/03/1980` |
| Giới tính | `Male` (Nam) |
| Quan hệ với chủ hộ | `Head` (Chủ hộ) |
| Số điện thoại | Để trống |
| Hộ gia đình | Hộ vừa tạo ở bước 1; nút từ form hộ sẽ điền sẵn |
| Đã lưu trữ | Không chọn |

Bấm **Lưu**, mở lại hộ. Kết quả mong đợi: **Số thành viên = 1** và **Công dân làm chủ hộ** được liên kết với Nguyễn Văn An.

Thêm một thành viên nữa bằng cùng nút:

| Trường trên form | Dữ liệu mẫu / cách điền |
|---|---|
| Mã công dân | Để trống; hệ thống tự tạo |
| Số định danh / CCCD | Để trống |
| Họ và tên | `Nguyễn Thị Bình` |
| Ngày sinh | `20/07/1983` |
| Giới tính | `Female` (Nữ) |
| Quan hệ với chủ hộ | `Spouse` (Vợ/chồng) |
| Số điện thoại | Để trống |
| Hộ gia đình | Cùng hộ Nguyễn Văn An |
| Đã lưu trữ | Không chọn |

Sau khi lưu, **Số thành viên = 2**. Một hộ chỉ được có một công dân đánh dấu `Head`.

## 3. Ghi kỳ phân loại hộ

Mở hộ ở bước 1, bấm **Thêm kỳ phân loại**. Chương trình diện hộ nghèo ở bước 4 chỉ chấp nhận hồ sơ nếu phân loại phù hợp và còn hiệu lực vào **ngày hồ sơ**.

| Trường trên form | Dữ liệu mẫu / cách điền |
|---|---|
| Hộ gia đình | Hộ Nguyễn Văn An; nút từ form hộ sẽ điền sẵn |
| Phân loại | `Poor Household` (Hộ nghèo) |
| Kỳ phân loại | `2026` |
| Hiệu lực từ | `01/01/2026` |
| Hiệu lực đến | `31/12/2026` |
| Căn cứ phân loại | `Quyết định rà soát hộ nghèo năm 2026 (dữ liệu mẫu)` |
| Tệp minh chứng | Để trống |
| Ghi chú | `Dữ liệu mẫu phục vụ kiểm tra quy trình` |
| Dữ liệu cũ cần rà soát | Chỉ đọc; không chọn |
| Đã hủy hiệu lực, lý do/người/thời điểm hủy | Hệ thống quản lý; không nhập |

Bấm **Lưu**. Bản phân loại đã lưu được giữ làm lịch sử; không sửa hoặc xóa trực tiếp. Các kỳ của cùng hộ không được chồng ngày hiệu lực.

## 4. Tạo chương trình hỗ trợ

Vào **Chương trình hỗ trợ → Thêm mới**.

| Trường trên form | Dữ liệu mẫu / cách điền |
|---|---|
| Mã chương trình | `DEMO-POOR-2026` |
| Tên chương trình | `Hỗ trợ hộ nghèo năm 2026` |
| Mô tả | `Chương trình dữ liệu mẫu để thử quy trình tại phường` |
| Ngày bắt đầu | `01/01/2026` |
| Ngày kết thúc | `31/12/2026` |
| Mức hỗ trợ | `1000000` |
| Nhóm đối tượng | `poor` |
| Đang triển khai | Chọn |
| Đã lưu trữ | Không chọn |

Bấm **Lưu**. Chương trình và hộ được tạo độc lập, rồi mới chọn trong hồ sơ hỗ trợ.

## 5. Tạo và trình hồ sơ hỗ trợ

Vào **Hồ sơ hỗ trợ → Thêm mới**.

| Trường trên form | Dữ liệu mẫu / cách điền |
|---|---|
| Mã hồ sơ | Để trống; hệ thống tự tạo |
| Hộ gia đình | Hộ Nguyễn Văn An ở bước 1 |
| Chương trình hỗ trợ | `DEMO-POOR-2026` |
| Ngày hồ sơ | `08/11/2026` |
| Số tiền đề nghị | `1000000` |
| Số tiền phê duyệt | Để `0` lúc tạo; lãnh đạo nhập sau |
| Lý do đề nghị | `Đề nghị hỗ trợ theo diện hộ nghèo năm 2026 (dữ liệu mẫu)` |
| Trạng thái | Hệ thống đặt `Draft` (Nháp) |
| Kết quả xác minh | Để trống lúc tạo |
| Ý kiến của lãnh đạo | Để trống lúc tạo |
| Ghi chú xác nhận chi trả | Để trống lúc tạo |
| Người trình, người quyết định, người xác nhận chi; các thời điểm tương ứng | Hệ thống tự ghi khi chuyển bước |

Bấm **Lưu**, kiểm tra trạng thái `Draft`, rồi bấm riêng **Submit**. Kết quả mong đợi: `Submitted` (Đã tiếp nhận). **Lưu** chỉ lưu bản nháp, không thay cho **Submit**. Hệ thống không cho một hộ lập hai hồ sơ cho cùng một chương trình.

## 6. Người xác minh xử lý

Đăng xuất, đăng nhập tài khoản có role `Social Welfare Reviewer` đã được gán cho hộ ở bước 1. Vào **Hồ sơ được giao xác minh**, mở đúng hồ sơ.

| Trạng thái trước | Việc cần làm | Dữ liệu mẫu | Trạng thái sau |
|---|---|---|---|
| `Submitted` | Bấm **Start Review** | Không cần nhập thêm | `Reviewing` |
| `Reviewing` | Nhập **Kết quả xác minh**, bấm **Lưu**, rồi **Complete Verification** | `Đã đối chiếu thông tin hộ, thành viên và kỳ phân loại hộ nghèo năm 2026. Hồ sơ phù hợp để trình lãnh đạo xem xét. (Dữ liệu mẫu)` | `Pending Approval` |

Nếu không thấy hồ sơ, mở hộ bằng tài khoản Cán bộ an sinh và kiểm tra **Người được giao xác minh**. Reviewer chỉ nhìn thấy hộ/hồ sơ được giao.

## 7. Lãnh đạo phường phê duyệt

Đăng xuất, đăng nhập tài khoản có role `Social Welfare Manager`. Mở hồ sơ ở mục **Hồ sơ chờ phê duyệt**.

| Trường cần điền | Dữ liệu mẫu |
|---|---|
| Ý kiến của lãnh đạo | `Đồng ý hỗ trợ hộ Nguyễn Văn An theo kết quả xác minh và chương trình hỗ trợ hộ nghèo năm 2026. (Dữ liệu mẫu)` |
| Số tiền phê duyệt | `1000000` |

Bấm **Lưu**, sau đó **Approve**. Kết quả mong đợi: `Approved`; hệ thống tự ghi người và thời điểm quyết định. Lãnh đạo cần là người khác với người đã Submit.

Trong trường hợp khác, lãnh đạo có thể nhập lý do rồi chọn **Reject** hoặc **Return for Supplement**. Hồ sơ `Returned` được Cán bộ an sinh đưa về `Draft` bằng **Reset to Draft**, bổ sung và **Submit** lại. Đây là nhánh phụ; để hoàn thành một vòng mẫu, hãy chọn **Approve**.

## 8. Tài chính xác nhận chi

Đăng xuất, đăng nhập tài khoản có role `Social Welfare Finance` do bạn tự tạo. Mở hồ sơ ở mục **Hồ sơ chờ xác nhận chi trả**.

| Trường cần điền | Dữ liệu mẫu |
|---|---|
| Ghi chú xác nhận chi trả | `Đã kiểm tra hồ sơ được duyệt và ghi nhận chi trả 1.000.000 đồng cho hộ Nguyễn Văn An ngày 08/11/2026. (Dữ liệu mẫu)` |

Bấm **Lưu**, sau đó **Mark as Paid**. Kết quả mong đợi: `Paid`; hệ thống tự ghi người và thời điểm xác nhận chi. Đây là **cuối một vòng** trong app hiện tại. `Paid` mới là trạng thái ghi nhận, **chưa tạo chứng từ hoặc chuyển tiền thật**.

## Kiểm tra nhanh kết quả

`Draft → Submitted → Reviewing → Pending Approval → Approved → Paid`

Mỗi bước phải do role được phân công thực hiện. Nếu thực hành sau năm 2026, hãy đổi **ngày hiệu lực phân loại, ngày chương trình và ngày hồ sơ** cùng sang một khoảng thời gian phù hợp. Không sử dụng dữ liệu mẫu này cho quyết định hoặc chi trả thực tế.
