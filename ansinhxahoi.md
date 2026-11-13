1. **Household và citizen**

![](data:image/png;base64...)

![](data:image/png;base64...)

đạt tên chủ hộ và tên trong trong citizen khác nhau cũng được mặc dù là chủ hộ.

Chưa có phần này:

1. Người có công: Cá nhân thuộc diện người có công.
2. Thân nhân người có công: Cá nhân thuộc nhóm thân nhân được công nhận.
3. Đối tượng bảo trợ xã hội: Các cá nhân thuộc những nhóm bảo trợ được lựa chọn trong phạm vi đề tài.

Đề xuất:

**Tạo thêm 2 DocType**

A. Target Group — Danh mục nhóm đối tượng

|  |  |  |
| --- | --- | --- |
| **Fieldname** | **Type** | **Ví dụ** |
| group\_code | Data (Unique) | MERITORIOUS\_PERSON |
| group\_name | Data | Người có công |
| description | Text | Mô tả nhóm |
| is\_active | Check | 1 |

Dữ liệu mẫu gồm: Người có công, Thân nhân người có công, Đối tượng bảo trợ xã hội.

B. Target Group Assignment — Gán nhóm cho đối tượng

|  |  |
| --- | --- |
| **Fieldname** | **Type** |
| target\_group | Link → Target Group |
| citizen | Link → Citizen |
| household | Link → Household |
| valid\_from | Date |
| valid\_to | Date |
| evidence | Attach |
| status | Select |

 Một hộ chỉ có một phân loại hộ hiệu lực tại cùng thời điểm.

 Một công dân có thể thuộc nhiều nhóm đối tượng chính sách.

 Không cho phép gán trùng cùng nhóm với khoảng hiệu lực chồng lấn.

 Khi nhóm hết hiệu lực, giữ bản ghi lịch sử, không xóa.

 Bổ sung danh sách Nhóm đối tượng chính sách trên form Household và Citizen, lọc theo đối tượng tương ứng.

# **2. Support Program và Support Application.**

Phần này cần thiết kế lại vì nó phải application cho từng hộ gia đình cần sửa lại bộ lọc để app dụng hàng loạt chương trinh hỗ trợ có thể là hỗ trợ hộ gia đình hoặc cá nhân

## 1. Policy — Danh mục chính sách

Mục đích: Quản lý các chính sách an sinh xã hội được sử dụng trong hệ thống.

|  |  |  |  |
| --- | --- | --- | --- |
| **Fieldname** | **Field Type** | **Bắt buộc** | **Mô tả** |
| policy\_code | Data (Unique) | Có | Mã chính sách |
| policy\_name | Data | Có | Tên chính sách |
| description | Text | Không | Nội dung chính sách |
| policy\_type | Select | Có | Hộ gia đình / Cá nhân / Cả hai |
| is\_active | Check | Có | Trạng thái hoạt động |

Ví dụ: Chính sách hỗ trợ hộ nghèo, chính sách hỗ trợ người khuyết tật, chính sách hỗ trợ người có công với cách mạng.

## 2. Policy Version — Phiên bản chính sách

Mục đích: Quản lý các phiên bản của một chính sách theo thời gian hiệu lực.

|  |  |  |  |
| --- | --- | --- | --- |
| **Fieldname** | **Field Type** | **Bắt buộc** | **Mô tả** |
| policy | Link → Policy | Có | Chính sách áp dụng |
| version\_number | Data | Có | Số phiên bản |
| effective\_from | Date | Có | Ngày bắt đầu hiệu lực |
| effective\_to | Date | Không | Ngày hết hiệu lực |
| legal\_reference | Data | Có | Căn cứ pháp lý |
| document\_file | Attach | Không | Văn bản chính sách |
| status | Select | Có | DRAFT / ACTIVE / EXPIRED |
| approved\_by | Link → User | Khi kích hoạt | Người phê duyệt |
| approved\_on | Datetime | Khi kích hoạt | Thời điểm phê duyệt |

Quy tắc:

* Một Policy có thể có nhiều phiên bản.
* Không cho phép các phiên bản ACTIVE có khoảng hiệu lực chồng lấn trái quy tắc.
* Phiên bản đã được sử dụng để rà soát không được sửa nội dung; phải tạo phiên bản mới.
* Chỉ phiên bản đã phê duyệt và có hiệu lực mới được dùng để chạy rà soát.

