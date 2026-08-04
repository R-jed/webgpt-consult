from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_packet_safety import scan
from conversation_registry import project_identity, record_thread, list_threads
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
        ok = verify("SENTINEL\nTask-ID: task-1\nResult", "SENTINEL", "task-1")
        self.assertTrue(ok["ok"])
        bad = verify("I saw SENTINEL\nTask-ID: task-1", "SENTINEL", "task-1")
        self.assertFalse(bad["ok"])


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


class RegistryTests(unittest.TestCase):
    def test_project_scoped_multiple_threads(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            identity = project_identity(root)
            data = {"version": 1, "projects": {}}
            record_thread(data, identity, thread_key="architecture", conversation_url="https://chatgpt.com/c/a", scope="routing architecture", task_id="t1", summary="keep policy")
            record_thread(data, identity, thread_key="bug-42", conversation_url="https://chatgpt.com/c/b", scope="bug 42", task_id="t2", summary="repro found")
            threads = list_threads(data, identity)
            self.assertEqual({t["thread_key"] for t in threads}, {"architecture", "bug-42"})

    def test_git_subdirectories_share_project_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            child = root / "src"
            child.mkdir(parents=True)
            subprocess.run(["git", "-C", str(root), "init"], check=True, capture_output=True)
            self.assertEqual(project_identity(root)["fingerprint"], project_identity(child)["fingerprint"])

    def test_thread_rollover_preserves_previous_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = project_identity(Path(tmp))
            data = {"version": 1, "projects": {}}
            record_thread(data, identity, thread_key="architecture", conversation_url="https://chatgpt.com/c/one", scope="routing", task_id="t1", summary="one")
            updated = record_thread(data, identity, thread_key="architecture", conversation_url="https://chatgpt.com/c/two", scope="routing", task_id="t2", summary="two")
            self.assertEqual(updated["previous_conversations"], ["https://chatgpt.com/c/one"])


class BundleCliTests(unittest.TestCase):
    def test_missing_input_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "bundle.md"
            result = subprocess.run([sys.executable, str(SCRIPTS / "build_attachment_bundle.py"), str(Path(tmp) / "missing.md"), "-o", str(out)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(out.exists())

    def test_dynamic_fence_handles_four_backticks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "a.md"
            source.write_text("before\n````\ninside\n````\nafter", encoding="utf-8")
            out = root / "bundle.md"
            result = subprocess.run([sys.executable, str(SCRIPTS / "build_attachment_bundle.py"), str(source), "-o", str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            content = out.read_text(encoding="utf-8")
            self.assertIn("`````markdown", content)


if __name__ == "__main__":
    unittest.main()
