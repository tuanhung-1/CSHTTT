import tempfile
import unittest
import zipfile
import json
import urllib.error
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from rag_core import GeminiClient, RAGError, RAGService, extract_pages, split_text


class FakeModel:
    embedding_model = "test-embed"
    chat_model = "test-chat"
    configured = True

    def embed(self, texts, task_type="RETRIEVAL_DOCUMENT"):
        vectors = []
        for text in texts:
            text = text.lower()
            vectors.append([1.0, 0.0] if "hỗ trợ" in text else [0.0, 1.0])
        return vectors

    def chat(self, question, context, history):
        if "hỗ trợ" in context.lower():
            return "Hồ sơ cần giấy xác nhận. [1]"
        return "Tôi chưa tìm thấy thông tin này trong tài liệu đã nạp."


class RAGTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.service = RAGService(Path(self.temp.name), FakeModel(), background=False)

    def tearDown(self):
        self.temp.cleanup()

    def test_ingest_search_answer_and_delete(self):
        doc = self.service.add_document(
            "chinh-sach.txt",
            "Điều 1. Hỗ trợ học phí.\n\nHồ sơ cần giấy xác nhận của địa phương.".encode(),
        )
        self.service.index_document(doc["id"])
        self.assertEqual(self.service.get_document(doc["id"])["status"], "ready")
        matches = self.service.search("Hỗ trợ học phí cần giấy tờ gì?")
        self.assertEqual(matches[0]["filename"], "chinh-sach.txt")
        answer = self.service.answer("Hỗ trợ học phí cần giấy tờ gì?")
        self.assertIn("[1]", answer["answer"])
        self.assertEqual(answer["sources"][0]["document_id"], doc["id"])
        self.service.delete_document(doc["id"])
        self.assertEqual(self.service.list_documents(), [])
        self.assertFalse((Path(self.temp.name) / "uploads" / doc["id"]).exists())

    def test_docx_text_extraction(self):
        content = BytesIO()
        xml = b'''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Chinh sach</w:t></w:r></w:p><w:p><w:r><w:t>Ho tro hoc phi</w:t></w:r></w:p></w:body></w:document>'''
        with zipfile.ZipFile(content, "w") as archive:
            archive.writestr("word/document.xml", xml)
        path = Path(self.temp.name) / "sample.docx"
        path.write_bytes(content.getvalue())
        self.assertIn("Ho tro hoc phi", extract_pages(path, path.name)[0][1])

    def test_validation_and_empty_text(self):
        with self.assertRaises(RAGError):
            self.service.add_document("secret.exe", b"test")
        with self.assertRaises(RAGError):
            self.service.add_document("../empty.txt", b"")
        doc = self.service.add_document("blank.txt", b"  \n ")
        self.service.index_document(doc["id"])
        self.assertEqual(self.service.get_document(doc["id"])["status"], "failed")

    def test_long_paragraph_is_split_with_overlap(self):
        chunks = split_text("Một đoạn văn bản " * 300)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 1200 for chunk in chunks))

    def test_no_documents_does_not_call_chat(self):
        result = self.service.answer("Chính sách nào áp dụng?")
        self.assertEqual(result["sources"], [])
        self.assertIn("Chưa có tài liệu", result["answer"])

    def test_reindex_after_embedding_model_change(self):
        doc = self.service.add_document("policy.txt", "Hỗ trợ học phí".encode())
        self.service.index_document(doc["id"])
        self.service.model.embedding_model = "new-embed"
        self.assertTrue(self.service.get_document(doc["id"])["needs_reindex"])
        self.service.reindex_document(doc["id"])
        self.service.index_document(doc["id"])
        self.assertFalse(self.service.get_document(doc["id"])["needs_reindex"])
        self.assertEqual(self.service.get_document(doc["id"])["status"], "ready")

    def test_missing_key_rejects_upload(self):
        self.service.model.configured = False
        with self.assertRaisesRegex(RAGError, "GEMINI_API_KEY"):
            self.service.add_document("policy.txt", b"hello")


