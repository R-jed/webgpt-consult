#!/usr/bin/env python3
"""Build a fail-closed submission manifest before any WebGPT Consult send."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
from pathlib import Path

from check_packet_safety import scan

TEXT_EXTENSIONS = {
    ".c", ".cc", ".cfg", ".conf", ".css", ".csv", ".go", ".h", ".html", ".ini",
    ".java", ".js", ".json", ".jsx", ".md", ".mjs", ".py", ".rb", ".rs", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml",
}
TASK_ID_RE = re.compile(r"^webgpt-consult-(\d{8})-(\d{6})-([A-Za-z0-9_-]{8,})$")
SENTINEL_RE = re.compile(r"^WEBGPT_CONSULT_RESULT_(\d{8})_(\d{6})_([A-Za-z0-9_-]{8,})$")


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

    text_candidate = path.suffix.lower() in TEXT_EXTENSIONS and b"\x00" not in raw[:4096]
    if text_candidate:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            item["scan_status"] = "unscanned_binary_confirmed" if allow_unscanned_binary else "manual_review_required"
            item["manual_review_reason"] = "non_utf8_text"
            return item

        result = scan(text)
        item["scan_status"] = "passed" if result["ok"] else "blocked"
        item["high_count"] = result["high_count"]
        item["warn_count"] = result["warn_count"]
        if not result["ok"]:
            item["findings"] = result["findings"]
    else:
        item["scan_status"] = "unscanned_binary_confirmed" if allow_unscanned_binary else "manual_review_required"
        item["manual_review_reason"] = "non_text_or_binary"
    return item


def _invocation_identity_status(*, task_id: str, sentinel: str) -> dict:
    task_match = TASK_ID_RE.fullmatch(task_id)
    sentinel_match = SENTINEL_RE.fullmatch(sentinel)
    task_format_ok = task_match is not None
    sentinel_format_ok = sentinel_match is not None
    pair_ok = False
    if task_match and sentinel_match:
        pair_ok = task_match.groups() == sentinel_match.groups()
    return {
        "ok": task_format_ok and sentinel_format_ok and pair_ok,
        "task_id_format_ok": task_format_ok,
        "sentinel_format_ok": sentinel_format_ok,
        "timestamp_and_nonce_match": pair_ok,
    }


def _packet_binding_status(packet_text: str, *, task_id: str, sentinel: str) -> dict:
    lines = [line.strip() for line in packet_text.splitlines()]
    expected_task = f"Task-ID: {task_id}"
    expected_sentinel = f"Sentinel: {sentinel}"
    task_count = sum(line == expected_task for line in lines)
    sentinel_count = sum(line == expected_sentinel for line in lines)
    return {
        "ok": task_count == 1 and sentinel_count == 1,
        "task_id_exactly_once": task_count == 1,
        "sentinel_exactly_once": sentinel_count == 1,
        "task_id_count": task_count,
        "sentinel_count": sentinel_count,
    }


def build_manifest(packet: Path, attachments: list[Path], *, task_id: str, sentinel: str, allow_unscanned_binary: bool) -> dict:
    if not packet.exists() or not packet.is_file():
        raise ValueError(f"packet missing or not a file: {packet}")
    if packet.is_symlink():
        raise ValueError(f"symlink packet is not allowed: {packet}")
    packet_raw = packet.read_bytes()
    packet_text = packet_raw.decode("utf-8")
    packet_scan = scan(packet_text)
    identity = _invocation_identity_status(task_id=task_id, sentinel=sentinel)
    binding = _packet_binding_status(packet_text, task_id=task_id, sentinel=sentinel)
    items = [inspect_file(path, allow_unscanned_binary=allow_unscanned_binary) for path in attachments]
    blocked = [item for item in items if item["scan_status"] == "blocked"]
    manual = [item for item in items if item["scan_status"] == "manual_review_required"]
    ok = packet_scan["ok"] and identity["ok"] and binding["ok"] and not blocked and not manual
    packet_info = {
        "name": packet.name,
        "bytes": len(packet_raw),
        "sha256": sha256_bytes(packet_raw),
        "scan_status": "passed" if packet_scan["ok"] else "blocked",
        "high_count": packet_scan["high_count"],
        "warn_count": packet_scan["warn_count"],
    }
    if not packet_scan["ok"]:
        packet_info["findings"] = packet_scan["findings"]
    return {
        "ok": ok,
        "task_id": task_id,
        "sentinel": sentinel,
        "context_hash": sha256_bytes(packet_raw),
        "identity": identity,
        "binding": binding,
        "packet": packet_info,
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
        help="Allow non-scannable attachments after local manual review. Never overrides detected credentials.",
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