## 3. Policy Rule — Quy tắc xét điều kiện

Mục đích: Lưu các điều kiện để Python Rule Engine tự động lọc hộ gia đình hoặc công dân.

|  |  |  |  |
| --- | --- | --- | --- |
| **Fieldname** | **Field Type** | **Bắt buộc** | **Mô tả** |
| policy\_version | Link → Policy Version | Có | Phiên bản áp dụng |
| rule\_code | Data | Có | Mã điều kiện |
| rule\_name | Data | Có | Tên điều kiện |
| condition\_type | Select | Có | CLASSIFICATION / TARGET\_GROUP / RESIDENCY / DUPLICATE |
| operator | Select | Có | EQ / IN / EXISTS / NOT\_EXISTS |
| expected\_value | Data | Có điều kiện | Giá trị cần kiểm tra |
| missing\_behavior | Select | Có | NEED\_VERIFICATION / FAIL |
| priority | Int | Có | Thứ tự kiểm tra |
| is\_required | Check | Có | Điều kiện bắt buộc |
| message | Small Text | Không | Giải thích kết quả |

Ví dụ quy tắc:

Rule Engine trả về ba trạng thái: ELIGIBLE, NOT\_ELIGIBLE, NEED\_VERIFICATION. AI không được tự sửa các rule này.

## 4. Support Program — Chương trình áp dụng chính sách

Mục đích: Tạo các chương trình hỗ trợ dựa trên Policy Version để tự động lọc đối tượng.

Giữ nguyên các trường cũ, bổ sung:

|  |  |  |  |
| --- | --- | --- | --- |
| **Fieldname** | **Field Type** | **Bắt buộc** | **Mô tả** |
| beneficiary\_type | Select | Có | Household / Citizen |
| target\_group\_ref | Link → Target Group | Có điều kiện | Nhóm đối tượng cần hỗ trợ |
| policy\_version | Link → Policy Version | Khi tự động | Phiên bản chính sách |
| cutoff\_date | Date | Khi tự động | Ngày chốt xét hưởng |
| support\_type | Select | Có | CASH / IN\_KIND |
| budget\_estimate | Currency | Không | Ngân sách dự kiến |
| screening\_status | Select (Read Only) | Có | NOT\_RUN / RUNNING / COMPLETED / FAILED |

Giữ target\_group Select cũ để tương thích; sử dụng target\_group\_ref cho nhóm chính sách mới. Với chương trình hộ nghèo/cận nghèo, điều kiện phải đọc từ Household Classification, không bắt buộc tạo Target Group tương ứng.

Quy tắc: Chương trình tự động phải dùng Policy Version hợp lệ, thực hiện các Policy Rule và tạo Eligibility Run để lưu lần rà soát.

## 1. Eligibility Run — Lần chạy rà soát

Mục đích: Quản lý mỗi lần hệ thống chạy bộ lọc để tìm các hộ gia đình hoặc công dân đủ điều kiện nhận hỗ trợ theo chương trình và chính sách đã cấu hình.

|  |  |  |  |
| --- | --- | --- | --- |
| **Fieldname** | **Field Type** | **Bắt buộc** | **Mô tả** |
| support\_program | Link → Support Program | Có | Chương trình cần rà soát |
| policy\_version | Link → Policy Version | Có | Phiên bản chính sách được áp dụng |
| cutoff\_date | Date | Có | Ngày chốt để xét điều kiện |
| status | Select | Có | QUEUED / RUNNING / COMPLETED / FAILED |
| total\_count | Int | Tự động | Tổng đối tượng được rà soát |
| eligible\_count | Int | Tự động | Số đối tượng đủ điều kiện |
| not\_eligible\_count | Int | Tự động | Số đối tượng không đủ điều kiện |
| need\_verification\_count | Int | Tự động | Số đối tượng cần xác minh |
| started\_by | Link → User | Tự động | Người thực hiện rà soát |
| started\_at | Datetime | Tự động | Thời gian bắt đầu |
| completed\_at | Datetime | Tự động | Thời gian kết thúc |
| rule\_snapshot | JSON | Tự động | Bản sao các điều kiện áp dụng tại thời điểm chạy |

Quy tắc xử lý: Một Support Program có thể được rà soát nhiều lần. Mỗi lần chạy lưu kết quả riêng để có thể so sánh và truy vết, không ghi đè kết quả trước đó.

