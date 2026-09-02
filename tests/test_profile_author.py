from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from profile_author import build_profile, collect_files  # noqa: E402


class ProfileAuthorTests(unittest.TestCase):
    def test_profile_contains_basic_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.md"
            path.write_text(
                "# 見出し\n\n私はこの方法がいいと思います。短い文です。\n\n"
                "ただし、条件によって結果は変わるかもしれません。\n",
                encoding="utf-8",
            )
            files = collect_files([path])
            profile = build_profile(files)

        self.assertEqual(profile["source"]["file_count"], 1)
        self.assertGreaterEqual(profile["sentence_metrics"]["count"], 3)
        self.assertEqual(profile["style_markers"]["markdown"]["headings"], 1)
        self.assertIn("と思う", profile["style_markers"]["sentence_endings"])
        self.assertIn("私", profile["style_markers"]["first_person_per_1000_chars"])

    def test_directory_collection_filters_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("文章です。", encoding="utf-8")
            (root / "b.py").write_text("print('x')", encoding="utf-8")
            files = collect_files([root])
        self.assertEqual([path.name for path in files], ["a.txt"])


if __name__ == "__main__":
    unittest.main()
