from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protect_audit import audit_texts  # noqa: E402


class ProtectAuditTests(unittest.TestCase):
    def test_identical_text_is_ok(self) -> None:
        text = "p95は480msから160msへ低下した。`timeout=30` を使う。"
        result = audit_texts(text, text)
        self.assertTrue(result.ok)
        self.assertEqual(result.differences, [])

    def test_numeric_change_is_high_severity(self) -> None:
        before = "p95は480msから160msへ低下した。"
        after = "p95は480msから150msへ低下した。"
        result = audit_texts(before, after)
        self.assertFalse(result.ok)
        number_diff = next(diff for diff in result.differences if diff.category == "numbers")
        self.assertEqual(number_diff.severity, "high")
        self.assertIn("160ms", number_diff.removed)
        self.assertIn("150ms", number_diff.added)

    def test_url_and_code_are_protected(self) -> None:
        before = "詳しくは https://example.com/a を参照し、`--timeout 30` を実行する。"
        after = "詳しくは https://example.com/b を参照し、`--timeout 20` を実行する。"
        result = audit_texts(before, after)
        categories = {diff.category for diff in result.differences}
        self.assertIn("urls", categories)
        self.assertIn("inline_code", categories)
        self.assertNotIn("paths", categories)


    def test_url_is_not_duplicated_as_path(self) -> None:
        before = "https://example.com/a を参照する。"
        after = "https://example.com/b を参照する。"
        result = audit_texts(before, after)
        categories = {diff.category for diff in result.differences}
        self.assertIn("urls", categories)
        self.assertNotIn("paths", categories)

    def test_certainty_change_is_reported(self) -> None:
        before = "原因は競合の可能性がある。"
        after = "原因は競合だ。"
        result = audit_texts(before, after)
        certainty_diff = next(diff for diff in result.differences if diff.category == "certainty")
        self.assertIn("可能性", certainty_diff.removed)
        # Certainty markers are medium severity; semantic review is still required.
        self.assertTrue(result.ok)


if __name__ == "__main__":
    unittest.main()
