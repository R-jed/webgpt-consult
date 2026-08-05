#!/usr/bin/env python3
"""Fail-closed credential scanner for WebGPT Consult text inputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


HIGH_PATTERNS = [
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b")),
    ("gitlab_token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b")),
    ("openai_key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("anthropic_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("stripe_live_key", re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("authorization_header", re.compile(r"(?i)\bAuthorization\s*:\s*(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{12,}")),
    ("cookie_header", re.compile(r"(?i)\bCookie\s*:\s*[^\n]{20,}")),
    ("npm_auth_token", re.compile(r"(?i)\b_?authToken\s*=\s*[^\s\"']{8,}")),
    ("credential_assignment", re.compile(
        r"(?i)\b(?:token|api[_-]?key|access[_-]?token|refresh[_-]?token|"
        r"client[_-]?secret|session[_-]?token|auth[_-]?token|bearer[_-]?token|"
        r"aws[_-]?secret[_-]?access[_-]?key|password|passwd|pwd|secret)\s*[:=]\s*"
        r"(?:['\"][^'\"\n]{8,}['\"]|[^\s'\"]{8,})"
    )),
]

WARN_PATTERNS = [
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone_cn", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
    ("id_card_cn", re.compile(r"\b\d{17}[\dXx]\b")),
    ("absolute_user_path", re.compile(r"/Users/[^\s`'\"<>]+")),
    ("private_url", re.compile(r"https?://(?:localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[0-1])\.\d+\.\d+)[^\s`'\"<>]*")),
]


def compact_excerpt(text: str, start: int, end: int) -> str:
    left = max(0, start - 12)
    right = min(len(text), end + 12)
    snippet = text[left:right].replace("\n", "\\n")
    return snippet if len(snippet) <= 80 else snippet[:77] + "..."


def _redact_finding(text: str, finding: dict) -> dict:
    if finding["severity"] != "high":
        return finding
    matched = text[finding["start"]:finding["end"]]
    parts = re.split(r"[:=]", matched, maxsplit=1)
    if len(parts) > 1 and parts[0].strip():
        return {**finding, "excerpt": f"{parts[0].strip()}=<REDACTED>"}
    return {**finding, "excerpt": "<REDACTED>"}


def scan(text: str) -> dict:
    findings = []
    for severity, patterns in (("high", HIGH_PATTERNS), ("warn", WARN_PATTERNS)):
        for name, pattern in patterns:
            for match in pattern.finditer(text):
                finding = {
                    "severity": severity,
                    "type": name,
                    "start": match.start(),
                    "end": match.end(),
                    "excerpt": compact_excerpt(text, match.start(), match.end()),
                }
                findings.append(_redact_finding(text, finding))
    high_count = sum(item["severity"] == "high" for item in findings)
    warn_count = sum(item["severity"] == "warn" for item in findings)
    return {
        "ok": high_count == 0,
        "high_count": high_count,
        "warn_count": warn_count,
        "char_count": len(text),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan WebGPT Consult text for credential-like material.")
    parser.add_argument("packet", help="Path to text input, or '-' for stdin")
    parser.add_argument("--max-chars", type=int, default=15000, help="Warn above this character count")
    parser.add_argument("--fail-on-length", action="store_true", help="Fail when input exceeds --max-chars")
    args = parser.parse_args()

    try:
        text = sys.stdin.read() if args.packet == "-" else Path(args.packet).read_text(encoding="utf-8")
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"read_failed: {exc}"}, ensure_ascii=False, indent=2))
        return 2

    result = scan(text)
    if len(text) > args.max_chars:
        severity = "high" if args.fail_on_length else "warn"
        result["findings"].append({
            "severity": severity,
            "type": "packet_too_long",
            "start": args.max_chars,
            "end": len(text),
            "excerpt": f"{len(text)} chars exceeds max {args.max_chars}",
        })
        result[f"{severity}_count"] += 1
        if severity == "high":
            result["ok"] = False

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
