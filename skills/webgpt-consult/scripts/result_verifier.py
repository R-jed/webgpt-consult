#!/usr/bin/env python3
"""Verify that an extracted assistant turn belongs to the requested consultation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def normalize_line(line: str) -> str:
    return line.replace("\\_", "_").strip()


def verify(reply: str, sentinel: str, task_id: str) -> dict:
    lines = [line for line in reply.splitlines() if line.strip()]
    expected_task = f"Task-ID: {task_id}"
    first_ok = bool(lines) and normalize_line(lines[0]) == sentinel
    task_ok = len(lines) >= 2 and normalize_line(lines[1]) == expected_task
    return {
        "ok": first_ok and task_ok,
        "sentinel_ok": first_ok,
        "task_id_ok": task_ok,
        "expected_sentinel": sentinel,
        "expected_task_line": expected_task,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reply", help="Extracted assistant reply path, or '-' for stdin")
    parser.add_argument("--sentinel", required=True)
    parser.add_argument("--task-id", required=True)
    args = parser.parse_args()
    try:
        text = sys.stdin.read() if args.reply == "-" else Path(args.reply).read_text(encoding="utf-8")
        result = verify(text, args.sentinel, args.task_id)
    except Exception as exc:
        result = {"ok": False, "error": str(exc)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
