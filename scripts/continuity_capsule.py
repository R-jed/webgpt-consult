#!/usr/bin/env python3
"""Validate a compact continuity capsule used for ChatGPT conversation rollover."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

CAPSULE_HEADER = "CONTINUITY_CAPSULE_V1"
REQUIRED_HEADINGS = (
    "## WORKSTREAM",
    "## BASELINE",
    "## USER_INTENT",
    "## STANDING_CONSTRAINTS",
    "## ACCEPTED_DECISIONS",
    "## REJECTED_OR_DEFERRED_PATHS",
    "## OPEN_QUESTIONS",
    "## EVIDENCE_INDEX",
    "## CURRENT_STATE",
    "## CURRENT_ASK",
    "## COVERAGE_ATTESTATION",
)
DEFAULT_MAX_CHARS = 12_000


def _section_has_content(lines: list[str], heading: str) -> bool:
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return False
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if stripped:
            return True
    return False


def validate_capsule(
    text: str,
    *,
    base_task_id: str,
    last_task_id: str,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> dict:
    errors: list[str] = []
    stripped = text.strip()
    lines = stripped.splitlines()

    if not lines or lines[0].strip() != CAPSULE_HEADER:
        errors.append(f"first line must be {CAPSULE_HEADER}")

    if len(text) > max_chars:
        errors.append(f"capsule exceeds max chars: {len(text)} > {max_chars}")

    for heading in REQUIRED_HEADINGS:
        if heading not in lines:
            errors.append(f"missing heading: {heading}")
        elif not _section_has_content(lines, heading):
            errors.append(f"empty section: {heading}")

    required_markers = (
        f"Base-Task-ID: {base_task_id}",
        f"Last-Task-ID: {last_task_id}",
        "Material-Reusable-Context-Omitted: no",
    )
    for marker in required_markers:
        if marker not in lines:
            errors.append(f"missing exact coverage marker: {marker}")

    return {
        "ok": not errors,
        "char_count": len(text),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "base_task_id": base_task_id,
        "last_task_id": last_task_id,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capsule", type=Path)
    parser.add_argument("--base-task-id", required=True)
    parser.add_argument("--last-task-id", required=True)
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    args = parser.parse_args()

    try:
        text = args.capsule.read_text(encoding="utf-8")
        result = validate_capsule(
            text,
            base_task_id=args.base_task_id,
            last_task_id=args.last_task_id,
            max_chars=args.max_chars,
        )
    except Exception as exc:
        result = {"ok": False, "errors": [str(exc)]}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