## 2. Eligibility Result — Kết quả rà soát

Mục đích: Lưu kết quả xét điều kiện của từng hộ gia đình hoặc công dân trong một lần rà soát.

|  |  |  |  |
| --- | --- | --- | --- |
| **Fieldname** | **Field Type** | **Bắt buộc** | **Mô tả** |
| eligibility\_run | Link → Eligibility Run | Có | Lần rà soát |
| beneficiary\_type | Select | Có | Household / Citizen |
| household | Link → Household | Có điều kiện | Hộ được xét hỗ trợ |
| citizen | Link → Citizen | Có điều kiện | Công dân được xét hỗ trợ |
| result\_status | Select | Có | ELIGIBLE / NOT\_ELIGIBLE / NEED\_VERIFICATION |
| reason\_summary | Small Text | Không | Tổng hợp lý do kết quả |
| evaluated\_at | Datetime | Tự động | Thời gian đánh giá |
| input\_snapshot | JSON | Tự động | Dữ liệu dùng để xét tại thời điểm chạy |
| rule\_details | Table → Eligibility Rule Detail | Tự động | Chi tiết kết quả từng rule |

Quy tắc xử lý: Mỗi đối tượng chỉ có một Eligibility Result trong cùng một Eligibility Run. Kết quả đã hoàn thành được giữ nguyên; nếu hồ sơ thay đổi thì tạo lần rà soát mới.

## 3. Eligibility Rule Detail — Chi tiết điều kiện xét hưởng

Loại: Child DocType thuộc Eligibility Result.

Mục đích: Lưu kết quả kiểm tra từng điều kiện để cán bộ biết vì sao một đối tượng đủ điều kiện, không đủ điều kiện hoặc cần xác minh.

|  |  |  |  |
| --- | --- | --- | --- |
| **Fieldname** | **Field Type** | **Bắt buộc** | **Mô tả** |
| rule\_code | Data | Có | Mã điều kiện |
| rule\_name | Data | Có | Tên điều kiện |
| actual\_value | Data | Không | Giá trị dữ liệu thực tế |
| expected\_value | Data | Không | Giá trị yêu cầu |
| evaluation | Select | Có | PASS / FAIL / UNKNOWN |
| reason | Small Text | Không | Giải thích kết quả |

Ví dụ: Hộ HH-2026-00001 được kiểm tra:

|  |  |  |
| --- | --- | --- |
| **Rule** | **Kết quả** | **Giải thích** |
| CLASS\_VALID | PASS | Hộ nghèo còn hiệu lực |
| RESIDENCY\_VALID | PASS | Cư trú đã xác minh |
| NO\_DUPLICATE | PASS | Chưa phát hiện hỗ trợ trùng |

Kết quả tổng hợp: ELIGIBLE.

## 4. Approval Batch — Đợt trình phê duyệt

Mục đích: Tổng hợp danh sách hộ gia đình hoặc công dân đủ điều kiện đã được cán bộ lựa chọn để trình lãnh đạo phê duyệt hàng loạt, thay vì duyệt từng hồ sơ riêng lẻ.

|  |  |  |  |
| --- | --- | --- | --- |
| **Fieldname** | **Field Type** | **Bắt buộc** | **Mô tả** |
| support\_program | Link → Support Program | Có | Chương trình hỗ trợ |
| eligibility\_run | Link → Eligibility Run | Có | Lần rà soát làm căn cứ |
| status | Select | Có | DRAFT / SUBMITTED / APPROVED / REJECTED / RETURNED |
| total\_beneficiaries | Int | Tự động | Tổng số đối tượng đề xuất |
| total\_amount | Currency | Tự động | Tổng kinh phí đề xuất |
| submitted\_by | Link → User | Tự động | Cán bộ trình duyệt |
| submitted\_at | Datetime | Tự động | Thời điểm trình |
| decided\_by | Link → User | Khi quyết định | Lãnh đạo phê duyệt |
| decided\_at | Datetime | Khi quyết định | Thời điểm quyết định |
| decision\_note | Text | Có điều kiện | Ý kiến phê duyệt, từ chối hoặc trả lại |
| items | Table → Approval Batch Item | Có | Danh sách các đối tượng đề xuất |

