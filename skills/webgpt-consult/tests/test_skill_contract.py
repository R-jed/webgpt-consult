#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]


class SkillContractTests(unittest.TestCase):
    def test_required_runtime_files_exist(self) -> None:
        for relative in (
            "SKILL.md",
            "agents/openai.yaml",
            "references/chrome-workflow.md",
            "references/context-packet-template.md",
            "scripts/safety_guard.py",
            "scripts/build_attachment_bundle.py",
            "evals/evals.json",
            "THIRD_PARTY_NOTICES.md",
        ):
            self.assertTrue((SKILL_DIR / relative).is_file(), relative)

    def test_skill_uses_clear_runtime_authority_structure(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        for heading in (
            "## Runtime sources",
            "## Routing and requirements",
            "## Hard gates",
            "## Workflow",
            "## Context assembly",
            "## Attachments",
            "## Conversation continuity",
            "## Completion contract",
            "## Local integration",
            "## Failure handling",
        ):
            self.assertIn(heading, skill)
        self.assertIn("canonical browser state machine", skill)
        self.assertIn("belong exclusively to `references/chrome-workflow.md`", skill)

    def test_context_packet_retains_core_contract(self) -> None:
        packet = (SKILL_DIR / "references/context-packet-template.md").read_text(encoding="utf-8")
        for required in (
            "CONTEXT_PACKET_V1",
            '"task_id"',
            '"sentinel"',
            '"context_strategy"',
            '"credential_status"',
            '"context_hash"',
            '"required_output"',
            "## TASK",
            "## BACKGROUND",
            "## USER_INTENT",
            "## LOCAL_JUDGMENT",
            "## EVIDENCE",
            "## ATTEMPTS_SO_FAR",
            "## OPTIONS",
            "## RISKS",
            "## ASK",
            "## RETURN_FORMAT",
            "WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS_<same-nonce>",
            "## Follow-up delta packet",
            '"context_strategy": "same_conversation_delta"',
            "## CURRENT_DELTA",
            "## Integrity rules",
            "8,000 to 15,000 characters",
        ):
            self.assertIn(required, packet)

    def test_agent_readme_is_bootstrap_not_second_runtime_spec(self) -> None:
        agent_readme = (REPO_ROOT / "README_Agent.md").read_text(encoding="utf-8")
        for required in (
            "## Read order",
            "## Critical boundaries",
            "## Validation assets",
            "Browser state machine",
            "Full `CONTEXT_PACKET_V1`",
        ):
            self.assertIn(required, agent_readme)
        for duplicated_state_field in (
            "review_tab_handle",
            "current_task_id",
            "current_dispatch_state",
        ):
            self.assertNotIn(duplicated_state_field, agent_readme)

    def test_chrome_workflow_has_live_fast_path_and_model_cache(self) -> None:
        workflow = (SKILL_DIR / "references/chrome-workflow.md").read_text(encoding="utf-8")
        for required in (
            "Live fast path",
            "without re-reading the previous sentinel",
            "Do not reopen the picker per message",
            "A Chrome runtime reset alone does not invalidate the model cache",
            "current_task_id",
            "current_sentinel",
            "current_attachment_names",
            "current_dispatch_state: NOT_SENT",
            "current_conversation_url",
        ):
            self.assertIn(required, workflow)

    def test_chrome_workflow_blocks_duplicate_send(self) -> None:
        workflow = (SKILL_DIR / "references/chrome-workflow.md").read_text(encoding="utf-8")
        for state in ("NOT_SENT", "SENT", "UNKNOWN"):
            self.assertIn(state, workflow)
        self.assertIn("Never create a replacement consultation or click Send again", workflow)
        self.assertIn("mark it incomplete rather than risking a duplicate", workflow)

    def test_bundle_is_canonical_multi_file_fallback(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        workflow = (SKILL_DIR / "references/chrome-workflow.md").read_text(encoding="utf-8")
        for text in (skill, workflow):
            self.assertIn("scripts/build_attachment_bundle.py", text)
            self.assertIn("original", text.lower())
        self.assertIn("--allow-partial", skill)

    def test_runtime_stays_chrome_only(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Use the Codex Chrome capability only", skill)
        self.assertFalse((SKILL_DIR / "references/opencli-fallback.md").exists())
        self.assertFalse((SKILL_DIR / "scripts/run_gpt56_sol_pro_consult.py").exists())
        self.assertFalse((SKILL_DIR / "scripts/extract_chatgpt_reply.py").exists())

    def test_metadata_keeps_explicit_invocation(self) -> None:
        metadata = (SKILL_DIR / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: false", metadata)

    def test_evals_cover_real_failure_modes(self) -> None:
        payload = json.loads((SKILL_DIR / "evals/evals.json").read_text(encoding="utf-8"))
        scenarios = "\n".join(
            f"{case['prompt']}\n{case['expected_output']}" for case in payload["evals"]
        )
        for concept in (
            "CONTEXT_PACKET_V1",
            "build_attachment_bundle.py",
            "UNKNOWN",
            "model picker",
            "Show in text field",
            "already visible",
        ):
            self.assertIn(concept, scenarios)


if __name__ == "__main__":
    unittest.main()
