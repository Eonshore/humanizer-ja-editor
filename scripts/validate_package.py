#!/usr/bin/env python3
"""Validate the Humanizer JA Editor Agent Skill package without dependencies."""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
BENCHMARK_ID_RE = re.compile(r"^HJ-(\d{3,})$")
ALLOWED_PURPOSE_PROFILES = {
    "guided-tutorial",
    "troubleshooting",
    "comparison-selection",
}
OPENAI_INTERFACE_FIELD_RE = re.compile(
    r'^  ([a-z_]+):\s*("(?:[^"\\]|\\.)*")\s*$'
)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter is not closed")
    raw = text[4:end]
    body = text[end + 5 :]
    metadata: dict[str, str] = {}
    current_key: str | None = None
    block_lines: list[str] = []

    def flush_block() -> None:
        nonlocal current_key, block_lines
        if current_key is not None:
            metadata[current_key] = "\n".join(line.strip() for line in block_lines).strip()
        current_key = None
        block_lines = []

    for line in raw.splitlines():
        if current_key is not None:
            if line.startswith("  ") or not line.strip():
                block_lines.append(line)
                continue
            flush_block()
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.groups()
        if value in {"|", ">"}:
            current_key = key
            block_lines = []
        elif not line.startswith("  "):
            metadata[key] = value.strip().strip('"\'')
    flush_block()
    return metadata, body


def parse_openai_interface(text: str) -> dict[str, str]:
    """Parse the flat string fields used by the interface block."""

    lines = text.splitlines()
    interface_indexes = [index for index, line in enumerate(lines) if line == "interface:"]
    if len(interface_indexes) != 1:
        raise ValueError("agents/openai.yaml must contain exactly one interface block")

    fields: dict[str, str] = {}
    for line in lines[interface_indexes[0] + 1 :]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith("  "):
            break
        match = OPENAI_INTERFACE_FIELD_RE.fullmatch(line)
        if not match:
            raise ValueError(f"agents/openai.yaml has an invalid interface field: {line!r}")
        key, raw_value = match.groups()
        if key in fields:
            raise ValueError(f"agents/openai.yaml repeats interface.{key}")
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"agents/openai.yaml has an invalid quoted value for interface.{key}") from exc
        if not isinstance(value, str):
            raise ValueError(f"agents/openai.yaml interface.{key} must be a string")
        fields[key] = value
    return fields