Quy tắc xử lý: Chỉ những đối tượng đủ điều kiện mới được đưa vào danh sách đề xuất thông thường. Lãnh đạo phê duyệt, từ chối hoặc trả lại cả đợt. Người trình không được tự phê duyệt đợt mình đã trình.

## 5. Approval Batch Item — Chi tiết danh sách hỗ trợ

Loại: Child DocType thuộc Approval Batch.

Mục đích: Lưu thông tin từng hộ gia đình hoặc công dân được đề xuất nhận hỗ trợ trong một đợt phê duyệt.

|  |  |  |  |
| --- | --- | --- | --- |
| **Fieldname** | **Field Type** | **Bắt buộc** | **Mô tả** |
| beneficiary\_type | Select | Có | Household / Citizen |
| household | Link → Household | Có điều kiện | Hộ gia đình được đề xuất |
| citizen | Link → Citizen | Có điều kiện | Công dân được đề xuất |
| eligibility\_result | Link → Eligibility Result | Có | Kết quả rà soát làm căn cứ |
| proposed\_amount | Currency | Khi hỗ trợ tiền | Số tiền đề xuất hỗ trợ |
| remarks | Small Text | Không | Ghi chú về đối tượng |
| selection\_status | Select | Có | SELECTED / REMOVED, mặc định SELECTED |
| change\_reason | Small Text | Khi thay đổi | Lý do sửa, loại hoặc khôi phục |
| modified\_by\_user | Link → User | Tự động | Cán bộ thực hiện thay đổi gần nhất |
| modified\_at | Datetime | Tự động | Thời điểm thay đổi gần nhất |

**2. Quy tắc xử lý**

|  |  |
| --- | --- |
| **Thao tác** | **Quy tắc** |
| Thêm | Chỉ thêm hộ/công dân có kết quả ELIGIBLE thuộc lần rà soát của Approval Batch |
| Sửa | Cho phép chỉnh sửa mức hỗ trợ đề xuất và ghi chú theo chính sách; yêu cầu lý do khi điều chỉnh |
| Loại | Chuyển selection\_status thành REMOVED, bắt buộc nhập lý do |
| Khôi phục | Chuyển về SELECTED sau khi kiểm tra lại điều kiện |
| Chống trùng | Một hộ/công dân không được xuất hiện hai lần trong cùng Approval Batch |
| Trình duyệt | Khi Approval Batch chuyển SUBMITTED, khóa chỉnh sửa các dòng |
| Phê duyệt | Khi APPROVED, chỉ các dòng SELECTED được chuyển sang chi trả |

## 6. Disbursement — Ghi nhận chi trả

Mục đích: Quản lý việc chi tiền hoặc cấp phát hiện vật cho các hộ gia đình, công dân đã được lãnh đạo phê duyệt.

|  |  |  |  |
| --- | --- | --- | --- |
| **Fieldname** | **Field Type** | **Bắt buộc** | **Mô tả** |
| approval\_batch | Link → Approval Batch | Có | Đợt đã phê duyệt |
| eligibility\_result | Link → Eligibility Result | Có | Kết quả xét hưởng |
| beneficiary\_type | Select | Có | Household / Citizen |
| household | Link → Household | Có điều kiện | Hộ nhận hỗ trợ |
| citizen | Link → Citizen | Có điều kiện | Công dân nhận hỗ trợ |
| support\_type | Select | Có | CASH / IN\_KIND |
| amount | Currency | Khi hỗ trợ tiền | Số tiền được chi |
| item\_description | Data | Khi hỗ trợ hiện vật | Tên hiện vật |
| quantity | Float | Khi hỗ trợ hiện vật | Số lượng hiện vật |
| status | Select | Có | PENDING / PAID / FAILED / CANCELLED |
| paid\_on | Datetime | Khi hoàn tất | Thời điểm chi trả |
| confirmed\_by | Link → User | Khi hoàn tất | Cán bộ xác nhận |
| payment\_note | Small Text | Không | Ghi chú chi trả |
| receipt\_file | Attach | Không | Minh chứng nhận hỗ trợ |

Quy tắc xử lý: Chỉ được tạo khoản chi trả từ danh sách đã được phê duyệt. Mỗi khoản chi gắn với một đối tượng và phải kiểm tra chống chi trùng theo chương trình, kỳ hỗ trợ và loại hỗ trợ. Chỉ bản ghi PAID mới được tính vào số đã chi thực tế.

![](data:image/png;base64...)