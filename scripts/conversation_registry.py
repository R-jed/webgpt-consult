#!/usr/bin/env python3
"""Project-scoped registry for WebGPT Consult ChatGPT conversation continuity."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_STATE = Path.home() / ".codex" / "webgpt-consult" / "conversations.json"
MAX_THREADS_PER_PROJECT = 20
LOCK_TIMEOUT_SECONDS = 5.0
STALE_LOCK_SECONDS = 30.0


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
    supplied_root = project_root.expanduser().resolve()
    git_root = _git_root(supplied_root)
    canonical_root = git_root or supplied_root
    remote = _git_origin(canonical_root) if git_root else None
    source = f"git:{normalize_remote(remote)}" if remote else f"path:{canonical_root}"
    fingerprint = hashlib.sha256(source.encode("utf-8")).hexdigest()[:20]
    label = normalize_remote(remote).split("/")[-1] if remote else canonical_root.name
    source_kind = "git-remote" if remote else ("git-root" if git_root else "path")
    return {"fingerprint": fingerprint, "label": label, "source_kind": source_kind}


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


@contextmanager
def registry_lock(path: Path, timeout: float = LOCK_TIMEOUT_SECONDS):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.parent / f".{path.name}.lock"
    deadline = time.monotonic() + timeout
    fd: int | None = None
    while fd is None:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(fd, str(os.getpid()).encode("ascii"))
        except FileExistsError:
            try:
                age = time.time() - lock.stat().st_mtime
                if age > STALE_LOCK_SECONDS:
                    lock.unlink(missing_ok=True)
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError(f"registry lock timeout: {lock}")
            time.sleep(0.05)
    try:
        yield
    finally:
        if fd is not None:
            os.close(fd)
        lock.unlink(missing_ok=True)


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


def _valid_conversation_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.hostname == "chatgpt.com" and parsed.path not in {"", "/"}


def record_thread(data: dict, identity: dict, *, thread_key: str, conversation_url: str, scope: str, task_id: str, summary: str) -> dict:
    if not _valid_conversation_url(conversation_url):
        raise ValueError("conversation_url must be a canonical chatgpt.com conversation URL")
    if not thread_key.strip():
        raise ValueError("thread_key must not be empty")
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
        previous_url = existing.get("conversation_url")
        if previous_url and previous_url != conversation_url:
            history = existing.setdefault("previous_conversations", [])
            if previous_url not in history:
                history.insert(0, previous_url)
                del history[5:]
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
            if args.command == "list":
                out = {"project": identity, "threads": list_threads(load_state(path), identity)}
            else:
                with registry_lock(path):
                    data = load_state(path)
                    if args.command == "record":
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
