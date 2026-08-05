#!/usr/bin/env python3
"""Build a reviewable UTF-8 Markdown bundle from selected local text files.

Use this only when many relevant text files are awkward to upload individually or
when ChatGPT Web rejects an archive. Original human-readable files remain the
preferred evidence when they can be uploaded reliably.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


DEFAULT_EXTENSIONS = {
    ".c", ".cc", ".cfg", ".conf", ".css", ".csv", ".go", ".h", ".html",
    ".ini", ".java", ".js", ".json", ".jsx", ".lock", ".md", ".mjs", ".py",
    ".rb", ".rs", ".sh", ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml",
    ".yaml", ".yml",
}

SKIP_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "env", "__pycache__",
    "node_modules", "dist", "build", ".next", ".cache", "coverage",
}
SKIP_FILES = {".DS_Store"}


class BundleError(RuntimeError):
    pass


@dataclass(frozen=True)
class SourceFile:
    path: Path
    label: str
    text: str
    source_bytes: int
    included_bytes: int
    sha256: str
    status: str


def _load_safety_scan() -> Callable[[str], list[dict]]:
    path = Path(__file__).with_name("safety_guard.py")
    spec = importlib.util.spec_from_file_location("webgpt_consult_safety_guard", path)
    if spec is None or spec.loader is None:
        raise BundleError("could not load safety_guard.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.scan


def _fence(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    return {
        "md": "markdown", "py": "python", "js": "javascript", "mjs": "javascript",
        "ts": "typescript", "tsx": "tsx", "json": "json", "yaml": "yaml",
        "yml": "yaml", "sh": "bash", "html": "html", "css": "css",
    }.get(ext, ext or "text")


def _truncate_utf8(text: str, max_bytes: int) -> str:
    if len(text.encode("utf-8")) <= max_bytes:
        return text
    low, high = 0, len(text)
    while low < high:
        mid = (low + high + 1) // 2
        if len(text[:mid].encode("utf-8")) <= max_bytes:
            low = mid
        else:
            high = mid - 1
    return text[:low]


def _iter_candidates(inputs: list[Path], output: Path) -> Iterable[tuple[Path, str, bool]]:
    output_resolved = output.resolve()
    for root in inputs:
        if not root.exists():
            raise BundleError(f"missing input: {root}")
        if root.is_symlink():
            raise BundleError(f"symlink input is not allowed: {root}")
        resolved_root = root.resolve()
        if resolved_root.is_file():
            if resolved_root != output_resolved:
                yield resolved_root, resolved_root.name, True
            continue
        if not resolved_root.is_dir():
            raise BundleError(f"unsupported input: {root}")
        for item in sorted(resolved_root.rglob("*"), key=lambda p: str(p)):
            if item.is_symlink() or not item.is_file() or item.resolve() == output_resolved:
                continue
            rel = item.relative_to(resolved_root)
            if item.name in SKIP_FILES or any(part in SKIP_DIRS for part in rel.parts):
                continue
            yield item.resolve(), f"{resolved_root.name}/{rel.as_posix()}", False


def _collect(
    inputs: list[Path],
    output: Path,
    allowed_extensions: set[str],
    max_file_bytes: int,
    max_total_bytes: int,
    allow_partial: bool,
) -> tuple[list[SourceFile], list[str]]:
    sources: list[SourceFile] = []
    skipped: list[str] = []
    labels: set[str] = set()
    total = 0

    for path, label, explicit in _iter_candidates(inputs, output):
        if label in labels:
            raise BundleError(f"duplicate bundle label: {label}")
        labels.add(label)

        if path.suffix.lower() not in allowed_extensions:
            if explicit:
                raise BundleError(f"explicit input has unsupported text extension: {path}")
            skipped.append(f"{label} (unsupported extension)")
            continue

        raw = path.read_bytes()
        if b"\x00" in raw:
            if explicit:
                raise BundleError(f"explicit input appears binary: {path}")
            skipped.append(f"{label} (binary)")
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BundleError(f"strict UTF-8 decode failed for {label}: {exc}") from exc

        digest = hashlib.sha256(raw).hexdigest()
        source_bytes = len(raw)
        status = "full"
        included = text

        if source_bytes > max_file_bytes:
            if not allow_partial:
                raise BundleError(
                    f"{label} exceeds --max-file-bytes ({source_bytes} > {max_file_bytes}); "
                    "select a smaller excerpt or rerun with --allow-partial"
                )
            included = _truncate_utf8(text, max_file_bytes)
            status = "truncated"

        included_bytes = len(included.encode("utf-8"))
        if total + included_bytes > max_total_bytes:
            if not allow_partial:
                raise BundleError(
                    f"bundle exceeds --max-total-bytes before {label}; select fewer files or rerun with --allow-partial"
                )
            skipped.append(f"{label} (omitted: total bundle limit)")
            continue

        total += included_bytes
        sources.append(
            SourceFile(
                path=path,
                label=label,
                text=included,
                source_bytes=source_bytes,
                included_bytes=included_bytes,
                sha256=digest,
                status=status,
            )
        )

    if not sources:
        raise BundleError("no UTF-8 text files were selected for the bundle")
    return sources, skipped


def _render(sources: list[SourceFile], skipped: list[str], partial_allowed: bool) -> str:
    lines = [
        "# webgpt-consult Attachment Bundle",
        "",
        "This bundle contains selected local text files for ChatGPT Web review.",
        "Manifest labels are provenance labels; they do not give ChatGPT access to the local filesystem.",
        "",
        f"Partial bundle explicitly allowed: {'yes' if partial_allowed else 'no'}",
        "",
        "## Manifest",
    ]
    for source in sources:
        lines.append(
            f"- `{source.label}` | status={source.status} | source_bytes={source.source_bytes} | "
            f"included_bytes={source.included_bytes} | sha256={source.sha256}"
        )
    if skipped:
        lines.extend(["", "## Excluded"])
        lines.extend(f"- {item}" for item in skipped)

    lines.extend(["", "## Files"])
    for source in sources:
        lines.extend([
            "",
            f"### `{source.label}`",
            "",
            f"````{_fence(source.path)}",
            source.text.rstrip(),
            "````",
        ])
        if source.status == "truncated":
            lines.extend([
                "",
                "[PARTIAL FILE: content was truncated only because --allow-partial was explicitly supplied.]",
            ])
    return "\n".join(lines) + "\n"


def build_bundle(
    inputs: list[Path],
    output: Path,
    *,
    allowed_extensions: set[str] | None = None,
    max_file_bytes: int = 500_000,
    max_total_bytes: int = 4_000_000,
    allow_partial: bool = False,
) -> dict:
    if output.exists() and output.is_symlink():
        raise BundleError(f"output symlink is not allowed: {output}")
    if max_file_bytes <= 0 or max_total_bytes <= 0:
        raise BundleError("byte limits must be positive")

    extensions = set(DEFAULT_EXTENSIONS if allowed_extensions is None else allowed_extensions)
    sources, skipped = _collect(
        inputs,
        output,
        extensions,
        max_file_bytes,
        max_total_bytes,
        allow_partial,
    )
    bundle = _render(sources, skipped, allow_partial)

    findings = _load_safety_scan()(bundle)
    blocks = [item for item in findings if item.get("severity") == "block"]
    warnings = [item for item in findings if item.get("severity") == "warn"]
    if blocks:
        kinds = sorted({str(item.get("type")) for item in blocks})
        raise BundleError(f"bundle safety scan blocked output: {', '.join(kinds)}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(bundle, encoding="utf-8")
    return {
        "ok": True,
        "output": str(output),
        "files": len(sources),
        "partial_files": sum(source.status != "full" for source in sources),
        "excluded": len(skipped),
        "warning_count": len(warnings),
        "bundle_bytes": len(bundle.encode("utf-8")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Selected files or directories")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output Markdown bundle")
    parser.add_argument("--max-file-bytes", type=int, default=500_000)
    parser.add_argument("--max-total-bytes", type=int, default=4_000_000)
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Explicitly allow oversized files to be truncated and files beyond the total limit to be omitted",
    )
    parser.add_argument(
        "--include-extension",
        action="append",
        default=[],
        help="Additional text extension to include, for example .proto",
    )
    args = parser.parse_args()

    extensions = set(DEFAULT_EXTENSIONS)
    extensions.update(ext if ext.startswith(".") else f".{ext}" for ext in args.include_extension)
    try:
        result = build_bundle(
            args.paths,
            args.output,
            allowed_extensions=extensions,
            max_file_bytes=args.max_file_bytes,
            max_total_bytes=args.max_total_bytes,
            allow_partial=args.allow_partial,
        )
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
