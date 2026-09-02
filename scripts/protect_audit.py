#!/usr/bin/env python3
"""Compare protected textual spans before and after an edit.

This is a conservative static guardrail, not a semantic-equivalence proof.
It reports removed and added numbers, dates, URLs, code, paths, versions,
quoted spans, certainty markers, and polarity markers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


FENCED_CODE_RE = re.compile(r"(?ms)^(```|~~~).*?^\1\s*$")
INLINE_CODE_RE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
URL_RE = re.compile(r"https?://[^\s<>{}\[\]）)」』]+", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
MARKDOWN_TARGET_RE = re.compile(r"\]\(([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)")
ISO_DATE_RE = re.compile(r"(?<!\d)\d{4}[-/]\d{1,2}[-/]\d{1,2}(?!\d)")
JP_DATE_RE = re.compile(r"(?<!\d)\d{4}年\s*\d{1,2}月(?:\s*\d{1,2}日)?")
JP_SHORT_DATE_RE = re.compile(r"(?<!\d)\d{1,2}月\s*\d{1,2}日")
VERSION_RE = re.compile(
    r"(?<![0-9A-Za-z_.])(?:v|ver\.?\s*)?\d+\.\d+(?:\.\d+)+(?:[-+][A-Za-z0-9.-]+)?(?![0-9A-Za-z_.])",
    re.IGNORECASE,
)
RANGE_RE = re.compile(
    r"(?<![0-9A-Za-z_.])(?:約|およそ|最大|最小|少なくとも)?\s*[+-]?\d[\d,]*(?:\.\d+)?\s*"
    r"(?:〜|~|–|—|－|-)\s*[+-]?\d[\d,]*(?:\.\d+)?\s*"
    r"(?:%|％|ms|秒|分|時間|日|週|か月|ヶ月|月|年|KB|MB|GB|TB|KiB|MiB|GiB|"
    r"Hz|kHz|MHz|GHz|px|pt|円|万円|億円|人|件|回|倍|個|台|本|文字|字|語|"
    r"tokens?|km|cm|mm|kg|℃|°C|V|A|W)?",
    re.IGNORECASE,
)
NUMBER_RE = re.compile(
    r"(?<![0-9A-Za-z_.])(?:約|およそ|最大|最小|少なくとも)?\s*[+-]?\d[\d,]*(?:\.\d+)?\s*"
    r"(?:%|％|ms|秒|分|時間|日|週|か月|ヶ月|月|年|KB|MB|GB|TB|KiB|MiB|GiB|"
    r"Hz|kHz|MHz|GHz|px|pt|円|万円|億円|人|件|回|倍|個|台|本|文字|字|語|"
    r"tokens?|km|cm|mm|kg|℃|°C|V|A|W)?(?![0-9A-Za-z_.])",
    re.IGNORECASE,
)
UNIX_PATH_RE = re.compile(r"(?<![\w:])(?:\.{0,2}/|/)[A-Za-z0-9._~+@%=-]+(?:/[A-Za-z0-9._~+@%=-]+)+/?")
WINDOWS_PATH_RE = re.compile(r"\b[A-Za-z]:\\(?:[^\\\s:*?\"<>|]+\\)*[^\\\s:*?\"<>|]*")
CLI_FLAG_RE = re.compile(r"(?<!\w)--[A-Za-z0-9][A-Za-z0-9_-]*")
ENV_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
JP_QUOTE_RE = re.compile(r"[「『]([^」』\n]{2,200})[」』]")
EN_QUOTE_RE = re.compile(r"(?<!\w)[\"“]([^\"”\n]{4,200})[\"”]")

CERTAINTY_TERMS = (
    "可能性",
    "推定",
    "予定",
    "見込み",
    "未確認",
    "仮説",
    "約",
    "およそ",
    "最大",
    "最小",
    "少なくとも",
    "現時点",
    "とみられる",
    "と考えられる",
    "かもしれない",
    "may",
    "might",
    "likely",
    "estimated",
    "planned",
    "approximately",
)

POLARITY_TERMS = (
    "できない",
    "ではない",
    "しない",
    "含まない",
    "未対応",
    "無効",
    "禁止",
    "不要",
    "失敗",
    "not",
    "cannot",
    "can't",
    "without",
    "disabled",
    "failed",
    "forbidden",
)

HIGH_SEVERITY = {
    "fenced_code",
    "inline_code",
    "urls",
    "emails",
    "markdown_targets",
    "dates",
    "versions",
    "ranges",
    "numbers",
    "paths",
    "cli_flags",
}


@dataclass(frozen=True)
class Difference:
    category: str
    severity: str
    removed: list[str]
    added: list[str]


@dataclass(frozen=True)
class AuditResult:
    ok: bool
    differences: list[Difference]
    before_counts: dict[str, int]
    after_counts: dict[str, int]


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"\s+", " ", value).strip()
    value = value.rstrip(".,;:、。）」』】]")
    # Numeric formatting differences such as 1,000 vs 1000 should not dominate.
    if re.search(r"\d", value):
        value = re.sub(r"(?<=\d),(?=\d{3}(?:\D|$))", "", value)
    return value


def hash_block(value: str) -> str:
    normalized = normalize(value)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
    first_line = normalized.splitlines()[0][:60] if normalized else ""
    return f"sha256:{digest}:{first_line}"


def counter_from(values: Iterable[str], *, hash_values: bool = False) -> Counter[str]:
    result: Counter[str] = Counter()
    for value in values:
        normalized = hash_block(value) if hash_values else normalize(value)
        if normalized:
            result[normalized] += 1
    return result


def term_counter(text: str, terms: Iterable[str]) -> Counter[str]:
    normalized_text = unicodedata.normalize("NFKC", text).lower()
    result: Counter[str] = Counter()
    for term in terms:
        normalized_term = unicodedata.normalize("NFKC", term).lower()
        count = normalized_text.count(normalized_term)
        if count:
            result[normalized_term] = count
    return result


def extract(text: str) -> dict[str, Counter[str]]:
    fenced_full = [match.group(0) for match in FENCED_CODE_RE.finditer(text)]
    inline_code = INLINE_CODE_RE.findall(text)
    urls = URL_RE.findall(text)
    emails = EMAIL_RE.findall(text)
    markdown_targets = MARKDOWN_TARGET_RE.findall(text)

    # Avoid reporting numeric/path fragments a second time when the exact code or
    # URL span is already protected by a stronger category.
    analysis_source = FENCED_CODE_RE.sub(" ", text)
    analysis_source = INLINE_CODE_RE.sub(" ", analysis_source)
    analysis_source = URL_RE.sub(" ", analysis_source)
    analysis_source = EMAIL_RE.sub(" ", analysis_source)

    long_date_source = ISO_DATE_RE.sub(" ", analysis_source)
    long_date_source = JP_DATE_RE.sub(" ", long_date_source)
    dates = (
        list(ISO_DATE_RE.findall(analysis_source))
        + list(JP_DATE_RE.findall(analysis_source))
        + list(JP_SHORT_DATE_RE.findall(long_date_source))
    )
    numeric_source = ISO_DATE_RE.sub(" ", analysis_source)
    numeric_source = JP_DATE_RE.sub(" ", numeric_source)
    numeric_source = JP_SHORT_DATE_RE.sub(" ", numeric_source)
    numeric_source = VERSION_RE.sub(" ", numeric_source)
    numeric_source = RANGE_RE.sub(" ", numeric_source)

    paths = list(UNIX_PATH_RE.findall(analysis_source)) + list(WINDOWS_PATH_RE.findall(analysis_source))
    quotes = list(JP_QUOTE_RE.findall(text)) + list(EN_QUOTE_RE.findall(text))

    return {
        "fenced_code": counter_from(fenced_full, hash_values=True),
        "inline_code": counter_from(inline_code),
        "urls": counter_from(urls),
        "emails": counter_from(emails),
        "markdown_targets": counter_from(markdown_targets),
        "dates": counter_from(dates),
        "versions": counter_from(VERSION_RE.findall(analysis_source)),
        "ranges": counter_from(RANGE_RE.findall(analysis_source)),
        "numbers": counter_from(NUMBER_RE.findall(numeric_source)),
        "paths": counter_from(paths),
        "cli_flags": counter_from(CLI_FLAG_RE.findall(analysis_source)),
        "identifiers": counter_from(ENV_RE.findall(analysis_source)),
        "quoted_spans": counter_from(quotes),
        "certainty": term_counter(text, CERTAINTY_TERMS),
        "polarity": term_counter(text, POLARITY_TERMS),
    }


def expanded_difference(before: Counter[str], after: Counter[str]) -> tuple[list[str], list[str]]:
    removed_counter = before - after
    added_counter = after - before
    removed = [item for item, count in sorted(removed_counter.items()) for _ in range(count)]
    added = [item for item, count in sorted(added_counter.items()) for _ in range(count)]
    return removed, added


def audit_texts(before_text: str, after_text: str) -> AuditResult:
    before = extract(before_text)
    after = extract(after_text)
    differences: list[Difference] = []

    for category in before.keys():
        removed, added = expanded_difference(before[category], after[category])
        if removed or added:
            severity = "high" if category in HIGH_SEVERITY else "medium"
            differences.append(Difference(category, severity, removed, added))

    high_difference = any(diff.severity == "high" for diff in differences)
    return AuditResult(
        ok=not high_difference,
        differences=differences,
        before_counts={key: sum(value.values()) for key, value in before.items()},
        after_counts={key: sum(value.values()) for key, value in after.items()},
    )


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def print_human(result: AuditResult) -> None:
    if not result.differences:
        print("OK: 保護対象の文字列差分は検出されませんでした。")
        return

    print("保護対象の差分を検出しました。意味関係は別途確認してください。")
    for diff in result.differences:
        print(f"\n[{diff.severity.upper()}] {diff.category}")
        if diff.removed:
            print("  removed:")
            for item in diff.removed:
                print(f"    - {item}")
        if diff.added:
            print("  added:")
            for item in diff.added:
                print(f"    + {item}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path, help="編集前のUTF-8テキスト")
    parser.add_argument("after", type=Path, help="編集後のUTF-8テキスト")
    parser.add_argument("--json", action="store_true", help="JSONで出力")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="medium差分も終了コード1にする（既定はhigh差分のみ）",
    )
    args = parser.parse_args()

    if not args.before.is_file() or not args.after.is_file():
        parser.error("beforeとafterには存在するファイルを指定してください")

    result = audit_texts(read_text(args.before), read_text(args.after))
    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print_human(result)

    if args.strict and result.differences:
        return 1
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
