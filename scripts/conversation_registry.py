#!/usr/bin/env python3
"""Project-scoped registry for WebGPT Consult ChatGPT conversation continuity."""

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

DEFAULT_STATE = Path.home() / ".codex" / "webgpt-consult" / "conversations.json"
MAX_THREADS_PER_PROJECT = 20


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _git_origin(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            text=True,
            capture_output=True,
            timeout=5,
        )
    except Exception:
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def normalize_remote(remote: str) -> str:
    remote = remote.strip()
    ssh = re.match(r"git@([^:]+):(.+)$", remote)
    if ssh:
        host, path = ssh.groups()
        value = f"{host}/{path}"
    else:
        parsed = urlparse(remote)
        if parsed.scheme and parsed.netloc:
            value = f"{parsed.netloc}{parsed.path}"
        else:
            value = remote
    return value.removesuffix(".git").strip("/").lower()


def project_identity(project_root: Path) -> dict:
    root = project_root.expanduser().resolve()
    remote = _git_origin(root)
    source = f"git:{normalize_remote(remote)}" if remote else f"path:{root}"
    fingerprint = hashlib.sha256(source.encode("utf-8")).hexdigest()[:20]
    label = normalize_remote(remote).split("/")[-1] if remote else root.name
    return {"fingerprint": fingerprint, "label": label, "source_kind": "git" if remote else "path"}


def state_path() -> Path:
    override = os.environ.get("WEBGPT_CONSULT_STATE")
    return Path(override).expanduser() if override else DEFAULT_STATE


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "projects": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("projects"), dict):
        raise ValueError("invalid registry format")
    return data


def save_state(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.parent.chmod(0o700)
    except OSError:
        pass
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        tmp.chmod(0o600)
    except OSError:
        pass
    tmp.replace(path)


def _project_bucket(data: dict, identity: dict) -> dict:
    return data["projects"].setdefault(identity["fingerprint"], {
        "label": identity["label"],
        "source_kind": identity["source_kind"],
        "threads": [],
    })


def list_threads(data: dict, identity: dict) -> list[dict]:
    bucket = data["projects"].get(identity["fingerprint"], {})
    threads = [t for t in bucket.get("threads", []) if t.get("status", "active") == "active"]
    return sorted(threads, key=lambda t: t.get("last_used_at", ""), reverse=True)


def record_thread(data: dict, identity: dict, *, thread_key: str, conversation_url: str, scope: str, task_id: str, summary: str) -> dict:
    if not conversation_url.startswith("https://chatgpt.com/"):
        raise ValueError("conversation_url must be a chatgpt.com URL")
    bucket = _project_bucket(data, identity)
    now = utc_now()
    existing = next((t for t in bucket["threads"] if t.get("thread_key") == thread_key), None)
    payload = {
        "thread_key": thread_key,
        "conversation_url": conversation_url,
        "scope": scope.strip(),
        "last_task_id": task_id,
        "summary": summary.strip(),
        "last_used_at": now,
        "status": "active",
    }
    if existing:
        existing.update(payload)
        result = existing
    else:
        payload["created_at"] = now
        bucket["threads"].append(payload)
        result = payload
    bucket["threads"] = sorted(bucket["threads"], key=lambda t: t.get("last_used_at", ""), reverse=True)[:MAX_THREADS_PER_PROJECT]
    return result


def retire_thread(data: dict, identity: dict, thread_key: str) -> bool:
    bucket = data["projects"].get(identity["fingerprint"], {})
    for thread in bucket.get("threads", []):
        if thread.get("thread_key") == thread_key:
            thread["status"] = "retired"
            thread["last_used_at"] = utc_now()
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("identity")
    sub.add_parser("list")
    record = sub.add_parser("record")
    record.add_argument("--thread-key", required=True)
    record.add_argument("--conversation-url", required=True)
    record.add_argument("--scope", required=True)
    record.add_argument("--task-id", required=True)
    record.add_argument("--summary", default="")
    retire = sub.add_parser("retire")
    retire.add_argument("--thread-key", required=True)
    args = parser.parse_args()

    try:
        identity = project_identity(Path(args.project_root))
        if args.command == "identity":
            out = identity
        else:
            path = state_path()
            data = load_state(path)
            if args.command == "list":
                out = {"project": identity, "threads": list_threads(data, identity)}
            elif args.command == "record":
                out = record_thread(
                    data, identity,
                    thread_key=args.thread_key,
                    conversation_url=args.conversation_url,
                    scope=args.scope,
                    task_id=args.task_id,
                    summary=args.summary,
                )
                save_state(path, data)
            else:
                changed = retire_thread(data, identity, args.thread_key)
                if changed:
                    save_state(path, data)
                out = {"retired": changed, "thread_key": args.thread_key}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
