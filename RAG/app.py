"""HTTP entry point for the local document RAG demo."""

from __future__ import annotations

import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlsplit

from rag_core import MAX_FILE_BYTES, GeminiClient, RAGError, RAGService


BASE_DIR = Path(__file__).resolve().parent
ENV_KEYS = {"GEMINI_API_KEY", "RAG_CHAT_MODEL", "RAG_EMBED_MODEL", "RAG_HOST", "RAG_PORT", "RAG_DATA_DIR"}
STATIC = {
    "/": (BASE_DIR / "static" / "index.html", "text/html; charset=utf-8"),
    "/static/app.js": (BASE_DIR / "static" / "app.js", "text/javascript; charset=utf-8"),
    "/static/style.css": (BASE_DIR / "static" / "style.css", "text/css; charset=utf-8"),
}


def load_local_env(path: Path = BASE_DIR / ".env") -> None:
    """Load simple KEY=VALUE settings without replacing shell environment variables."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        key = key.strip()
        if separator and key in ENV_KEYS:
            value = value.strip()
            if len(value) >= 2 and value[0] in {'"', "'"} and value[-1] == value[0]:
                value = value[1:-1]
            os.environ.setdefault(key, value)


def make_handler(service: RAGService):
    class Handler(BaseHTTPRequestHandler):
        server_version = "DocumentRAG/1.0"

        def _json(self, status: int, value: dict | list) -> None:
            body = json.dumps(value, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def _error(self, exc: Exception) -> None:
            if isinstance(exc, RAGError):
                self._json(exc.status, {"error": str(exc)})
            else:
                self.log_error("Unexpected error: %s", exc)
                self._json(500, {"error": "Lỗi máy chủ. Hãy xem nhật ký để biết chi tiết."})

        def _read_body(self, max_bytes: int) -> bytes:
            length = self.headers.get("Content-Length", "")
            if not length.isdigit():
                raise RAGError("Thiếu độ dài nội dung gửi lên.", 411)
            size = int(length)
            if size > max_bytes:
                raise RAGError("Nội dung gửi lên vượt quá giới hạn.", 413)
            return self.rfile.read(size)

        def _route(self) -> tuple[str, dict]:
            parsed = urlsplit(self.path)
            return parsed.path, parse_qs(parsed.query)

        def _check_origin(self) -> None:
            origin = self.headers.get("Origin")
            if origin and urlsplit(origin).netloc != self.headers.get("Host"):
                raise RAGError("Yêu cầu từ trang khác không được phép.", 403)

        def do_GET(self) -> None:
            try:
                path, _ = self._route()
                if path in STATIC:
                    file_path, content_type = STATIC[path]
                    body = file_path.read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("X-Content-Type-Options", "nosniff")
                    self.end_headers()
                    self.wfile.write(body)
                elif path == "/api/status":
                    self._json(200, {
                        "provider": "Gemini",
                        "configured": service.model.configured,
                        "chat_model": service.model.chat_model,
                        "embedding_model": service.model.embedding_model,
                        "document_count": len(service.list_documents()),
                    })
                elif path == "/api/documents":
                    self._json(200, {"documents": service.list_documents()})
                elif path.startswith("/api/documents/") and path.endswith("/file"):
                    doc_id = path.split("/")[3]
                    document = service.get_document(doc_id)
                    file_path = service.upload_dir / doc_id
                    if not file_path.is_file():
                        raise RAGError("Không tìm thấy tệp gốc.", 404)
                    content = file_path.read_bytes()
                    mime, _ = mimetypes.guess_type(document["filename"])
                    inline = Path(document["filename"]).suffix.lower() in {".pdf", ".txt", ".md"}
                    disposition = "inline" if inline else "attachment"
                    self.send_response(200)
                    self.send_header("Content-Type", mime or "application/octet-stream")
                    self.send_header("Content-Disposition", f"{disposition}; filename*=UTF-8''{quote(document['filename'])}")
                    self.send_header("Content-Length", str(len(content)))
                    self.send_header("X-Content-Type-Options", "nosniff")
                    self.end_headers()
                    self.wfile.write(content)
                else:
                    raise RAGError("Không tìm thấy đường dẫn.", 404)
            except Exception as exc:
                self._error(exc)

        def do_POST(self) -> None:
            try:
                self._check_origin()
                path, params = self._route()
                if path == "/api/documents":
                    filename = unquote(params.get("filename", [""])[0])
                    content = self._read_body(MAX_FILE_BYTES)
                    self._json(202, {"document": service.add_document(filename, content)})
                elif path.startswith("/api/documents/") and path.endswith("/reindex"):
                    service.reindex_document(path.split("/")[3])
                    self._json(202, {"document": service.get_document(path.split("/")[3])})
                elif path == "/api/chat":
                    payload = json.loads(self._read_body(64 * 1024))
                    if not isinstance(payload, dict) or not isinstance(payload.get("question"), str):
                        raise RAGError("Câu hỏi không hợp lệ.")
                    self._json(200, service.answer(payload["question"], payload.get("history")))
                else:
                    raise RAGError("Không tìm thấy đường dẫn.", 404)
            except json.JSONDecodeError:
                self._error(RAGError("JSON không hợp lệ."))
            except Exception as exc:
                self._error(exc)

        def do_DELETE(self) -> None:
            try:
                self._check_origin()
                path, _ = self._route()
                if path.startswith("/api/documents/") and path.count("/") == 3:
                    service.delete_document(path.split("/")[3])
                    self._json(200, {"deleted": True})
                else:
                    raise RAGError("Không tìm thấy đường dẫn.", 404)
            except Exception as exc:
                self._error(exc)

    return Handler


def main() -> None:
    load_local_env()
    host = os.getenv("RAG_HOST", "127.0.0.1")
    port = int(os.getenv("RAG_PORT", "8765"))
    model = GeminiClient(
        os.getenv("GEMINI_API_KEY", ""),
        os.getenv("RAG_CHAT_MODEL", "gemini-3.5-flash-lite"),
        os.getenv("RAG_EMBED_MODEL", "gemini-embedding-001"),
    )
    service = RAGService(Path(os.getenv("RAG_DATA_DIR", str(BASE_DIR / "data"))), model)
    server = ThreadingHTTPServer((host, port), make_handler(service))
    print(f"Document RAG đang chạy tại http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