class GeminiClientTests(unittest.TestCase):
    def test_embedding_tasks_and_chat_request(self):
        calls = []

        def fake_open(request, timeout):
            payload = json.loads(request.data)
            calls.append((request, payload))
            if request.full_url.endswith(":batchEmbedContents"):
                return BytesIO(json.dumps({"embeddings": [{"values": [3.0, 4.0]} for _ in payload["requests"]]}).encode())
            return BytesIO(json.dumps({"candidates": [{"content": {"parts": [{"text": "Theo tài liệu [1]."}]}}]}).encode())

        client = GeminiClient("test-key", "gemini-test", "gemini-embedding-001", "https://example.test/v1beta")
        with patch("urllib.request.urlopen", side_effect=fake_open):
            self.assertEqual(client.embed(["văn bản"], "RETRIEVAL_DOCUMENT"), [[0.6, 0.8]])
            client.embed(["câu hỏi"], "RETRIEVAL_QUERY")
            self.assertEqual(client.chat("Hỏi gì?", "NGUỒN [1]", []), "Theo tài liệu [1].")
        self.assertEqual(calls[0][1]["requests"][0]["taskType"], "RETRIEVAL_DOCUMENT")
        self.assertEqual(calls[1][1]["requests"][0]["taskType"], "RETRIEVAL_QUERY")
        self.assertEqual(calls[2][1]["contents"][-1]["parts"][0]["text"], "Hỏi gì?")
        self.assertTrue(all(call[0].get_header("X-goog-api-key") == "test-key" for call in calls))

    def test_retries_temporary_503_then_succeeds(self):
        responses = [
            urllib.error.HTTPError("https://example.test", 503, "busy", {}, BytesIO(b"{}")),
            urllib.error.HTTPError("https://example.test", 503, "busy", {}, BytesIO(b"{}")),
            BytesIO(b'{"embeddings":[{"values":[3,4]}]}'),
        ]
        client = GeminiClient("test-key", "gemini-test", "gemini-embedding-001", "https://example.test/v1beta")
        with patch("urllib.request.urlopen", side_effect=responses) as call, patch("time.sleep") as sleep, patch("random.uniform", return_value=0):
            self.assertEqual(client.embed(["văn bản"]), [[0.6, 0.8]])
        self.assertEqual(call.call_count, 3)
        self.assertEqual([item.args[0] for item in sleep.call_args_list], [1, 2])

    def test_does_not_retry_nontransient_error(self):
        error = urllib.error.HTTPError(
            "https://example.test", 400, "bad request", {},
            BytesIO(b'{"error":{"message":"Invalid API key"}}'),
        )
        client = GeminiClient("test-key", "gemini-test", "gemini-embedding-001", "https://example.test/v1beta")
        with patch("urllib.request.urlopen", side_effect=error) as call, patch("time.sleep") as sleep:
            with self.assertRaisesRegex(RAGError, "Invalid API key"):
                client.embed(["văn bản"])
        self.assertEqual(call.call_count, 1)
        sleep.assert_not_called()

    def test_reports_overload_after_three_failures(self):
        def unavailable(request, timeout):
            raise urllib.error.HTTPError(request.full_url, 503, "busy", {}, BytesIO(b"{}"))

        client = GeminiClient("test-key", "gemini-test", "gemini-embedding-001", "https://example.test/v1beta")
        with patch("urllib.request.urlopen", side_effect=unavailable) as call, patch("time.sleep"), patch("random.uniform", return_value=0):
            with self.assertRaisesRegex(RAGError, "sau 3 lần thử") as error:
                client.embed(["văn bản"])
        self.assertEqual(error.exception.status, 503)
        self.assertEqual(call.call_count, 3)


if __name__ == "__main__":
    unittest.main()
