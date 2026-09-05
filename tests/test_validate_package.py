from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_package import validate  # noqa: E402


class PackageValidationTests(unittest.TestCase):
    def test_current_package_is_structurally_valid(self) -> None:
        errors, _warnings = validate(ROOT)
        self.assertEqual(errors, [])

    def test_validator_rejects_missing_references_and_noncontiguous_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copied_root = Path(tmp) / "humanizer-ja-editor"
            shutil.copytree(
                ROOT,
                copied_root,
                ignore=shutil.ignore_patterns(".git", ".codex", "__pycache__", "*.pyc", "*.zip"),
            )
            (copied_root / "references" / "software-exposition.md").unlink()
            (copied_root / "references" / "beginner-explanation-profile.md").unlink()
            (copied_root / "references" / "guided-tutorial-profile.md").unlink()
            (copied_root / "references" / "troubleshooting-profile.md").unlink()
            (copied_root / "references" / "comparison-selection-profile.md").unlink()
            (copied_root / "evals" / "benchmark.jsonl").write_text(
                '{"id": "HJ-001"}\n{"id": "HJ-003"}\n',
                encoding="utf-8",
            )
            errors, _warnings = validate(copied_root)

        self.assertIn("Missing reference: references/software-exposition.md", errors)
        self.assertIn("Missing reference: references/beginner-explanation-profile.md", errors)
        self.assertIn("Missing reference: references/guided-tutorial-profile.md", errors)
        self.assertIn("Missing reference: references/troubleshooting-profile.md", errors)
        self.assertIn("Missing reference: references/comparison-selection-profile.md", errors)
        self.assertIn("Benchmark IDs must be unique and contiguous from HJ-001 through HJ-003", errors)

    def test_validator_rejects_invalid_or_missing_purpose_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copied_root = Path(tmp) / "humanizer-ja-editor"
            shutil.copytree(
                ROOT,
                copied_root,
                ignore=shutil.ignore_patterns(".git", ".codex", "__pycache__", "*.pyc", "*.zip"),
            )
            benchmark_path = copied_root / "evals" / "benchmark.jsonl"
            records = [
                json.loads(line)
                for line in benchmark_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]

            without_profiles = []
            for record in records:
                record = dict(record)
                record.pop("purpose_profile", None)
                without_profiles.append(record)
            benchmark_path.write_text(
                "\n".join(json.dumps(record, ensure_ascii=False) for record in without_profiles) + "\n",
                encoding="utf-8",
            )
            missing_errors, _warnings = validate(copied_root)

            invalid_records = [dict(record) for record in records]
            invalid_records[39]["purpose_profile"] = "winner-ranking"
            benchmark_path.write_text(
                "\n".join(json.dumps(record, ensure_ascii=False) for record in invalid_records) + "\n",
                encoding="utf-8",
            )
            invalid_errors, _warnings = validate(copied_root)

        self.assertIn(
            "Benchmark must cover all purpose profiles; missing: "
            "comparison-selection, guided-tutorial, troubleshooting",
            missing_errors,
        )
        self.assertIn(
            "Benchmark purpose_profile is invalid at evals/benchmark.jsonl:40: 'winner-ranking'",
            invalid_errors,
        )

    def test_validator_rejects_missing_or_invalid_openai_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copied_root = Path(tmp) / "humanizer-ja-editor"
            shutil.copytree(
                ROOT,
                copied_root,
                ignore=shutil.ignore_patterns(".git", ".codex", "__pycache__", "*.pyc", "*.zip"),
            )
            openai_path = copied_root / "agents" / "openai.yaml"
            openai_path.unlink()
            missing_errors, _warnings = validate(copied_root)

            openai_path.write_text(
                'interface:\n'
                '  display_name: "Humanizer JA Editor"\n'
                '  short_description: "短すぎます"\n'
                '  default_prompt: "次の文章を編集してください。"\n',
                encoding="utf-8",
            )
            invalid_errors, _warnings = validate(copied_root)

        self.assertIn("Missing agents/openai.yaml", missing_errors)
        self.assertIn(
            "agents/openai.yaml interface.short_description must be 25-64 characters",
            invalid_errors,
        )
        self.assertIn(
            "agents/openai.yaml interface.default_prompt must mention $humanizer-ja-editor",
            invalid_errors,
        )


if __name__ == "__main__":
    unittest.main()
