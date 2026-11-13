# Document RAG — chatbot hỏi đáp tài liệu với Gemini API

Ứng dụng độc lập trong thư mục `RAG/` để demo đồ án: tải PDF, DOCX, TXT hoặc Markdown; tạo embedding; hỏi đáp bằng tiếng Việt; hiển thị tài liệu và trang được trích dẫn. Bản này chỉ hỏi đáp **tài liệu văn bản**, chưa kết nối dữ liệu ERP.

## Chuẩn bị

- Python 3.11 trở lên. Ứng dụng chỉ dùng thư viện chuẩn, không cần `pip install`.
- [Tạo Gemini API key trong Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key). Mở file `.env` trong thư mục `RAG` và điền key vào dòng:

  ```dotenv
  GEMINI_API_KEY=API_KEY_CUA_BAN
  ```

  File `.env` đã được Git bỏ qua. Bạn cũng có thể đặt biến môi trường `GEMINI_API_KEY` trong Terminal; giá trị đó được ưu tiên hơn file `.env`.

- Để đọc PDF dạng văn bản, cài `pdftotext` (Poppler). Trên macOS: `brew install poppler`. PDF scan chưa có OCR; hãy chuyển thành PDF có lớp chữ hoặc TXT trước khi tải lên.

## Chạy

Sau khi điền key vào `.env`:

```bash
cd RAG
python3 app.py
```

Mở **http://127.0.0.1:8765**. Tải tài liệu lên, đợi trạng thái **Sẵn sàng**, rồi đặt câu hỏi. Bấm nguồn bên dưới câu trả lời để mở tệp gốc. Với PDF, liên kết mở đúng trang nếu trình xem PDF hỗ trợ `#page=`.

Nếu đã nạp tài liệu với một embedding model khác, bấm **Lập lại chỉ mục** trên tài liệu đó. Việc đổi model khiến vector cũ không còn dùng được cho tìm kiếm.

Nếu Gemini báo **HTTP 503**, dịch vụ đang tạm quá tải. Ứng dụng tự thử lại tối đa 3 lần với thời gian chờ tăng dần. Nếu vẫn lỗi, câu hỏi được giữ trong ô nhập để bạn gửi lại sau ít phút.

Các biến môi trường tùy chọn:

| Biến | Mặc định | Mục đích |
| --- | --- | --- |
| `RAG_HOST` | `127.0.0.1` | Địa chỉ máy chủ; giữ mặc định cho demo cục bộ |
| `RAG_PORT` | `8765` | Cổng web |
| `RAG_DATA_DIR` | `RAG/data` | Thư mục lưu file và SQLite |
| `RAG_CHAT_MODEL` | `gemini-3.5-flash-lite` | Mô hình tạo câu trả lời |
| `RAG_EMBED_MODEL` | `gemini-embedding-001` | Mô hình embedding văn bản |

Ví dụ đổi cổng: `RAG_PORT=9000 python3 app.py`. Nếu tài khoản Gemini không được dùng model mặc định, đổi `RAG_CHAT_MODEL` theo model mà API key của bạn truy cập được.

## Cách hoạt động

1. Tệp gốc lưu trong `data/uploads/`; tiến trình nền tách chữ thành đoạn tối đa khoảng 1.200 ký tự, có chồng lấn ngắn.
2. Gemini `batchEmbedContents` tạo vector cho từng đoạn với `RETRIEVAL_DOCUMENT`. SQLite lưu đoạn, vector và trang nguồn.
3. Khi hỏi, ứng dụng tạo vector với `RETRIEVAL_QUERY`, tính độ tương đồng cosine kết hợp từ khóa và chọn 5 đoạn gần nhất.
4. Gemini `generateContent` nhận các đoạn đó để viết câu trả lời. Giao diện chỉ hiện nguồn có số `[1]`, `[2]`… được mô hình trích dẫn.

File gốc lưu trên máy nhưng **đoạn văn bản được gửi đến Gemini API khi lập chỉ mục; câu hỏi và các đoạn tìm được được gửi đến Gemini API khi trả lời**. Ứng dụng chưa có đăng nhập/phân quyền, nên chỉ chạy cục bộ và dùng tài liệu phù hợp để gửi cho dịch vụ bên ngoài. Chỉ mục vector nhỏ này phù hợp demo vài chục tài liệu; quy mô lớn nên dùng vector database chuyên dụng.

## Kiểm tra

```bash
cd RAG
python3 -m unittest discover -s tests -v
```

Bài kiểm tra dùng phản hồi API giả, không cần API key thật và không gửi dữ liệu ra ngoài. Tham khảo [Gemini Embeddings](https://ai.google.dev/gemini-api/docs/embeddings) và [Generate Content API](https://ai.google.dev/gemini-api/docs/generate-content/text-generation).
