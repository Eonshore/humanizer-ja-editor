#!/usr/bin/env python3
"""Create a lightweight Japanese author-style profile from text/Markdown files.

No morphological analyzer is required. The output is descriptive evidence for
an editor, not a generator specification and not an authorship classifier.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

SUPPORTED = {".txt", ".md", ".markdown", ".rst"}
FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
FENCED_CODE_RE = re.compile(r"(?ms)^(```|~~~).*?^\1\s*$")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
HTML_TAG_RE = re.compile(r"<[^>]+>")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？!?])(?:[」』）】\]]*)\s*|\n+(?=[^\s#>*+-])")
PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n+")

CONNECTIVES = (
    "また",
    "さらに",
    "加えて",
    "一方で",
    "しかし",
    "しかしながら",
    "ただし",
    "とはいえ",
    "そのため",
    "したがって",
    "このため",
    "これにより",
    "つまり",
    "たとえば",
    "例えば",
    "なお",
    "まず",
    "次に",
    "最後に",
    "結局",
    "正直",
)

FIRST_PERSON = ("私", "わたし", "僕", "ぼく", "俺", "自分", "我々", "われわれ", "筆者", "本稿", "本研究")
SECOND_PERSON = ("あなた", "君", "きみ", "皆さん", "みなさん", "読者", "ユーザー")

ENDING_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("と思う", re.compile(r"(?:と|ように)思(?:う|います|った|いました)[。！？!?]?$")),
    ("と考える", re.compile(r"と考え(?:る|ます|られる|ています)[。！？!?]?$")),
    ("かもしれない", re.compile(r"かもしれ(?:ない|ません)[。！？!?]?$")),
    ("でしょう", re.compile(r"でしょう[。！？!?]?$")),
    ("である", re.compile(r"であ(?:る|った)[。！？!?]?$")),
    ("です", re.compile(r"(?:です|でした)[。！？!?]?$")),
    ("ます", re.compile(r"(?:ます|ました|ません|ましょう)[。！？!?]?$")),
    ("だ", re.compile(r"(?:だ|だった)[。！？!?]?$")),
    ("疑問", re.compile(r"[？?]$")),
    ("感嘆", re.compile(r"[！!]$")),
)

PUNCTUATION = {
    "読点": "、",
    "句点": "。",
    "疑問符": "？?",
    "感嘆符": "！!",
    "丸括弧": "（）()",
    "鉤括弧": "「」",
    "二重鉤括弧": "『』",
    "三点リーダー": "…",
    "ダッシュ": "—–―─",
    "コロン": ":：",
    "セミコロン": ";；",
    "中黒": "・",
}


def percentile(values: list[int], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def round2(value: float) -> float:
    return round(value, 2)


def collect_files(inputs: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for item in inputs:
        if item.is_dir():
            files.extend(path for path in item.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED)
        elif item.is_file() and item.suffix.lower() in SUPPORTED:
            files.append(item)
    return sorted(set(path.resolve() for path in files), key=lambda path: str(path).lower())


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def clean_text(text: str) -> tuple[str, dict[str, int]]:
    code_blocks = len(list(FENCED_CODE_RE.finditer(text)))
    headings = len(re.findall(r"(?m)^#{1,6}\s+\S", text))
    list_items = len(re.findall(r"(?m)^\s*(?:[-*+] |\d+[.)]\s+)", text))
    bold_spans = len(re.findall(r"\*\*[^*\n]+\*\*|__[^_\n]+__", text))

    text = FRONTMATTER_RE.sub("", text)
    text = FENCED_CODE_RE.sub("\n", text)
    text = INLINE_CODE_RE.sub("", text)
    text = MARKDOWN_LINK_RE.sub(r"\1", text)
    text = HTML_TAG_RE.sub("", text)
    text = re.sub(r"(?m)^#{1,6}\s+", "", text)
    text = re.sub(r"(?m)^\s*(?:[-*+] |\d+[.)]\s+)", "", text)
    text = re.sub(r"\*\*|__", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip(), {
        "headings": headings,
        "list_items": list_items,
        "bold_spans": bold_spans,
        "code_blocks": code_blocks,
    }


def split_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    for part in SENTENCE_SPLIT_RE.split(text):
        candidate = part.strip()
        if not candidate:
            continue
        candidate = re.sub(r"\s+", " ", candidate)
        if candidate:
            sentences.append(candidate)
    return sentences


def split_paragraphs(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", part).strip() for part in PARAGRAPH_SPLIT_RE.split(text) if part.strip()]


def ending_label(sentence: str) -> str:
    stripped = sentence.strip()
    for label, pattern in ENDING_PATTERNS:
        if pattern.search(stripped):
            return label
    ending = re.sub(r"[。！？!?」』）】\]]+$", "", stripped)
    if re.search(r"[一-龯々ァ-ヶーA-Za-z0-9]$", ending):
        return "その他・体言止め候補"
    return "その他"


def per_1000(count: int, total_chars: int) -> float:
    return round2(count * 1000 / max(total_chars, 1))


def build_profile(files: list[Path]) -> dict:
    raw_texts = [load_text(path) for path in files]
    markdown_totals: Counter[str] = Counter()
    cleaned_texts: list[str] = []
    for raw in raw_texts:
        cleaned, markdown = clean_text(raw)
        cleaned_texts.append(cleaned)
        markdown_totals.update(markdown)

    combined = "\n\n".join(cleaned_texts)
    total_chars = len(re.sub(r"\s", "", combined))
    sentences = split_sentences(combined)
    paragraphs = split_paragraphs(combined)
    sentence_lengths = [len(re.sub(r"\s", "", sentence)) for sentence in sentences]
    paragraph_sentence_counts = [len(split_sentences(paragraph)) for paragraph in paragraphs]

    endings = Counter(ending_label(sentence) for sentence in sentences)
    connectives = {term: combined.count(term) for term in CONNECTIVES if combined.count(term)}
    first_person = {term: combined.count(term) for term in FIRST_PERSON if combined.count(term)}
    second_person = {term: combined.count(term) for term in SECOND_PERSON if combined.count(term)}

    punctuation_counts: dict[str, int] = {}
    for label, chars in PUNCTUATION.items():
        if label == "三点リーダー":
            punctuation_counts[label] = combined.count("…")
        else:
            punctuation_counts[label] = sum(combined.count(char) for char in chars)

    frequent_endings = Counter()
    for sentence in sentences:
        stripped = re.sub(r"\s+", "", sentence)
        stripped = re.sub(r"[。！？!?」』）】\]]+$", "", stripped)
        if stripped:
            frequent_endings[stripped[-6:]] += 1

    warning = None
    if total_chars < 1000:
        warning = "サンプルが1000字未満です。偶然の表現を作者特性と誤認する可能性があります。"
    elif len(files) < 2:
        warning = "ファイルが1件だけです。別の文章でも傾向を確認してください。"

    mean_sentence = statistics.mean(sentence_lengths) if sentence_lengths else 0.0
    median_sentence = statistics.median(sentence_lengths) if sentence_lengths else 0.0
    mean_paragraph = statistics.mean(paragraph_sentence_counts) if paragraph_sentence_counts else 0.0
    median_paragraph = statistics.median(paragraph_sentence_counts) if paragraph_sentence_counts else 0.0
    single_ratio = (
        sum(1 for count in paragraph_sentence_counts if count == 1) / len(paragraph_sentence_counts)
        if paragraph_sentence_counts
        else 0.0
    )

    return {
        "schema_version": "1.0",
        "source": {
            "files": [str(path) for path in files],
            "file_count": len(files),
            "total_characters": total_chars,
            "sample_warning": warning,
        },
        "sentence_metrics": {
            "count": len(sentences),
            "length_chars": {
                "mean": round2(mean_sentence),
                "median": round2(float(median_sentence)),
                "p10": round2(percentile(sentence_lengths, 0.10)),
                "p90": round2(percentile(sentence_lengths, 0.90)),
                "min": min(sentence_lengths) if sentence_lengths else 0,
                "max": max(sentence_lengths) if sentence_lengths else 0,
            },
        },
        "paragraph_metrics": {
            "count": len(paragraphs),
            "sentences_per_paragraph": {
                "mean": round2(mean_paragraph),
                "median": round2(float(median_paragraph)),
            },
            "single_sentence_paragraph_ratio": round2(single_ratio),
        },
        "style_markers": {
            "sentence_endings": dict(endings.most_common()),
            "frequent_last_6_chars": dict(frequent_endings.most_common(20)),
            "connectives_per_1000_chars": {
                term: per_1000(count, total_chars) for term, count in connectives.items()
            },
            "first_person_per_1000_chars": {
                term: per_1000(count, total_chars) for term, count in first_person.items()
            },
            "second_person_per_1000_chars": {
                term: per_1000(count, total_chars) for term, count in second_person.items()
            },
            "punctuation_per_1000_chars": {
                label: per_1000(count, total_chars) for label, count in punctuation_counts.items()
            },
            "markdown": dict(markdown_totals),
        },
        "interpretation_notes": [
            "数値は作者性の証明ではなく、対象文との比較材料として使う。",
            "サンプルの場面が対象文と異なる場合、場面差を作者差と誤認しない。",
            "元文にない体験・感情・数字・出典・固有名詞は追加しない。",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="テキストファイルまたはディレクトリ")
    parser.add_argument("--output", "-o", type=Path, default=Path("author-profile.json"))
    args = parser.parse_args()

    files = collect_files(args.inputs)
    if not files:
        parser.error("対応する .txt/.md/.markdown/.rst ファイルが見つかりません")

    profile = build_profile(files)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} from {len(files)} file(s).")
    if profile["source"]["sample_warning"]:
        print(f"Warning: {profile['source']['sample_warning']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
