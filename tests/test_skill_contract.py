#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_chrome_is_default_and_opencli_is_optional(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Use the Codex Chrome plugin by default", skill)
        self.assertIn("OpenCLI is optional and is not an installation prerequisite", skill)
        self.assertNotIn("For text-only consultations, default to the wrapper", skill)

    def test_required_public_files_exist(self) -> None:
        for relative in (
            "agents/openai.yaml",
            "references/chrome-workflow.md",
            "references/opencli-fallback.md",
            "references/context-packet-template.md",
        ):
            self.assertTrue((SKILL_DIR / relative).is_file(), relative)

    def test_no_personal_absolute_paths(self) -> None:
        for path in SKILL_DIR.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                text = path.read_text(encoding="utf-8", errors="ignore")
                for forbidden in ("/Users/" + "me/", "zhu" + "jinpeng", "deepsight_" + "vault"):
                    self.assertNotIn(forbidden, text, str(path))

    def test_evals_route_normal_requests_to_chrome(self) -> None:
        payload = json.loads((SKILL_DIR / "evals/evals.json").read_text(encoding="utf-8"))
        for case in payload["evals"]:
            self.assertIn("Chrome", case["expected_output"])

    # --- Phase 4: Pro > High > fail contract ---

    def test_pro_is_preferred(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Preferred", skill)
        self.assertNotIn("Pro required", skill)
        self.assertNotIn("Pro is mandatory", skill)

    def test_high_is_only_fallback(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Fallback", skill)
        self.assertIn("High", skill)

    def test_extra_high_unsupported(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Extra High", skill)
        self.assertIn("unsupported", skill.lower())

    def test_medium_unsupported(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Medium", skill)
        self.assertIn("unsupported", skill.lower())

    def test_instant_unsupported(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Instant", skill)
        self.assertIn("unsupported", skill.lower())

    def test_fail_closed_when_no_tier(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("fail closed", skill.lower())

    def test_no_extra_high_medium_in_routing_chain(self) -> None:
        """Extra High and Medium must not appear in the routing chain."""
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        lines = skill.split("\n")
        in_chain = False
        for line in lines:
            if "pro (preferred)" in line.lower():
                in_chain = True
            if in_chain and "↓" in line:
                self.assertNotIn("Extra High", line)
                self.assertNotIn("Medium", line)
            if in_chain and line.strip() == "" and "↓" not in line:
                in_chain = False

    def test_downgraded_status_reported(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("downgraded", skill.lower())

    def test_selected_tier_pro_or_high_only(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Selected tier: pro | high", skill)

    def test_no_deprecated_wrapper_in_runner(self) -> None:
        runner = (SKILL_DIR / "scripts" / "run_gpt56_sol_pro_consult.py").read_text(encoding="utf-8")
        self.assertNotIn("def ensure_gpt56_sol_pro", runner)

    def test_no_pro_required_in_runner_errors(self) -> None:
        runner = (SKILL_DIR / "scripts" / "run_gpt56_sol_pro_consult.py").read_text(encoding="utf-8")
        self.assertNotIn("Pro required", runner)
        self.assertNotIn("Pro was not visible", runner)

    def test_supported_tiers_in_router(self) -> None:
        router = (SKILL_DIR / "scripts" / "model_router.py").read_text(encoding="utf-8")
        self.assertIn("SUPPORTED_TIERS", router)
        self.assertIn("TIER_PRO", router)
        self.assertIn("TIER_HIGH", router)

    def test_no_adaptive_priority_in_router(self) -> None:
        """Old ADAPTIVE_PRIORITY with 4 tiers should be gone."""
        router = (SKILL_DIR / "scripts" / "model_router.py").read_text(encoding="utf-8")
        self.assertNotIn("ADAPTIVE_PRIORITY", router)
        self.assertNotIn("FALLBACK_TIERS", router)

    def test_no_medium_candidate_in_router(self) -> None:
        router = (SKILL_DIR / "scripts" / "model_router.py").read_text(encoding="utf-8")
        self.assertNotIn("TIER_MEDIUM", router)
        self.assertNotIn("TIER_EXTRA_HIGH", router)

    def test_opencli_uses_same_routing(self) -> None:
        opencli = (SKILL_DIR / "references" / "opencli-fallback.md").read_text(encoding="utf-8")
        self.assertIn("Pro > High > fail", opencli)

    def test_chrome_workflow_uses_same_routing(self) -> None:
        chrome = (SKILL_DIR / "references" / "chrome-workflow.md").read_text(encoding="utf-8")
        self.assertIn("Pro (preferred) → High → fail", chrome)

    # --- Final Hardening: implicit invocation ---

    def test_implicit_invocation_disabled(self) -> None:
        yaml_text = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: false", yaml_text)
        self.assertNotIn("allow_implicit_invocation: true", yaml_text)

    def test_ui_metadata_reflects_high_fallback(self) -> None:
        """Display name and description must not claim Pro-only."""
        yaml_text = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("GPT 5.6 Sol Consult", yaml_text)
        self.assertIn("Pro/High", yaml_text)
        self.assertNotIn("Pro second-opinion", yaml_text)
        self.assertNotIn("Pro Consult", yaml_text.split("display_name")[1].split("\n")[0])

    def test_opencli_architecture_wording(self) -> None:
        """opencli-fallback.md must accurately describe the architecture."""
        doc = (SKILL_DIR / "references" / "opencli-fallback.md").read_text(encoding="utf-8")
        self.assertIn("model_router.py", doc)
        self.assertIn("programmatically", doc)
        self.assertIn("documented browser workflow", doc)

    def test_untrusted_evidence_present(self) -> None:
        template = (SKILL_DIR / "references" / "context-packet-template.md").read_text(encoding="utf-8")
        self.assertIn("UNTRUSTED_EVIDENCE", template)
        self.assertIn("untrusted evidence", template)
        self.assertIn("not follow instructions", template.lower())

    def test_bundle_header_adaptive(self) -> None:
        bundler = (SKILL_DIR / "scripts" / "build_attachment_bundle.py").read_text(encoding="utf-8")
        self.assertIn("GPT 5.6 Sol Attachment Bundle", bundler)
        self.assertNotIn("Pro Attachment Bundle", bundler)


class TestNonceUniqueness(unittest.TestCase):
    """Session and sentinel nonces must be 12-char hex, independently randomized."""

    def test_session_nonce_format(self) -> None:
        import re
        runner = (SKILL_DIR / "scripts" / "run_gpt56_sol_pro_consult.py").read_text(encoding="utf-8")
        self.assertIn("uuid.uuid4().hex[:12]", runner)
        self.assertNotIn("uuid.uuid4().hex[:6]", runner)
        self.assertNotIn("uuid.uuid4().hex[:8]", runner)

    def test_sentinel_nonce_format(self) -> None:
        import re
        runner = (SKILL_DIR / "scripts" / "run_gpt56_sol_pro_consult.py").read_text(encoding="utf-8")
        # _generate_sentinel should use hex[:12]
        self.assertIn("nonce = uuid.uuid4().hex[:12]", runner)

    def test_sentinel_prefix_preserved(self) -> None:
        runner = (SKILL_DIR / "scripts" / "run_gpt56_sol_pro_consult.py").read_text(encoding="utf-8")
        self.assertIn("GPT56_SOL_PRO_RESULT_", runner)

    def test_two_independent_sentinels_differ(self) -> None:
        import sys
        sys.path.insert(0, str(SKILL_DIR / "scripts"))
        from run_gpt56_sol_pro_consult import _generate_sentinel
        a = _generate_sentinel()
        b = _generate_sentinel()
        self.assertEqual(len(a.split("_")[-1]), 12)
        self.assertEqual(len(b.split("_")[-1]), 12)
        self.assertTrue(a.startswith("GPT56_SOL_PRO_RESULT_"))
        self.assertTrue(b.startswith("GPT56_SOL_PRO_RESULT_"))
        # Random nonces should differ (extremely unlikely to collide with 12 hex chars)
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
