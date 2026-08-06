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
        self.assertIn("canonical executable browser protocol", skill)
        self.assertIn("browser-adapter execution steps", skill)

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

    def test_agent_readme_is_plain_bootstrap_not_second_runtime_spec(self) -> None:
        agent_readme = (REPO_ROOT / "README_Agent.md").read_text(encoding="utf-8")
        for required in (
            "## Read order",
            "## Rules that must stay true",
            "## Validation assets",
            "executable Chrome protocol",
            "full `CONTEXT_PACKET_V1`",
        ):
            self.assertIn(required, agent_readme)
        for duplicated_state_field in (
            "review_tab_handle",
            "current_task_id",
            "current_dispatch_state",
        ):
            self.assertNotIn(duplicated_state_field, agent_readme)

    def test_chrome_workflow_has_executable_adapter_mechanics(self) -> None:
        workflow = (SKILL_DIR / "references/chrome-workflow.md").read_text(encoding="utf-8")
        for required in (
            "Read the installed `chrome:control-chrome` Skill completely",
            "`node_repl js`",
            "`browser-client.mjs`",
            'agent.browsers.get("extension")',
            "Action discipline",
            'waitForEvent("filechooser")',
            'getByTestId("composer-plus-btn")',
            "Required invariants",
            "Cleanup decision matrix",
            "first non-empty assistant line to equal the current sentinel exactly",
        ):
            self.assertIn(required, workflow)

    def test_chrome_workflow_has_safe_fresh_conversation_path(self) -> None:
        workflow = (SKILL_DIR / "references/chrome-workflow.md").read_text(encoding="utf-8")
        for required in (
            "### Fresh conversation path",
            "create a new tab through the documented Chrome-control API",
            "record the exact new handle as Skill-owned",
            "navigate that tab to `https://chatgpt.com/`",
            "start from a fresh chat state",
            "Do not take over an unrelated user tab",
        ):
            self.assertIn(required, workflow)

    def test_chrome_workflow_has_live_fast_path_and_model_cache(self) -> None:
        workflow = (SKILL_DIR / "references/chrome-workflow.md").read_text(encoding="utf-8")
        for required in (
            "Live fast path",
            "without re-reading the previous sentinel",
            "Same live verified conversation with valid cache",
            "do not open picker",
            "browser runtime reset does not by itself invalidate a verified conversation-scoped model cache",
            "`UNKNOWN` is a dispatch state, not a model state",
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
        self.assertIn("Never create a replacement consultation or click Send again while `UNKNOWN` remains unresolved", workflow)
        self.assertIn("never click Send again for the same submission", workflow)
        self.assertIn("mark the consultation incomplete", workflow)

    def test_model_policy_keeps_pro_to_high_fallback(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        workflow = (SKILL_DIR / "references/chrome-workflow.md").read_text(encoding="utf-8")
        for text in (skill, workflow):
            self.assertIn("GPT-5.6 Sol Pro", text)
            self.assertIn("GPT-5.6 Sol High", text)
        self.assertIn("select GPT-5.6 Sol `Pro` when available, otherwise `High`", workflow)

    def test_bundle_is_canonical_multi_file_fallback(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        workflow = (SKILL_DIR / "references/chrome-workflow.md").read_text(encoding="utf-8")
        for text in (skill, workflow):
            self.assertIn("scripts/build_attachment_bundle.py", text)
            self.assertIn("original", text.lower())
        self.assertIn("--allow-partial", skill)

    def test_bundle_contract_uses_one_content_hash_and_explicit_unicode_only(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        workflow = (SKILL_DIR / "references/chrome-workflow.md").read_text(encoding="utf-8")
        agent_readme = (REPO_ROOT / "README_Agent.md").read_text(encoding="utf-8")
        bundle = (SKILL_DIR / "scripts/build_attachment_bundle.py").read_text(encoding="utf-8")

        self.assertIn("one `sha256`", skill)
        self.assertIn("BOM-declared UTF-8, UTF-16, or UTF-32", skill)
        self.assertIn("does not guess legacy encodings", agent_readme)
        self.assertIn("BOM-declared UTF-8, UTF-16, and UTF-32", workflow)

        self.assertIn("sha256: str", bundle)
        self.assertNotIn("source_sha256", bundle)
        self.assertNotIn("included_sha256", bundle)
        self.assertNotIn('errors="replace"', bundle)
        self.assertNotIn("charset-normalizer", bundle)
        self.assertNotIn("chardet", bundle)

    def test_runtime_stays_chrome_only(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Use the Codex Chrome capability only", skill)
        self.assertFalse((SKILL_DIR / "references/opencli-fallback.md").exists())
        self.assertFalse((SKILL_DIR / "scripts/run_gpt56_sol_pro_consult.py").exists())
        self.assertFalse((SKILL_DIR / "scripts/extract_chatgpt_reply.py").exists())

    def test_project_docs_use_only_project_native_product_language(self) -> None:
        product_docs = (
            REPO_ROOT / "README.md",
            REPO_ROOT / "README_en.md",
            REPO_ROOT / "README_Agent.md",
            SKILL_DIR / "SKILL.md",
            SKILL_DIR / "references/chrome-workflow.md",
            SKILL_DIR / "references/context-packet-template.md",
        )
        forbidden = (
            "gpt56-sol-pro-consult",
            "zhijian-skills",
            "upstream",
            "informed by",
            "incorporates and adapts",
            "adapted from",
            "inspired by",
            "吸收自",
            "借鉴",
            "参考其它项目",
            "参考其他项目",
            "学习自",
        )
        for path in product_docs:
            text = path.read_text(encoding="utf-8").lower()
            for phrase in forbidden:
                self.assertNotIn(phrase.lower(), text, f"{phrase!r} found in {path}")

        notice = (SKILL_DIR / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        self.assertIn("MIT License", notice)
        self.assertIn("Copyright (c) 2026 zjp1997720", notice)
        self.assertIn("gpt56-sol-pro-consult", notice)

    def test_metadata_matches_current_product_positioning(self) -> None:
        metadata = (SKILL_DIR / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("Verified multi-turn ChatGPT Web consultation", metadata)
        self.assertIn("allow_implicit_invocation: false", metadata)

    def test_evals_cover_real_failure_modes_and_product_paths(self) -> None:
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
            "GPT-5.6 Sol High",
            "Skill-owned",
        ):
            self.assertIn(concept, scenarios)
        self.assertGreaterEqual(len(payload["evals"]), 10)


if __name__ == "__main__":
    unittest.main()
