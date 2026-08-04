#!/usr/bin/env python3
"""Run a GPT 5.6 Sol Pro/High consultation through ChatGPT Web and OpenCLI."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path

from extract_chatgpt_reply import split_latest_assistant
from model_router import (
    ModelRoutingError,
    ModelSelection,
    resolve_model_from_state,
    selection_is_confirmed,
)


SKILL_DIR = Path(__file__).resolve().parents[1]
MODEL_LABELS = ("Pro", "Sol", "5.6", "极高", "Extra High", "High", "Medium", "Instant")
SEND_HINTS = (
    "data-testid=send-button",
    "aria-label=发送提示",
    "aria-label=Send prompt",
    "aria-label=Send message",
)
GENERATING_HINTS = (
    "data-testid=stop-button",
    "aria-label=停止回答",
    "aria-label=Stop generating",
    "aria-label=Stop streaming",
    "正在思考",
)


class ConsultError(RuntimeError):
    pass


def run_opencli(args: list[str], *, timeout: int = 60, check: bool = True) -> str:
    result = subprocess.run(
        ["opencli", *args],
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ConsultError(f"opencli {' '.join(args)} failed: {detail}")
    return result.stdout


def find_ref(state: str, predicate) -> str | None:
    for line in state.splitlines():
        if predicate(line):
            match = re.search(r"\[(\d+)\]", line)
            if match:
                return match.group(1)
    return None


def find_ref_by_block(state: str, first_line_predicate, block_predicate, lookahead: int = 8) -> str | None:
    lines = state.splitlines()
    for index, line in enumerate(lines):
        if not first_line_predicate(line):
            continue
        block = "\n".join(lines[index : index + lookahead])
        if not block_predicate(block):
            continue
        match = re.search(r"\[(\d+)\]", line)
        if match:
            return match.group(1)
    return None


def get_state(session: str) -> str:
    return run_opencli(["browser", session, "state"], timeout=30)


def click_ref(session: str, ref: str) -> None:
    run_opencli(["browser", session, "click", ref], timeout=30)


def find_model_button(state: str) -> str | None:
    return find_ref_by_block(
        state,
        lambda line: "<button" in line and "aria-haspopup=menu" in line,
        lambda block: any(label in block for label in MODEL_LABELS),
        lookahead=10,
    )


# ---------------------------------------------------------------------------
# Model selection – Pro > High > fail
# ---------------------------------------------------------------------------

def ensure_best_available_model(session: str) -> ModelSelection:
    """Select the best available GPT-5.6 Sol model (Pro or High).

    Flow:
        1. inspect current state
        2. open model picker
        3. capture full picker state
        4. resolve best candidate (Pro or High)
        5. if already checked → verify → return
        6. if not checked → require ref → click → fresh state → verify → return
        7. otherwise → fail closed
    """
    state = get_state(session)

    # Step 1-2: open model picker
    model_button = find_model_button(state)
    if not model_button:
        raise ConsultError("Could not find the ChatGPT model switcher button.")

    click_ref(session, model_button)
    menu_state = get_state(session)

    # Step 3-4: resolve best model from full picker state
    try:
        selection = resolve_model_from_state(menu_state)
    except ModelRoutingError as exc:
        run_opencli(["browser", session, "keys", "Escape"], timeout=10, check=False)
        raise ConsultError(str(exc)) from exc

    # Step 5: already checked → verify and return
    if selection_is_confirmed(menu_state, selection):
        run_opencli(["browser", session, "keys", "Escape"], timeout=10, check=False)
        return selection

    # Step 6: not checked → need to click
    if not selection.ref:
        run_opencli(["browser", session, "keys", "Escape"], timeout=10, check=False)
        raise ConsultError(
            f"Selected GPT-5.6 Sol {selection.selected_tier} but no actionable ref "
            "was available to select it."
        )

    click_ref(session, selection.ref)
    time.sleep(1)

    # Step 8: fresh state after click
    fresh_state = get_state(session)

    # Step 9: re-open picker to get full menu state for verification
    model_button = find_model_button(fresh_state)
    if not model_button:
        raise ConsultError(
            f"Selected GPT-5.6 Sol {selection.selected_tier}, but could not "
            "reopen the model switcher for verification."
        )
    click_ref(session, model_button)
    fresh_menu_state = get_state(session)

    # Step 10: verify with fresh state
    if selection_is_confirmed(fresh_menu_state, selection):
        run_opencli(["browser", session, "keys", "Escape"], timeout=10, check=False)
        return selection

    # Step 11: fail closed
    run_opencli(["browser", session, "keys", "Escape"], timeout=10, check=False)
    raise ConsultError(
        f"Selected GPT-5.6 Sol {selection.selected_tier}, but post-selection "
        "verification failed."
    )


# ---------------------------------------------------------------------------
# Packet / safety / sentinel helpers
# ---------------------------------------------------------------------------

def read_packet(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    return sys.stdin.read()


def run_safety_check(packet_path: Path, allow_warnings: bool) -> None:
    result = subprocess.run(
        [sys.executable, str(SKILL_DIR / "scripts" / "check_packet_safety.py"), str(packet_path)],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        # Never leak raw scanner output to stderr — findings may contain
        # redacted but still-sensitive context.  Use a safe summary instead.
        try:
            payload = json.loads(result.stdout)
            high_count = payload.get("high_count", "?")
            raise ConsultError(
                f"Packet safety check failed: {high_count} high-risk credential finding(s)."
            )
        except json.JSONDecodeError:
            raise ConsultError("Packet safety check failed: unparseable scanner output.")
    if not allow_warnings:
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            return
        if payload.get("warn_count", 0):
            print(result.stdout.strip(), file=sys.stderr)


def extract_sentinel(packet: str, explicit: str | None) -> str:
    """Extract or generate a unique sentinel for this consultation.

    If --sentinel is provided, use it directly.
    Otherwise generate one from the packet's embedded sentinel.
    The sentinel format is always: WEBGPT_CONSULT_RESULT_<timestamp>_<nonce>
    """
    if explicit:
        return explicit
    match = re.search(r"WEBGPT_CONSULT_RESULT_[A-Za-z0-9_:-]+", packet)
    if not match:
        raise ConsultError("Could not infer sentinel. Pass --sentinel or include WEBGPT_CONSULT_RESULT_... in the packet.")
    return match.group(0)


def _generate_sentinel() -> str:
    """Generate a collision-resistant sentinel for a new consultation."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    nonce = uuid.uuid4().hex[:12]
    return f"WEBGPT_CONSULT_RESULT_{ts}_{nonce}"


