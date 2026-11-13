import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import load_local_env


class LocalEnvTests(unittest.TestCase):
    def test_loads_env_file_without_overriding_shell(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text(
                "# cau hinh\nGEMINI_API_KEY=file-key\nRAG_CHAT_MODEL='gemini-test'\nUNKNOWN=value\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {"GEMINI_API_KEY": "shell-key"}, clear=True):
                load_local_env(path)
                self.assertEqual(os.environ["GEMINI_API_KEY"], "shell-key")
                self.assertEqual(os.environ["RAG_CHAT_MODEL"], "gemini-test")
                self.assertNotIn("UNKNOWN", os.environ)


if __name__ == "__main__":
    unittest.main()