def validate(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        return ["Missing SKILL.md"], warnings

    text = skill_path.read_text(encoding="utf-8")
    try:
        metadata, body = parse_frontmatter(text)
    except ValueError as exc:
        return [str(exc)], warnings

    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not name:
        errors.append("frontmatter.name is required")
    elif not NAME_RE.fullmatch(name):
        errors.append(f"frontmatter.name is invalid: {name!r}")
    elif len(name) > 64:
        errors.append("frontmatter.name exceeds 64 characters")
    if name and name != root.name:
        errors.append(f"frontmatter.name {name!r} does not match directory {root.name!r}")

    if not description:
        errors.append("frontmatter.description is required")
    elif len(description) > 1024:
        errors.append("frontmatter.description exceeds 1024 characters")

    openai_path = root / "agents" / "openai.yaml"
    if not openai_path.is_file():
        errors.append("Missing agents/openai.yaml")
    else:
        try:
            interface = parse_openai_interface(openai_path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(str(exc))
        else:
            required_interface_fields = {"display_name", "short_description", "default_prompt"}
            for missing in sorted(required_interface_fields - set(interface)):
                errors.append(f"Missing agents/openai.yaml interface.{missing}")

            display_name = interface.get("display_name", "")
            if "display_name" in interface and not display_name.strip():
                errors.append("agents/openai.yaml interface.display_name must not be empty")

            short_description = interface.get("short_description", "")
            if "short_description" in interface and not 25 <= len(short_description) <= 64:
                errors.append("agents/openai.yaml interface.short_description must be 25-64 characters")

            default_prompt = interface.get("default_prompt", "")
            if "default_prompt" in interface and name and f"${name}" not in default_prompt:
                errors.append(f"agents/openai.yaml interface.default_prompt must mention ${name}")

    body_lines = body.splitlines()
    if len(body_lines) > 500:
        warnings.append(f"SKILL.md body has {len(body_lines)} lines; recommended maximum is 500")
    if len(body) > 30000:
        warnings.append(f"SKILL.md body is {len(body)} characters; consider further progressive disclosure")

    for target in LINK_RE.findall(body):
        target = target.strip().split("#", 1)[0]
        if not target or re.match(r"^[a-z]+://", target, re.IGNORECASE) or target.startswith("mailto:"):
            continue
        resolved = (root / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"Relative link escapes skill directory: {target}")
            continue
        if not resolved.exists():
            errors.append(f"Broken relative link in SKILL.md: {target}")

    required_references = {
        "fidelity-contract.md",
        "easy-japanese.md",
        "conversation-continuity.md",
        "technical-writing.md",
        "manuscript-style.md",
        "scene-profiles.md",
        "japanese-patterns.md",
        "reader-flow.md",
        "software-exposition.md",
        "beginner-explanation-profile.md",
        "guided-tutorial-profile.md",
        "troubleshooting-profile.md",
        "comparison-selection-profile.md",
        "rewrite-operations.md",
        "author-profile.md",
        "output-modes.md",
        "boundary-cases.md",
    }
    reference_dir = root / "references"
    existing_references = {path.name for path in reference_dir.glob("*.md")} if reference_dir.is_dir() else set()
    for missing in sorted(required_references - existing_references):
        errors.append(f"Missing reference: references/{missing}")

    for script in sorted((root / "scripts").glob("*.py")):
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"Python compile error in {script.name}: {exc.msg}")

    for json_path in sorted((root / "assets").glob("*.json")):
        try:
            json.loads(json_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Invalid JSON in {json_path.relative_to(root)}: {exc}")

    for jsonl_path in sorted((root / "evals").glob("*.jsonl")):
        benchmark_ids: list[int] = []
        seen_benchmark_ids: set[int] = set()
        seen_purpose_profiles: set[str] = set()
        for lineno, line in enumerate(jsonl_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"Invalid JSONL in {jsonl_path.relative_to(root)}:{lineno}: {exc}")
                continue
            if jsonl_path.name != "benchmark.jsonl":
                continue
            if not isinstance(record, dict):
                errors.append(f"Benchmark record is not an object at {jsonl_path.relative_to(root)}:{lineno}")
                continue
            raw_id = record.get("id")
            if not isinstance(raw_id, str):
                errors.append(f"Benchmark record has no string id at {jsonl_path.relative_to(root)}:{lineno}")
                continue
            match = BENCHMARK_ID_RE.fullmatch(raw_id)
            if not match:
                errors.append(f"Benchmark id is invalid at {jsonl_path.relative_to(root)}:{lineno}: {raw_id!r}")
                continue
            numeric_id = int(match.group(1))
            if numeric_id in seen_benchmark_ids:
                errors.append(f"Benchmark id is duplicated at {jsonl_path.relative_to(root)}:{lineno}: {raw_id}")
                continue
            seen_benchmark_ids.add(numeric_id)
            benchmark_ids.append(numeric_id)

            raw_purpose_profile = record.get("purpose_profile")
            if raw_purpose_profile is not None:
                if not isinstance(raw_purpose_profile, str):
                    errors.append(
                        "Benchmark purpose_profile must be a string at "
                        f"{jsonl_path.relative_to(root)}:{lineno}"
                    )
                elif raw_purpose_profile not in ALLOWED_PURPOSE_PROFILES:
                    errors.append(
                        "Benchmark purpose_profile is invalid at "
                        f"{jsonl_path.relative_to(root)}:{lineno}: {raw_purpose_profile!r}"
                    )
                else:
                    seen_purpose_profiles.add(raw_purpose_profile)

        if jsonl_path.name == "benchmark.jsonl" and benchmark_ids:
            expected_ids = list(range(1, max(benchmark_ids) + 1))
            if sorted(benchmark_ids) != expected_ids:
                errors.append(
                    "Benchmark IDs must be unique and contiguous from HJ-001 through "
                    f"HJ-{max(benchmark_ids):03d}"
                )
            missing_purpose_profiles = ALLOWED_PURPOSE_PROFILES - seen_purpose_profiles
            if missing_purpose_profiles:
                errors.append(
                    "Benchmark must cover all purpose profiles; missing: "
                    + ", ".join(sorted(missing_purpose_profiles))
                )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()

    errors, warnings = validate(root)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1
    print(f"OK: {root} is structurally valid ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
