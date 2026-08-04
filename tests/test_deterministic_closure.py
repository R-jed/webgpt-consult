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
from continuity_capsule import validate_capsule
from conversation_registry import list_threads, project_identity, record_thread, rollover_plan
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


class ContinuityCapsuleTests(unittest.TestCase):
    def _capsule(self) -> str:
        headings = [
            "## WORKSTREAM",
            "## BASELINE",
            "## USER_INTENT",
            "## STANDING_CONSTRAINTS",
            "## ACCEPTED_DECISIONS",
            "## REJECTED_OR_DEFERRED_PATHS",
            "## OPEN_QUESTIONS",
            "## EVIDENCE_INDEX",
            "## CURRENT_STATE",
            "## CURRENT_ASK",
            "## COVERAGE_ATTESTATION",
        ]
        body = [
            "CONTINUITY_CAPSULE_V1",
            "Base-Task-ID: t1",
            "Last-Task-ID: t9",
            "Material-Reusable-Context-Omitted: no",
        ]
        for heading in headings:
            body.extend(["", heading, "state"])
        return "\n".join(body) + "\n"

    def test_valid_capsule_has_hash(self):
        result = validate_capsule(self._capsule(), base_task_id="t1", last_task_id="t9")
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["sha256"]), 64)

    def test_capsule_requires_no_omission_attestation(self):
        text = self._capsule().replace("Material-Reusable-Context-Omitted: no", "Material-Reusable-Context-Omitted: yes")
        result = validate_capsule(text, base_task_id="t1", last_task_id="t9")
        self.assertFalse(result["ok"])


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

    def test_active_url_change_requires_explicit_rollover(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = project_identity(Path(tmp))
            data = {"version": 1, "projects": {}}
            record_thread(data, identity, thread_key="architecture", conversation_url="https://chatgpt.com/c/one", scope="routing", task_id="t1", summary="one")
            with self.assertRaises(ValueError):
                record_thread(data, identity, thread_key="architecture", conversation_url="https://chatgpt.com/c/two", scope="routing", task_id="t2", summary="two")

    def test_rollover_plan_keeps_stable_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = project_identity(Path(tmp))
            data = {"version": 1, "projects": {}}
            record_thread(data, identity, thread_key="architecture", conversation_url="https://chatgpt.com/c/one", scope="routing", task_id="t1", summary="one")
            record_thread(data, identity, thread_key="architecture", conversation_url="https://chatgpt.com/c/one", scope="routing", task_id="t2", summary="two")
            plan = rollover_plan(data, identity, "architecture")
            self.assertEqual(plan["root_task_id"], "t1")
            self.assertEqual(plan["branch_base_task_id"], "t1")
            self.assertEqual(plan["last_task_id"], "t2")
            self.assertEqual(plan["next_rollover_index"], 1)

    def test_branch_rollover_preserves_base_and_records_lineage(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = project_identity(Path(tmp))
            data = {"version": 1, "projects": {}}
            record_thread(data, identity, thread_key="architecture", conversation_url="https://chatgpt.com/c/one", scope="routing", task_id="t1", summary="one")
            updated = record_thread(
                data,
                identity,
                thread_key="architecture",
                conversation_url="https://chatgpt.com/c/two",
                scope="routing",
                task_id="t3",
                summary="rolled",
                parent_conversation_url="https://chatgpt.com/c/one",
                continuity_capsule_sha256="a" * 64,
                rollover=True,
                rollover_mode="branch",
            )
            self.assertEqual(updated["root_task_id"], "t1")
            self.assertEqual(updated["branch_base_task_id"], "t1")
            self.assertEqual(updated["parent_conversation_url"], "https://chatgpt.com/c/one")
            self.assertEqual(updated["rollover_count"], 1)
            self.assertEqual(updated["last_rollover_mode"], "branch")
            self.assertEqual(updated["continuity_capsule_sha256"], "a" * 64)
            self.assertEqual(updated["previous_conversations"], ["https://chatgpt.com/c/one"])

    def test_fresh_rollover_resets_active_base_but_preserves_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = project_identity(Path(tmp))
            data = {"version": 1, "projects": {}}
            record_thread(data, identity, thread_key="architecture", conversation_url="https://chatgpt.com/c/one", scope="routing", task_id="t1", summary="one")
            updated = record_thread(
                data,
                identity,
                thread_key="architecture",
                conversation_url="https://chatgpt.com/c/fresh",
                scope="routing",
                task_id="t10",
                summary="fresh rollover",
                parent_conversation_url="https://chatgpt.com/c/one",
                continuity_capsule_sha256="b" * 64,
                rollover=True,
                rollover_mode="fresh",
            )
            self.assertEqual(updated["root_task_id"], "t1")
            self.assertEqual(updated["branch_base_task_id"], "t10")
            self.assertEqual(updated["last_rollover_mode"], "fresh")
            plan = rollover_plan(data, identity, "architecture")
            self.assertEqual(plan["branch_base_task_id"], "t10")
            self.assertEqual(plan["next_rollover_index"], 2)

    def test_rollover_requires_new_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = project_identity(Path(tmp))
            data = {"version": 1, "projects": {}}
            record_thread(data, identity, thread_key="architecture", conversation_url="https://chatgpt.com/c/one", scope="routing", task_id="t1", summary="one")
            with self.assertRaises(ValueError):
                record_thread(
                    data,
                    identity,
                    thread_key="architecture",
                    conversation_url="https://chatgpt.com/c/one",
                    scope="routing",
                    task_id="t2",
                    summary="bad rollover",
                    parent_conversation_url="https://chatgpt.com/c/one",
                    continuity_capsule_sha256="c" * 64,
                    rollover=True,
                    rollover_mode="branch",
                )

    def test_rollover_requires_capsule_hash_and_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = project_identity(Path(tmp))
            data = {"version": 1, "projects": {}}
            record_thread(data, identity, thread_key="architecture", conversation_url="https://chatgpt.com/c/one", scope="routing", task_id="t1", summary="one")
            with self.assertRaises(ValueError):
                record_thread(
                    data,
                    identity,
                    thread_key="architecture",
                    conversation_url="https://chatgpt.com/c/two",
                    scope="routing",
                    task_id="t2",
                    summary="missing mode",
                    parent_conversation_url="https://chatgpt.com/c/one",
                    continuity_capsule_sha256="d" * 64,
                    rollover=True,
                )

    def test_branch_base_cannot_be_repointed_directly(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = project_identity(Path(tmp))
            data = {"version": 1, "projects": {}}
            record_thread(data, identity, thread_key="architecture", conversation_url="https://chatgpt.com/c/one", scope="routing", task_id="t1", summary="one")
            with self.assertRaises(ValueError):
                record_thread(
                    data,
                    identity,
                    thread_key="architecture",
                    conversation_url="https://chatgpt.com/c/one",
                    scope="routing",
                    task_id="t2",
                    summary="two",
                    branch_base_task_id="other",
                )


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
