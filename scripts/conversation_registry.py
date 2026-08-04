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
ROLLOVER_MODES = frozenset({"branch", "fresh"})
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


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


def _find_thread(data: dict, identity: dict, thread_key: str) -> dict | None:
    bucket = data["projects"].get(identity["fingerprint"], {})
    return next((t for t in bucket.get("threads", []) if t.get("thread_key") == thread_key), None)


def rollover_plan(data: dict, identity: dict, thread_key: str) -> dict:
    thread = _find_thread(data, identity, thread_key)
    if thread is None or thread.get("status", "active") != "active":
        raise ValueError(f"active workstream not found: {thread_key}")
    base_task_id = thread.get("branch_base_task_id") or thread.get("last_task_id")
    if not base_task_id:
        raise ValueError("workstream has no branch base task id")
    return {
        "thread_key": thread_key,
        "current_conversation_url": thread["conversation_url"],
        "root_task_id": thread.get("root_task_id") or base_task_id,
        "branch_base_task_id": base_task_id,
        "last_task_id": thread.get("last_task_id"),
        "next_rollover_index": int(thread.get("rollover_count", 0)) + 1,
        "continuity_capsule_sha256": thread.get("continuity_capsule_sha256"),
    }


def record_thread(
    data: dict,
    identity: dict,
    *,
    thread_key: str,
    conversation_url: str,
    scope: str,
    task_id: str,
    summary: str,
    branch_base_task_id: str | None = None,
    parent_conversation_url: str | None = None,
    continuity_capsule_sha256: str | None = None,
    rollover: bool = False,
    rollover_mode: str | None = None,
) -> dict:
    if not _valid_conversation_url(conversation_url):
        raise ValueError("conversation_url must be a canonical chatgpt.com conversation URL")
    if parent_conversation_url and not _valid_conversation_url(parent_conversation_url):
        raise ValueError("parent_conversation_url must be a canonical chatgpt.com conversation URL")
    if not thread_key.strip():
        raise ValueError("thread_key must not be empty")
    if continuity_capsule_sha256 and not SHA256_RE.fullmatch(continuity_capsule_sha256):
        raise ValueError("continuity_capsule_sha256 must be a lowercase SHA-256 hex digest")
    if rollover and rollover_mode not in ROLLOVER_MODES:
        raise ValueError("rollover_mode must be branch or fresh when rollover is true")
    if not rollover and rollover_mode is not None:
        raise ValueError("rollover_mode is only valid with rollover")

    bucket = _project_bucket(data, identity)
    now = utc_now()
    existing = next((t for t in bucket["threads"] if t.get("thread_key") == thread_key), None)

    if existing and existing.get("status", "active") != "active":
        raise ValueError("retired workstream cannot be silently reactivated; use a new workstream key")

    previous_base = (existing or {}).get("branch_base_task_id") or (existing or {}).get("last_task_id")
    previous_root = (existing or {}).get("root_task_id") or previous_base
    if existing and branch_base_task_id and previous_base and branch_base_task_id != previous_base:
        raise ValueError("branch_base_task_id is stable and cannot be changed directly")

    effective_root = previous_root or task_id
    effective_base = previous_base or branch_base_task_id or task_id
    if rollover and rollover_mode == "fresh":
        effective_base = task_id

    payload = {
        "thread_key": thread_key,
        "conversation_url": conversation_url,
        "scope": scope.strip(),
        "last_task_id": task_id,
        "summary": summary.strip(),
        "root_task_id": effective_root,
        "branch_base_task_id": effective_base,
        "last_used_at": now,
        "status": "active",
    }
    if continuity_capsule_sha256:
        payload["continuity_capsule_sha256"] = continuity_capsule_sha256

    if existing:
        previous_url = existing.get("conversation_url")
        if previous_url != conversation_url and not rollover:
            raise ValueError("changing an active workstream conversation URL requires explicit rollover")
        if rollover:
            if not previous_url or previous_url == conversation_url:
                raise ValueError("rollover requires a new conversation URL")
            if not parent_conversation_url or parent_conversation_url != previous_url:
                raise ValueError("rollover parent must exactly match the current registered conversation")
            if not continuity_capsule_sha256:
                raise ValueError("rollover requires a validated continuity capsule SHA-256")
            history = existing.setdefault("previous_conversations", [])
            if previous_url not in history:
                history.insert(0, previous_url)
                del history[5:]
            payload["parent_conversation_url"] = previous_url
            payload["rollover_count"] = int(existing.get("rollover_count", 0)) + 1
            payload["last_rollover_at"] = now
            payload["last_rollover_mode"] = rollover_mode
        else:
            payload["rollover_count"] = int(existing.get("rollover_count", 0))
            if existing.get("parent_conversation_url"):
                payload["parent_conversation_url"] = existing["parent_conversation_url"]
            if existing.get("last_rollover_mode"):
                payload["last_rollover_mode"] = existing["last_rollover_mode"]
        existing.update(payload)
        result = existing
    else:
        if rollover:
            raise ValueError("cannot rollover an unregistered workstream")
        payload["created_at"] = now
        payload["rollover_count"] = 0
        bucket["threads"].append(payload)
        result = payload

    bucket["threads"] = sorted(
        bucket["threads"],
        key=lambda t: t.get("last_used_at", ""),
        reverse=True,
    )[:MAX_THREADS_PER_PROJECT]
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
    plan = sub.add_parser("plan-rollover")
    plan.add_argument("--thread-key", required=True)
    record = sub.add_parser("record")
    record.add_argument("--thread-key", required=True)
    record.add_argument("--conversation-url", required=True)
    record.add_argument("--scope", required=True)
    record.add_argument("--task-id", required=True)
    record.add_argument("--summary", default="")
    record.add_argument("--branch-base-task-id")
    record.add_argument("--parent-conversation-url")
    record.add_argument("--continuity-capsule-sha256")
    record.add_argument("--rollover", action="store_true")
    record.add_argument("--rollover-mode", choices=sorted(ROLLOVER_MODES))
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
            elif args.command == "plan-rollover":
                out = rollover_plan(load_state(path), identity, args.thread_key)
            else:
                with registry_lock(path):
                    data = load_state(path)
                    if args.command == "record":
                        out = record_thread(
                            data,
                            identity,
                            thread_key=args.thread_key,
                            conversation_url=args.conversation_url,
                            scope=args.scope,
                            task_id=args.task_id,
                            summary=args.summary,
                            branch_base_task_id=args.branch_base_task_id,
                            parent_conversation_url=args.parent_conversation_url,
                            continuity_capsule_sha256=args.continuity_capsule_sha256,
                            rollover=args.rollover,
                            rollover_mode=args.rollover_mode,
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