# ---------------------------------------------------------------------------
# Composer / send / reply helpers
# ---------------------------------------------------------------------------

def composer_ref(state: str) -> str | None:
    return find_ref(
        state,
        lambda line: (
            "id=prompt-textarea" in line
            and ("contenteditable=true" in line or "textarea" in line)
        ),
    )


def fill_composer(session: str, state: str, packet: str, sentinel: str) -> str:
    ref = composer_ref(state)
    if not ref:
        raise ConsultError("Could not find ChatGPT composer.")

    raw = run_opencli(["browser", session, "fill", ref, packet], timeout=120, check=False)
    try:
        fill_payload = json.loads(raw)
    except json.JSONDecodeError:
        fill_payload = {}

    if fill_payload and not fill_payload.get("filled"):
        raise ConsultError(f"Composer fill failed: {raw.strip()}")

    # Fail closed: always verify from fresh DOM, never trust the tool response alone.
    state_after_fill = get_state(session)
    if sentinel not in state_after_fill:
        raise ConsultError(
            "Composer fill could not be verified: sentinel not visible in fresh page state."
        )
    return state_after_fill


def send_ref(state: str) -> str | None:
    return find_ref(
        state,
        lambda line: "<button" in line and any(hint in line for hint in SEND_HINTS),
    )


