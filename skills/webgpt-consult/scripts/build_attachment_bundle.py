#!/usr/bin/env python3
"""Build a strict text attachment bundle for WebGPT Consult."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

from check_packet_safety import scan

DEFAULT_EXTENSIONS = {
    ".c", ".cc", ".cfg", ".conf", ".css", ".csv", ".go", ".h", ".html", ".ini",
    ".java", ".js", ".json", ".jsx", ".md", ".mjs", ".py", ".rb", ".rs", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml",
}
SKIP_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "env", "__pycache__", "node_modules", "dist", "build", ".next", ".cache"}
SKIP_FILES = {".DS_Store"}


def iter_files(paths: Iterable[Path], *, exclude_output: Path | None = None) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            if not path.is_symlink():
                files.append(path)
            continue
        for item in path.rglob("*"):
            if not item.is_file() or item.is_symlink() or item.name in SKIP_FILES:
                continue
            if any(part in SKIP_DIRS for part in item.relative_to(path).parts):
                continue
            try:
                item.resolve().relative_to(path.resolve())
            except ValueError:
                continue
            if exclude_output and item.resolve() == exclude_output.resolve():
                continue
            files.append(item)
    return sorted(set(files), key=lambda p: str(p))


def read_utf8_text(path: Path, allowed_extensions: set[str]) -> tuple[bytes, str] | None:
    if path.suffix.lower() not in allowed_extensions:
        return None
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw[:4096]:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return raw, text


def relative_label(path: Path, roots: list[Path]) -> str:
    for root in roots:
        if root.is_file() and path == root:
            return root.name
        try:
            return str(path.relative_to(root))
        except ValueError:
            continue
    return path.name


def fence_for(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    return {"md": "markdown", "py": "python", "js": "javascript", "mjs": "javascript", "ts": "typescript", "tsx": "tsx", "json": "json", "yaml": "yaml", "yml": "yaml", "sh": "bash", "html": "html", "css": "css"}.get(ext, ext or "text")


def safe_fence(text: str) -> str:
    runs = [len(match.group(0)) for match in re.finditer(r"`+", text)]
    return "`" * max(4, (max(runs) + 1) if runs else 4)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--max-file-bytes", type=int, default=250_000)
    parser.add_argument("--max-total-bytes", type=int, default=2_000_000)
    parser.add_argument("--include-extension", action="append", default=[])
    parser.add_argument("--allow-truncation", action="store_true")
    parser.add_argument("--allow-partial", action="store_true", help="Allow supported text files to be omitted by total-size limit")
    args = parser.parse_args()

    missing = [str(p) for p in args.paths if not p.exists()]
    if missing:
        print(json.dumps({"ok": False, "error": "missing_inputs", "paths": missing}, ensure_ascii=False))
        return 1

    roots = [p.resolve() for p in args.paths]
    allowed_extensions = set(DEFAULT_EXTENSIONS)
    allowed_extensions.update(ext if ext.startswith(".") else f".{ext}" for ext in args.include_extension)
    candidates = iter_files(args.paths, exclude_output=args.output.resolve())

    explicit_unsupported = []
    for original, resolved in zip(args.paths, roots):
        if original.is_file() and read_utf8_text(resolved, allowed_extensions) is None:
            explicit_unsupported.append(str(original))
    if explicit_unsupported:
        print(json.dumps({"ok": False, "error": "explicit_file_not_strict_utf8_text", "paths": explicit_unsupported}, ensure_ascii=False))
        return 1

    selected: list[tuple[Path, str, str, int, int, str, bool]] = []
    skipped: list[str] = []
    total = 0
    hard_failure = False
    seen_labels: dict[str, Path] = {}

    for path in candidates:
        resolved = path.resolve()
        label = relative_label(resolved, roots)
        prior = seen_labels.get(label)
        if prior is not None and prior != resolved:
            print(json.dumps({
                "ok": False,
                "error": "ambiguous_labels",
                "label": label,
                "paths": [str(prior), str(resolved)],
                "hint": "Pass a common parent directory or otherwise preserve unique relative paths.",
            }, ensure_ascii=False))
            return 1
        seen_labels[label] = resolved

        loaded = read_utf8_text(resolved, allowed_extensions)
        if loaded is None:
            skipped.append(f"{label} (unsupported, binary, unreadable, or non-UTF-8)")
            continue
        raw, full_text = loaded
        original_size = len(raw)
        truncated = original_size > args.max_file_bytes
        if truncated and not args.allow_truncation:
            skipped.append(f"{label} (would truncate at max-file-bytes)")
            hard_failure = True
            continue
        included = raw[: args.max_file_bytes]
        if truncated:
            try:
                text = included.decode("utf-8")
            except UnicodeDecodeError:
                skipped.append(f"{label} (byte truncation would split a UTF-8 sequence)")
                hard_failure = True
                continue
        else:
            text = full_text
        if total + len(included) > args.max_total_bytes:
            skipped.append(f"{label} (total bundle limit reached)")
            hard_failure = hard_failure or not args.allow_partial
            continue
        total += len(included)
        selected.append((resolved, label, text, original_size, len(included), sha256(raw), truncated))

    if not selected:
        print(json.dumps({"ok": False, "error": "no_text_files_selected", "skipped": skipped}, ensure_ascii=False))
        return 1
    if hard_failure:
        print(json.dumps({"ok": False, "error": "incomplete_bundle", "skipped": skipped}, ensure_ascii=False))
        return 1

    lines = ["# WebGPT Consult Attachment Bundle", "", "Each manifest entry identifies the transmitted text by a unique relative label and records the original file size and SHA-256.", "", "## Manifest"]
    for _path, label, _text, original_size, included_size, digest, truncated in selected:
        status = "truncated" if truncated else "complete"
        lines.append(f"- `{label}` | sha256 `{digest}` | original {original_size} bytes | included {included_size} bytes | {status}")
    if skipped:
        lines.extend(["", "## Skipped"])
        lines.extend(f"- {item}" for item in skipped)
    lines.extend(["", "## Files"])

    for path, label, text, *_rest in selected:
        fence = safe_fence(text)
        lines.extend(["", f"### `{label}`", "", f"{fence}{fence_for(path)}", text.rstrip(), fence])

    content = "\n".join(lines) + "\n"
    safety = scan(content)
    if not safety["ok"]:
        print(json.dumps({"ok": False, "error": "credential_like_material_detected", "findings": safety["findings"]}, ensure_ascii=False))
        return 1

    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"write_failed: {exc}"}, ensure_ascii=False))
        return 1

    print(args.output)
    print(f"files={len(selected)} skipped={len(skipped)} bytes={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
