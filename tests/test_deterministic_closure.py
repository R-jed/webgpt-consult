from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_packet_safety import scan
from consult_state import list_consults, load_consult, project_identity, save_consult, validate_snapshot
from model_router import ModelRoutingError, resolve_model_from_state, selection_is_confirmed
from result_verifier import verify
from submission_preflight import build_manifest


class SafetyTests(unittest.TestCase):
    def test_common_credentials_block(self):
        cases = [
            "Authorization: Bearer " + "abcdefghijklmnopqrstuvwxyz",
            "AWS_SECRET_ACCESS_KEY='" + "abcdefghijklmnopqrstuvwxyz1234567890" + "'",
            "token = '" + "abcdefghijklmnopqrstuvwxyz" + "'",
            "gl" + "pat-" + "abcdefghijklmnopqrstuvwxyz",
            "xo" + "xb-" + "1234567890-abcdefghijklmnop",
        ]
        for value in cases:
            with self.subTest(value=value):
                self.assertFalse(scan(value)["ok"])

    def test_absolute_path_warning_stops_at_space(self):
        text = "open /Users/alice/my file.py now"
        result = scan(text)
        finding = next(item for item in result["findings"] if item["type"] == "absolute_user_path")
        self.assertEqual(text[finding["start"]:finding["end"]], "/Users/alice/my")


class ModelRouterTests(unittest.TestCase):
    def test_unactionable_pro_falls_back_to_high(self):
        state = """
[1] <div role=menuitem>Models
  GPT-5.6 Sol
<div role=menuitemradio aria-disabled=true>Pro
[3] <div role=menuitemradio aria-checked=false>High
"""
        selection = resolve_model_from_state(state)
        self.assertEqual(selection.selected_tier, "High")
        self.assertTrue(selection.downgraded)

    def test_generic_gpt5_pro_testid_does_not_claim_56(self):
        state = '[1] <div data-testid=model-switcher-gpt-5-pro role=menuitemradio aria-checked=true>Pro'
        with self.assertRaises(ModelRoutingError):
            resolve_model_from_state(state)

    def test_checked_pro_confirmed(self):
        state = """
[1] <div role=menuitem>GPT-5.6 Sol
[2] <div role=menuitemradio aria-checked=true>Pro
[3] <div role=menuitemradio aria-checked=false>High
"""
        selection = resolve_model_from_state(state)
        self.assertTrue(selection_is_confirmed(state, selection))


class ResultVerifierTests(unittest.TestCase):
    def test_requires_exact_first_line_and_task_binding(self):
        self.assertTrue(verify("SENTINEL\nTask-ID: task-1\nResult", "SENTINEL", "task-1")["ok"])
        self.assertFalse(verify("I saw SENTINEL\nTask-ID: task-1", "SENTINEL", "task-1")["ok"])


class PreflightTests(unittest.TestCase):
    def test_attachment_secret_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet = root / "packet.md"
            packet.write_text("safe", encoding="utf-8")
            secret = root / "config.txt"
            secret.write_text("password='" + "supersecretvalue" + "'", encoding="utf-8")
            manifest = build_manifest(packet, [secret], task_id="t", sentinel="s", allow_unscanned_binary=False)
            self.assertFalse(manifest["ok"])

    def test_binary_requires_manual_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet = root / "packet.md"
            packet.write_text("safe", encoding="utf-8")
            image = root / "image.png"
            image.write_bytes(b"\x89PNG\x00binary")
            blocked = build_manifest(packet, [image], task_id="t", sentinel="s", allow_unscanned_binary=False)
            allowed = build_manifest(packet, [image], task_id="t", sentinel="s", allow_unscanned_binary=True)
            self.assertFalse(blocked["ok"])
            self.assertTrue(allowed["ok"])


class ConsultStateTests(unittest.TestCase):
    def _snapshot(self, url: str = "https://chatgpt.com/c/one") -> dict:
        return {
            "consult_id": "routing-architecture",
            "title": "Routing architecture review",
            "anchor": "branch:main",
            "conversation_url": url,
            "user_intent": "Keep routing simple and reliable",
            "standing_constraints": ["Chrome only"],
            "accepted_decisions": ["Pro then High"],
            "rejected_or_deferred": [],
            "open_questions": ["real browser validation"],
            "evidence_refs": ["commit:abc"],
            "current_state": "Deterministic routing is implemented",
            "last_task_id": "task-1",
        }

    def test_snapshot_round_trip_and_url_replacement(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"WEBGPT_CONSULT_STATE_DIR": tmp}):
            project = Path(tmp) / "project"
            project.mkdir()
            identity = project_identity(project)
            saved = save_consult(identity, self._snapshot())
            self.assertEqual(load_consult(identity, "routing-architecture")["conversation_url"], "https://chatgpt.com/c/one")

            updated = self._snapshot("https://chatgpt.com/c/two")
            updated["last_task_id"] = "task-2"
            updated["accepted_decisions"].append("Use durable local state")
            save_consult(identity, updated)
            loaded = load_consult(identity, "routing-architecture")
            self.assertEqual(loaded["conversation_url"], "https://chatgpt.com/c/two")
            self.assertEqual(loaded["created_at"], saved["created_at"])
            self.assertIn("Use durable local state", loaded["accepted_decisions"])

    def test_corrupt_consult_does_not_break_project_list(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"WEBGPT_CONSULT_STATE_DIR": tmp}):
            project = Path(tmp) / "project"
            project.mkdir()
            identity = project_identity(project)
            save_consult(identity, self._snapshot())
            project_state_dir = Path(tmp) / identity["fingerprint"]
            (project_state_dir / "broken.json").write_text("{bad json", encoding="utf-8")
            result = list_consults(identity)
            self.assertEqual(len(result["consults"]), 1)
            self.assertEqual(len(result["warnings"]), 1)

    def test_separate_checkouts_do_not_share_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "one"
            second = Path(tmp) / "two"
            first.mkdir()
            second.mkdir()
            for root in (first, second):
                subprocess.run(["git", "-C", str(root), "init"], check=True, capture_output=True)
                subprocess.run(["git", "-C", str(root), "remote", "add", "origin", "git@github.com:R-jed/example.git"], check=True)
            self.assertNotEqual(project_identity(first)["fingerprint"], project_identity(second)["fingerprint"])

    def test_snapshot_schema_rejects_invalid_chat_url(self):
        snapshot = self._snapshot("https://example.com/not-chatgpt")
        with self.assertRaises(ValueError):
            validate_snapshot(snapshot)

    def test_snapshot_lists_must_be_strings(self):
        snapshot = self._snapshot()
        snapshot["accepted_decisions"] = [123]
        with self.assertRaises(ValueError):
            validate_snapshot(snapshot)


class BundleCliTests(unittest.TestCase):
    def test_missing_input_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "bundle.md"
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "build_attachment_bundle.py"), str(Path(tmp) / "missing.md"), "-o", str(out)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(out.exists())

    def test_dynamic_fence_handles_four_backticks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "a.md"
            source.write_text("before\n````\ninside\n````\nafter", encoding="utf-8")
            out = root / "bundle.md"
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "build_attachment_bundle.py"), str(source), "-o", str(out)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("`````markdown", out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
