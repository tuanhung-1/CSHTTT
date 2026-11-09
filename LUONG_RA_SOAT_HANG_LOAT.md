# Luồng rà soát hỗ trợ hàng loạt

Ứng dụng chạy trên ERPNext/Frappe và MariaDB. Các DocType và quy tắc trong mã nguồn được tạo khi chạy `bench --site <site> migrate`. Mỗi máy dùng dữ liệu riêng; không chép thư mục `sites` hoặc cơ sở dữ liệu vào Git.

## Chuẩn bị dữ liệu

1. Tạo **Household** và **Citizen**. Gắn công dân vào hộ. Với chủ hộ, chọn quan hệ `Head` để tên chủ hộ được đồng bộ.
2. Với chương trình cho hộ nghèo/cận nghèo, tạo **Household Classification** có kỳ và ngày hiệu lực bao phủ ngày chốt.
3. Với nhóm chính sách, cán bộ gán một tài khoản **Người xác minh** cho hộ trước. Mở **Household** hoặc **Citizen** và chọn **Gửi xác minh nhóm**. Reviewer ghi kết luận, căn cứ và khoảng hiệu lực; chỉ sau kết luận xác nhận, cán bộ mới dùng **Gán nhóm đã xác minh**. Mỗi bản gán nhóm mới phải dẫn chiếu hồ sơ xác minh phù hợp; bản lịch sử cũ vẫn được giữ.
4. Tạo **Policy**, rồi **Policy Version** ở `DRAFT`. Tạo các **Policy Rule** trỏ vào phiên bản đó. Quy tắc có loại `CLASSIFICATION`, `TARGET_GROUP`, `RESIDENCY` hoặc `DUPLICATE`; kết quả có thể là đạt, không đạt hoặc cần xác minh khi thiếu dữ liệu. Lãnh đạo chuyển phiên bản sang `ACTIVE` sau khi kiểm tra căn cứ và khoảng hiệu lực. Phiên bản đã kích hoạt không được sửa nội dung/quy tắc.

## Chạy một vòng

1. Cán bộ tạo **Support Program**. Chọn **Đối tượng nhận hỗ trợ** `Household` hoặc `Citizen`. Với `Citizen`, chọn **Nhóm đối tượng chính sách**; với `Household`, có thể chọn nhóm hộ nghèo/cận nghèo. Chọn phiên bản chính sách `ACTIVE`, ngày chốt, hình thức hỗ trợ và mức hỗ trợ.
2. Trên chương trình, bấm **Chạy rà soát hàng loạt**. Hệ thống tạo **Eligibility Run** riêng cho lần chạy, xét tất cả hộ/công dân chưa lưu trữ, lưu đầu vào, từng điều kiện và lý do trong **Eligibility Result**. Kết quả `NEED_VERIFICATION` không được tự đưa vào đợt trình.
3. Với dòng **Cần xác minh**, cán bộ mở **Kết quả rà soát** rồi bấm **Gửi yêu cầu xác minh**. Hộ phải có Reviewer được giao. Reviewer chỉ thấy hồ sơ được giao, ghi kết luận và căn cứ trong **Hồ sơ xác minh**. Kết luận không sửa kết quả cũ: cán bộ cập nhật dữ liệu gốc hoặc gán nhóm theo kết luận, sau đó chạy rà soát mới. Nếu Reviewer xác nhận đối tượng không thuộc nhóm tại ngày chốt, quy tắc nhóm tương ứng sẽ trả về **Không đạt** ở lần rà soát tiếp theo, thay vì tiếp tục **Cần xác minh**.
4. Mở lần rà soát, xem danh sách, chọn các dòng **Đủ điều kiện** rồi bấm **Lập đợt trình**. Trong **Approval Batch**, cán bộ có thể bỏ dòng hoặc điều chỉnh mức hỗ trợ kèm lý do; với hiện vật phải nhập tên và số lượng. Bấm **Trình lãnh đạo**.
5. Lãnh đạo mở đợt **Đã trình lãnh đạo**, đọc danh sách và lý do, rồi duyệt, từ chối hoặc trả lại kèm ý kiến. Người trình không tự duyệt đợt của mình. Khi duyệt, hệ thống tạo các **Disbursement** ở trạng thái **Chờ chi**.
6. Tài chính mở **Disbursement**, xác nhận khoản đã chi kèm ghi chú/chứng từ. **Báo cáo tài chính an sinh** thể hiện đã duyệt, đã chi, chờ chi và biểu đồ chi tiền theo tháng. Hỗ trợ hiện vật được đếm theo số khoản, không cộng vào số tiền.

**Lưu ý:** `Support Application` là luồng hồ sơ đơn lẻ cũ, vẫn có để dùng dữ liệu trước đây. Trạng thái `Paid` của hồ sơ cũ không được coi là chi tiền thực tế trong báo cáo mới khi chưa có **Disbursement**. Hệ thống hiện ghi nhận việc xác nhận chi, chưa kết nối ngân hàng hoặc đối soát tự động. Cán bộ phải xác minh hồ sơ và căn cứ trước khi phê duyệt.
