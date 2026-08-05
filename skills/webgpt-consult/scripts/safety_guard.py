#!/usr/bin/env python3
"""Small local guard for secrets, auth/payment data, and obvious privacy warnings."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


BLOCK_PATTERNS = [
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
]

WARN_PATTERNS = [
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone_number", re.compile(r"(?<!\w)\+?\d(?:[\s().-]?\d){7,14}(?!\w)")),
    ("cn_national_id", re.compile(r"\b\d{17}[\dXx]\b")),
    ("absolute_user_path", re.compile(r"(?:/Users/|/home/)[^\s`'\"<>]+")),
    (
        "private_network_url",
        re.compile(
            r"https?://(?:localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|"
            r"172\.(?:1[6-9]|2\d|3[0-1])\.\d+\.\d+)[^\s`'\"<>]*"
        ),
    ),
]

ASSIGNMENT_RE = re.compile(
    r"""(?ix)
    \b(?P<key>
        token|api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|
        session[_-]?token|auth[_-]?token|bearer[_-]?token|aws[_-]?secret[_-]?access[_-]?key|
        password|passwd|pwd|secret|otp|one[_-]?time[_-]?password|recovery[_-]?code|
        cvv|cvc|card[_-]?pin|payment[_-]?pin
    )\s*[:=]\s*
    (?P<value>
        "(?:\\.|[^"\n])*" |
        '(?:\\.|[^'\n])*' |
        [^\s,;#]+
    )
    """
)

CARD_CANDIDATE_RE = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")

BENIGN_ASSIGNMENT_VALUES = {
    "",
    "none",
    "null",
    "nil",
    "true",
    "false",
    "0",
    "-",
    "redacted",
    "<redacted>",
    "<secret>",
    "<token>",
    "<password>",
    "changeme",
    "change-me",
    "example",
    "placeholder",
    "xxxx",
    "xxxxx",
    "xxxxxxxx",
    "***",
    "********",
}


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


def _strip_quotes(value: str) -> tuple[str, bool]:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1], True
    return value, False


def _looks_like_code_reference(value: str) -> bool:
    value = value.strip()
    patterns = (
        r"\$\{?[A-Za-z_][A-Za-z0-9_]*\}?",
        r"[A-Z][A-Z0-9_]{2,}",
        r"[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_.]*",
        r"[A-Za-z_][A-Za-z0-9_]*(?:\[[^\]]+\])+",
        r"[A-Za-z_][A-Za-z0-9_.]*\([^)]*\)",
        r"[A-Za-z_][A-Za-z0-9_]*(?:_value|_var|_ref)",
    )
    return any(re.fullmatch(pattern, value, re.IGNORECASE) for pattern in patterns)


def _assignment_contains_secret(value: str) -> bool:
    value, quoted = _strip_quotes(value)
    normalized = value.strip().lower()
    if normalized in BENIGN_ASSIGNMENT_VALUES:
        return False
    if "<redacted" in normalized or "${" in normalized or "{{" in normalized:
        return False
    if quoted:
        if re.fullmatch(r"\$[A-Za-z_][A-Za-z0-9_]*", value):
            return False
        return len(value) >= 3
    if _looks_like_code_reference(value):
        return False
    return len(value) >= 3


def _excerpt(text: str, start: int, end: int, *, redact: bool) -> str:
    matched = text[start:end]
    if redact:
        if ":" in matched or "=" in matched:
            key = re.split(r"[:=]", matched, maxsplit=1)[0].strip()
            return f"{key}=<REDACTED>" if key else "<REDACTED>"
        return "<REDACTED>"

    left = max(0, start - 12)
    right = min(len(text), end + 12)
    snippet = text[left:right].replace("\n", "\\n")
    return snippet if len(snippet) <= 96 else snippet[:93] + "..."


def scan(text: str) -> list[dict]:
    findings: list[dict] = []

    for kind, pattern in BLOCK_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                {
                    "severity": "block",
                    "type": kind,
                    "start": match.start(),
                    "end": match.end(),
                    "excerpt": _excerpt(text, match.start(), match.end(), redact=True),
                }
            )

    for match in ASSIGNMENT_RE.finditer(text):
        if _assignment_contains_secret(match.group("value")):
            findings.append(
                {
                    "severity": "block",
                    "type": "credential_assignment",
                    "start": match.start(),
                    "end": match.end(),
                    "excerpt": f"{match.group('key')}=<REDACTED>",
                }
            )

    for match in CARD_CANDIDATE_RE.finditer(text):
        digits = re.sub(r"\D", "", match.group(0))
        if _luhn_valid(digits):
            findings.append(
                {
                    "severity": "block",
                    "type": "payment_card_number",
                    "start": match.start(),
                    "end": match.end(),
                    "excerpt": f"<CARD_REDACTED_LAST4_{digits[-4:]}>",
                }
            )

    for kind, pattern in WARN_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                {
                    "severity": "warn",
                    "type": kind,
                    "start": match.start(),
                    "end": match.end(),
                    "excerpt": _excerpt(text, match.start(), match.end(), redact=False),
                }
            )

    unique: dict[tuple, dict] = {}
    for item in findings:
        key = (item["severity"], item["type"], item["start"], item["end"])
        unique[key] = item
    return sorted(unique.values(), key=lambda item: (item["start"], item["end"], item["severity"], item["type"]))


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
        description="Block high-confidence secrets/auth/payment data and warn about obvious private identifiers."
    )
    parser.add_argument("inputs", nargs="+", help="UTF-8 text files to scan; use '-' for stdin")
    args = parser.parse_args()

    results = []
    blocked = False
    try:
        for value in args.inputs:
            label, text = _read_input(value)
            findings = scan(text)
            block_count = sum(item["severity"] == "block" for item in findings)
            warn_count = sum(item["severity"] == "warn" for item in findings)
            blocked = blocked or block_count > 0
            results.append(
                {
                    "input": label,
                    "ok": block_count == 0,
                    "block_count": block_count,
                    "warn_count": warn_count,
                    "findings": findings,
                }
            )
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    print(json.dumps({"ok": not blocked, "results": results}, ensure_ascii=False, indent=2))
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
