#!/usr/bin/env python3
"""Minimal fail-closed guard for secrets, authentication material, and payment credentials."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PATTERNS = [
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("gitlab_token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b")),
    ("openai_key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("anthropic_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("stripe_live_key", re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("npm_token", re.compile(r"\bnpm_[A-Za-z0-9]{20,}\b")),
    ("huggingface_token", re.compile(r"\bhf_[A-Za-z0-9]{20,}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("authorization_header", re.compile(r"(?i)\bAuthorization\s*:\s*(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{12,}")),
    ("cookie_header", re.compile(r"(?i)\bCookie\s*:\s*[^\n]{20,}")),
    ("credential_assignment", re.compile(
        r"(?i)\b(?:token|api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|"
        r"session[_-]?token|auth[_-]?token|bearer[_-]?token|aws[_-]?secret[_-]?access[_-]?key|"
        r"password|passwd|pwd|secret|otp|one[_-]?time[_-]?password|recovery[_-]?code|"
        r"cvv|cvc|card[_-]?pin|payment[_-]?pin)\s*[:=]\s*"
        r"(?:['\"][^'\"\n]{3,}['\"]|[^\s'\"]{3,})"
    )),
]

CARD_CANDIDATE_RE = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")


def _luhn_valid(digits: str) -> bool:
    if not 13 <= len(digits) <= 19 or len(set(digits)) == 1:
        return False
    total = 0
    parity = len(digits) % 2
    for i, ch in enumerate(digits):
        value = int(ch)
        if i % 2 == parity:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def _excerpt(text: str, start: int, end: int) -> str:
    matched = text[start:end]
    if ":" in matched or "=" in matched:
        key = re.split(r"[:=]", matched, maxsplit=1)[0].strip()
        return f"{key}=<REDACTED>" if key else "<REDACTED>"
    return "<REDACTED>"


def scan(text: str) -> list[dict]:
    findings: list[dict] = []
    for kind, pattern in PATTERNS:
        for match in pattern.finditer(text):
            findings.append({
                "type": kind,
                "start": match.start(),
                "end": match.end(),
                "excerpt": _excerpt(text, match.start(), match.end()),
            })

    for match in CARD_CANDIDATE_RE.finditer(text):
        digits = re.sub(r"\D", "", match.group(0))
        if _luhn_valid(digits):
            findings.append({
                "type": "payment_card_number",
                "start": match.start(),
                "end": match.end(),
                "excerpt": f"<CARD_REDACTED_LAST4_{digits[-4:]}>",
            })

    return sorted(findings, key=lambda item: (item["start"], item["end"], item["type"]))


def _read_input(value: str) -> tuple[str, str]:
    if value == "-":
        return "stdin", sys.stdin.read()
    path = Path(value)
    if not path.exists() or not path.is_file():
        raise ValueError(f"missing or invalid file: {path}")
    if path.is_symlink():
        raise ValueError(f"symlink input is not allowed: {path}")
    try:
        return str(path), path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"input is not strict UTF-8 text and requires local manual review: {path}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Block high-confidence secrets, authentication material, and payment credentials before Web consultation."
    )
    parser.add_argument("inputs", nargs="+", help="UTF-8 text files to scan; use '-' for stdin")
    args = parser.parse_args()

    results = []
    blocked = False
    try:
        for value in args.inputs:
            label, text = _read_input(value)
            findings = scan(text)
            blocked = blocked or bool(findings)
            results.append({
                "input": label,
                "ok": not findings,
                "findings": findings,
            })
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    print(json.dumps({"ok": not blocked, "results": results}, ensure_ascii=False, indent=2))
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