def send_packet(session: str, state: str) -> None:
    ref = send_ref(state)
    if not ref:
        raise ConsultError("Could not find ChatGPT send button after filling composer.")
    click_ref(session, ref)


def extract_current(session: str) -> str:
    return run_opencli(
        ["browser", session, "extract", "--selector", "main", "--chunk-size", "40000"],
        timeout=60,
    )


def normalize_sentinel(text: str) -> str:
    return text.replace("\\_", "_")


def page_is_generating(state: str) -> bool:
    return any(hint in state for hint in GENERATING_HINTS)


def wait_for_reply(session: str, sentinel: str, timeout_seconds: int, poll_seconds: int) -> str:
    deadline = time.time() + timeout_seconds
    last_error = "Timed out before extraction started."

    while time.time() < deadline:
        time.sleep(poll_seconds)
        state = get_state(session)

        # Sentinel presence != completion.
        # Page must finish generating before extraction or sentinel check.
        if page_is_generating(state):
            last_error = "GPT 5.6 Sol is still generating/thinking; waiting for completion."
            continue

        # Generation stopped – extract the complete assistant turn.
        extract_json = extract_current(session)
        try:
            payload = json.loads(extract_json)
            reply = split_latest_assistant(str(payload.get("content", "")))
        except Exception as exc:
            last_error = f"Extraction failed after generation stopped: {exc}"
            continue

        normalized = normalize_sentinel(reply)
        if sentinel in normalized:
            return normalized
        last_error = f"Sentinel not found in completed assistant reply: {sentinel}"

    raise ConsultError(f"Timed out waiting for GPT 5.6 Sol reply: {last_error}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prompt-file", help="Path to a full context packet.")
    source.add_argument("--stdin", action="store_true", help="Read a full context packet from stdin.")
    parser.add_argument("--sentinel", help="Expected sentinel in the assistant reply.")
    parser.add_argument("--session", help="OpenCLI browser session name.")
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--poll", type=int, default=180)
    parser.add_argument("--skip-doctor", action="store_true")
    parser.add_argument("--skip-safety", action="store_true")
    parser.add_argument("--allow-warning-output", action="store_true")
    parser.add_argument(
        "--attachment",
        action="append",
        default=[],
        help="Not supported by this wrapper; use the Chrome file chooser workflow.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.attachment:
        print(
            "ERROR: This wrapper is text-only. Use the Chrome file chooser workflow for attachments.",
            file=sys.stderr,
        )
        return 2

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nonce = uuid.uuid4().hex[:12]
    session = args.session or f"gpt56-sol-{timestamp}-{nonce}"

    try:
        packet = read_packet(args)
        sentinel = extract_sentinel(packet, args.sentinel)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as file:
            file.write(packet)
            packet_path = Path(file.name)
        try:
            if not args.skip_safety:
                run_safety_check(packet_path, args.allow_warning_output)

            if not args.skip_doctor:
                run_opencli(["doctor"], timeout=60)

            run_opencli(["browser", session, "open", "https://chatgpt.com/"], timeout=60)
            selection = ensure_best_available_model(session)
            state = get_state(session)
            state = fill_composer(session, state, packet, sentinel)
            send_packet(session, state)
            reply = wait_for_reply(session, sentinel, args.timeout, args.poll)
        finally:
            packet_path.unlink(missing_ok=True)
    except ConsultError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"session={session}", file=sys.stderr)
    print(f"requested_tier={selection.requested_tier.lower()}", file=sys.stderr)
    print(f"selected_tier={selection.selected_tier.lower()}", file=sys.stderr)
    print(f"selected_model=GPT-5.6 Sol {selection.display_name}", file=sys.stderr)
    print(f"downgraded={'true' if selection.downgraded else 'false'}", file=sys.stderr)
    print("sentinel_verified=yes", file=sys.stderr)
    sys.stdout.write(reply)
    if not reply.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
