#!/usr/bin/env python3
"""Durable, project-scoped consultation state for WebGPT Consult."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_ROOT = Path.home() / ".codex" / "webgpt-consult" / "state"
CONSULT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
LIST_FIELDS = (
    "standing_constraints",
    "accepted_decisions",
    "rejected_or_deferred",
    "open_questions",
    "evidence_refs",
)
REQUIRED_TEXT_FIELDS = ("consult_id", "title", "user_intent", "current_state", "last_task_id")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _run_git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            capture_output=True,
            timeout=5,
        )
    except Exception:
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def _git_root(root: Path) -> Path | None:
    value = _run_git(root, "rev-parse", "--show-toplevel")
    return Path(value).resolve() if value else None


def _git_origin(root: Path) -> str | None:
    return _run_git(root, "remote", "get-url", "origin")


def normalize_remote(remote: str) -> str:
    remote = remote.strip()
    ssh = re.match(r"git@([^:]+):(.+)$", remote)
    if ssh:
        host, path = ssh.groups()
        value = f"{host}/{path}"
    else:
        parsed = urlparse(remote)
        if parsed.scheme and parsed.hostname:
            value = f"{parsed.hostname}{parsed.path}"
        else:
            value = remote
    return value.removesuffix(".git").strip("/").lower()


def project_identity(project_root: Path) -> dict:
    supplied = project_root.expanduser().resolve()
    git_root = _git_root(supplied)
    canonical = git_root or supplied
    remote = _git_origin(canonical) if git_root else None

    # Include the checkout path even when a remote exists. Two clones/worktrees of
    # the same repository may intentionally contain different code and must not
    # silently share consultation state.
    remote_part = normalize_remote(remote) if remote else "no-remote"
    source = f"{remote_part}|{canonical}"
    fingerprint = hashlib.sha256(source.encode("utf-8")).hexdigest()[:20]
    label = normalize_remote(remote).split("/")[-1] if remote else canonical.name
    return {
        "fingerprint": fingerprint,
        "label": label,
        "root": str(canonical),
        "source_kind": "git-checkout" if git_root else "path",
    }


def state_root() -> Path:
    override = os.environ.get("WEBGPT_CONSULT_STATE_DIR")
    return Path(override).expanduser() if override else DEFAULT_ROOT


def project_dir(identity: dict) -> Path:
    return state_root() / identity["fingerprint"]


def consult_path(identity: dict, consult_id: str) -> Path:
    if not CONSULT_ID_RE.fullmatch(consult_id):
        raise ValueError("consult_id must match [A-Za-z0-9][A-Za-z0-9._-]{0,79}")
    return project_dir(identity) / f"{consult_id}.json"


def _valid_chat_url(value: str | None) -> bool:
    if value in (None, ""):
        return True
    parsed = urlparse(str(value))
    return parsed.scheme == "https" and parsed.hostname == "chatgpt.com" and parsed.path not in {"", "/"}


def validate_snapshot(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("consult state must be a JSON object")

    for field in REQUIRED_TEXT_FIELDS:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")

    if not CONSULT_ID_RE.fullmatch(data["consult_id"]):
        raise ValueError("invalid consult_id")

    for field in LIST_FIELDS:
        value = data.get(field)
        if value is None:
            data[field] = []
            continue
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"{field} must be a list of strings")

    anchor = data.get("anchor")
    if anchor is not None and not isinstance(anchor, str):
        raise ValueError("anchor must be a string or null")

    chat_url = data.get("conversation_url")
    if not _valid_chat_url(chat_url):
        raise ValueError("conversation_url must be a canonical chatgpt.com conversation URL or null")

    return data


def load_consult(identity: dict, consult_id: str) -> dict:
    path = consult_path(identity, consult_id)
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_snapshot(data)
    if data.get("project_fingerprint") != identity["fingerprint"]:
        raise ValueError("consult state belongs to a different project checkout")
    return data


def list_consults(identity: dict) -> dict:
    directory = project_dir(identity)
    if not directory.exists():
        return {"project": identity, "consults": [], "warnings": []}

    consults: list[dict] = []
    warnings: list[str] = []
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            validate_snapshot(data)
            if data.get("project_fingerprint") != identity["fingerprint"]:
                raise ValueError("project fingerprint mismatch")
            consults.append({
                "consult_id": data["consult_id"],
                "title": data["title"],
                "anchor": data.get("anchor"),
                "conversation_url": data.get("conversation_url"),
                "last_task_id": data["last_task_id"],
                "updated_at": data.get("updated_at"),
            })
        except Exception as exc:
            warnings.append(f"{path.name}: {exc}")

    consults.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
    return {"project": identity, "consults": consults, "warnings": warnings}


def save_consult(identity: dict, input_data: dict) -> dict:
    data = validate_snapshot(dict(input_data))
    path = consult_path(identity, data["consult_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.parent.chmod(0o700)
    except OSError:
        pass

    created_at = None
    if path.exists():
        try:
            previous = json.loads(path.read_text(encoding="utf-8"))
            created_at = previous.get("created_at")
        except Exception:
            created_at = None

    now = utc_now()
    data.update({
        "version": 1,
        "project_fingerprint": identity["fingerprint"],
        "project_label": identity["label"],
        "project_root": identity["root"],
        "created_at": created_at or now,
        "updated_at": now,
    })

    tmp = path.parent / f".{path.name}.{os.getpid()}.tmp"
    try:
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        try:
            tmp.chmod(0o600)
        except OSError:
            pass
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)
    return data


def remove_consult(identity: dict, consult_id: str) -> bool:
    path = consult_path(identity, consult_id)
    if not path.exists():
        return False
    path.unlink()
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("identity")
    sub.add_parser("list")

    show = sub.add_parser("show")
    show.add_argument("--consult-id", required=True)

    save = sub.add_parser("save")
    save.add_argument("snapshot", type=Path, help="JSON file containing the durable consultation snapshot")

    remove = sub.add_parser("remove")
    remove.add_argument("--consult-id", required=True)

    args = parser.parse_args()
    identity = project_identity(Path(args.project_root))

    try:
        if args.command == "identity":
            out = identity
        elif args.command == "list":
            out = list_consults(identity)
        elif args.command == "show":
            out = load_consult(identity, args.consult_id)
        elif args.command == "save":
            raw = json.loads(args.snapshot.read_text(encoding="utf-8"))
            out = save_consult(identity, raw)
        else:
            out = {"removed": remove_consult(identity, args.consult_id), "consult_id": args.consult_id}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
