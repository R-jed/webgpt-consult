#!/usr/bin/env python3
"""Build a fail-closed submission manifest before any WebGPT Consult send."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
from pathlib import Path

from check_packet_safety import scan

TEXT_EXTENSIONS = {
    ".c", ".cc", ".cfg", ".conf", ".css", ".csv", ".go", ".h", ".html", ".ini",
    ".java", ".js", ".json", ".jsx", ".md", ".mjs", ".py", ".rb", ".rs", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml",
}


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def inspect_file(path: Path, *, allow_unscanned_binary: bool = False) -> dict:
    if not path.exists() or not path.is_file():
        raise ValueError(f"attachment missing or not a file: {path}")
    if path.is_symlink():
        raise ValueError(f"symlink attachments are not allowed: {path}")
    raw = path.read_bytes()
    item = {
        "name": path.name,
        "bytes": len(raw),
        "sha256": sha256_bytes(raw),
        "mime": mimetypes.guess_type(path.name)[0],
    }
    if path.suffix.lower() in TEXT_EXTENSIONS and b"\x00" not in raw[:4096]:
        text = raw.decode("utf-8", errors="replace")
        result = scan(text)
        item["scan_status"] = "passed" if result["ok"] else "blocked"
        item["high_count"] = result["high_count"]
        if not result["ok"]:
            item["findings"] = result["findings"]
    else:
        item["scan_status"] = "unscanned_binary_confirmed" if allow_unscanned_binary else "manual_review_required"
    return item


def build_manifest(packet: Path, attachments: list[Path], *, task_id: str, sentinel: str, allow_unscanned_binary: bool) -> dict:
    if not packet.exists() or not packet.is_file():
        raise ValueError(f"packet missing or not a file: {packet}")
    packet_raw = packet.read_bytes()
    packet_text = packet_raw.decode("utf-8")
    packet_scan = scan(packet_text)
    items = [inspect_file(path, allow_unscanned_binary=allow_unscanned_binary) for path in attachments]
    blocked = [item for item in items if item["scan_status"] == "blocked"]
    manual = [item for item in items if item["scan_status"] == "manual_review_required"]
    ok = packet_scan["ok"] and not blocked and not manual
    return {
        "ok": ok,
        "task_id": task_id,
        "sentinel": sentinel,
        "context_hash": sha256_bytes(packet_raw),
        "packet": {
            "name": packet.name,
            "bytes": len(packet_raw),
            "sha256": sha256_bytes(packet_raw),
            "scan_status": "passed" if packet_scan["ok"] else "blocked",
            "high_count": packet_scan["high_count"],
        },
        "attachments": items,
        "manual_review_required": [item["name"] for item in manual],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--attachment", action="append", default=[], type=Path)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--sentinel", required=True)
    parser.add_argument(
        "--confirm-unscanned-binary",
        action="store_true",
        help="Allow intended non-text attachments after local manual review. Never overrides detected credentials.",
    )
    args = parser.parse_args()
    try:
        result = build_manifest(
            args.packet,
            args.attachment,
            task_id=args.task_id,
            sentinel=args.sentinel,
            allow_unscanned_binary=args.confirm_unscanned_binary,
        )
    except Exception as exc:
        result = {"ok": False, "error": str(exc)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
