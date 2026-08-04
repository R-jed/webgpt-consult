#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from model_router import (
    SUPPORTED_TIERS,
    TIER_HIGH,
    TIER_PRO,
    ModelRoutingError,
    discover_model_candidates,
    resolve_model_from_state,
    select_best_model,
    selection_is_confirmed,
)


# ---------------------------------------------------------------------------
# Realistic multi-line DOM states used across tests
# ---------------------------------------------------------------------------

MENU_PRO_AND_HIGH = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio data-testid=model-switcher-gpt-5-pro aria-checked=false>Pro
[42] <div role=menuitemradio aria-checked=false>High
[43] <div role=menuitemradio aria-checked=false>Extra High
[44] <div role=menuitemradio aria-checked=false>Medium"""

MENU_PRO_ONLY = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio data-testid=model-switcher-gpt-5-6-pro aria-checked=true>Pro
[43] <div role=menuitemradio aria-checked=false>Extra High
[44] <div role=menuitemradio aria-checked=false>Medium"""

MENU_HIGH_ONLY = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[42] <div role=menuitemradio aria-checked=true>High
[43] <div role=menuitemradio aria-checked=false>Extra High
[44] <div role=menuitemradio aria-checked=false>Medium"""

MENU_MEDIUM_ONLY = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[44] <div role=menuitemradio aria-checked=true>Medium"""

MENU_EXTRA_HIGH_ONLY = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[43] <div role=menuitemradio aria-checked=true>Extra High"""

MENU_EXTRA_HIGH_AND_MEDIUM = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[43] <div role=menuitemradio aria-checked=true>Extra High
[44] <div role=menuitemradio aria-checked=false>Medium"""

MENU_NO_FAMILY_BARE_PRO = """\
[41] <div role=menuitemradio aria-checked=true>Pro"""

MENU_NO_FAMILY_BARE_HIGH = """\
[42] <div role=menuitemradio aria-checked=true>High"""

MENU_LEGACY_GPT55_PRO = """\
[12] <div role=menuitemradio data-testid=model-switcher-gpt-5-5-pro aria-checked=true>GPT 5.5 Pro"""

MENU_PRO_EXTENDED = """\
[13] <div role=menuitemradio aria-checked=true>Pro Extended"""

MENU_UNKNOWN_MODEL = """\
[99] <div role=menuitemradio aria-checked=true>Quantum Ultra"""

MENU_EMPTY = """\
[20] <div role=menuitem>
  GPT-5.6 Sol"""

MENU_INSTANT_ONLY = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[45] <div role=menuitemradio aria-checked=true>Instant"""


# ---------------------------------------------------------------------------
# Discovery tests
# ---------------------------------------------------------------------------

class TestDiscoverCandidates(unittest.TestCase):
    """Tests for discover_model_candidates() – Pro and High only."""

    def test_pro_and_high_both_discovered(self) -> None:
        candidates = discover_model_candidates(MENU_PRO_AND_HIGH)
        tiers = {c.tier for c in candidates}
        self.assertIn(TIER_PRO, tiers)
        self.assertIn(TIER_HIGH, tiers)

    def test_extra_high_not_discovered(self) -> None:
        candidates = discover_model_candidates(MENU_EXTRA_HIGH_ONLY)
        self.assertEqual(candidates, [])

    def test_medium_not_discovered(self) -> None:
        candidates = discover_model_candidates(MENU_MEDIUM_ONLY)
        self.assertEqual(candidates, [])

    def test_extra_high_and_medium_not_discovered(self) -> None:
        candidates = discover_model_candidates(MENU_EXTRA_HIGH_AND_MEDIUM)
        self.assertEqual(candidates, [])

    def test_instant_not_discovered(self) -> None:
        candidates = discover_model_candidates(MENU_INSTANT_ONLY)
        self.assertEqual(candidates, [])

    def test_unknown_not_discovered(self) -> None:
        candidates = discover_model_candidates(MENU_UNKNOWN_MODEL)
        self.assertEqual(candidates, [])

    def test_bare_pro_without_family_rejected(self) -> None:
        candidates = discover_model_candidates(MENU_NO_FAMILY_BARE_PRO)
        self.assertEqual(candidates, [])

    def test_bare_high_without_family_rejected(self) -> None:
        candidates = discover_model_candidates(MENU_NO_FAMILY_BARE_HIGH)
        self.assertEqual(candidates, [])

    def test_legacy_gpt55_pro_rejected(self) -> None:
        candidates = discover_model_candidates(MENU_LEGACY_GPT55_PRO)
        self.assertEqual(candidates, [])

    def test_pro_extended_rejected(self) -> None:
        candidates = discover_model_candidates(MENU_PRO_EXTENDED)
        self.assertEqual(candidates, [])

    def test_empty_menu_no_candidates(self) -> None:
        candidates = discover_model_candidates(MENU_EMPTY)
        self.assertEqual(candidates, [])


# ---------------------------------------------------------------------------
# Selection tests
# ---------------------------------------------------------------------------

class TestSelectBestModel(unittest.TestCase):
    """Tests for select_best_model() and the full resolve pipeline."""

    def test_pro_and_high_selects_pro(self) -> None:
        result = resolve_model_from_state(MENU_PRO_AND_HIGH)
        self.assertEqual(result.selected_tier, TIER_PRO)
        self.assertFalse(result.downgraded)

    def test_pro_unavailable_high_selected(self) -> None:
        result = resolve_model_from_state(MENU_HIGH_ONLY)
        self.assertEqual(result.selected_tier, TIER_HIGH)
        self.assertTrue(result.downgraded)

    def test_pro_only_selects_pro(self) -> None:
        result = resolve_model_from_state(MENU_PRO_ONLY)
        self.assertEqual(result.selected_tier, TIER_PRO)
        self.assertFalse(result.downgraded)

    def test_medium_only_raises(self) -> None:
        with self.assertRaises(ModelRoutingError):
            resolve_model_from_state(MENU_MEDIUM_ONLY)

    def test_extra_high_only_raises(self) -> None:
        with self.assertRaises(ModelRoutingError):
            resolve_model_from_state(MENU_EXTRA_HIGH_ONLY)

    def test_extra_high_and_medium_raises(self) -> None:
        with self.assertRaises(ModelRoutingError):
            resolve_model_from_state(MENU_EXTRA_HIGH_AND_MEDIUM)

    def test_instant_only_raises(self) -> None:
        with self.assertRaises(ModelRoutingError):
            resolve_model_from_state(MENU_INSTANT_ONLY)

    def test_empty_menu_raises(self) -> None:
        with self.assertRaises(ModelRoutingError):
            resolve_model_from_state(MENU_EMPTY)

    def test_no_valid_candidates_raises(self) -> None:
        with self.assertRaises(ModelRoutingError):
            resolve_model_from_state(MENU_NO_FAMILY_BARE_PRO)

    def test_requested_tier_always_pro(self) -> None:
        for menu in (MENU_PRO_AND_HIGH, MENU_HIGH_ONLY, MENU_PRO_ONLY):
            result = resolve_model_from_state(menu)
            self.assertEqual(result.requested_tier, TIER_PRO)


# ---------------------------------------------------------------------------
# selection_is_confirmed tests
# ---------------------------------------------------------------------------

class TestSelectionIsConfirmed(unittest.TestCase):
    """Tests for selection_is_confirmed() – Pro or High only."""

    def test_checked_pro_confirmed(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio data-testid=model-switcher-gpt-5-pro aria-checked=true>Pro"""
        result = resolve_model_from_state(state)
        self.assertTrue(selection_is_confirmed(state, result))

    def test_checked_high_confirmed(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[42] <div role=menuitemradio aria-checked=true>High"""
        result = resolve_model_from_state(state)
        self.assertTrue(selection_is_confirmed(state, result))

    def test_unchecked_pro_returns_false(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio data-testid=model-switcher-gpt-5-pro aria-checked=false>Pro
[42] <div role=menuitemradio aria-checked=true>High"""
        result = resolve_model_from_state(state)
        self.assertFalse(selection_is_confirmed(state, result))

    def test_tier_mismatch_returns_false(self) -> None:
        """Router picks Pro but state shows High checked → False."""
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio data-testid=model-switcher-gpt-5-pro aria-checked=false>Pro
[42] <div role=menuitemradio aria-checked=true>High"""
        result = resolve_model_from_state(state)
        self.assertFalse(selection_is_confirmed(state, result))

    def test_pro_bare_with_family_confirmed(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio aria-checked=true>Pro"""
        result = resolve_model_from_state(state)
        self.assertTrue(selection_is_confirmed(state, result))

    def test_empty_state_raises(self) -> None:
        selection = resolve_model_from_state(MENU_PRO_ONLY)
        with self.assertRaises(ValueError):
            selection_is_confirmed("", selection)

    def test_high_without_family_returns_false(self) -> None:
        state = """\
[42] <div role=menuitemradio aria-checked=true>High"""
        result = resolve_model_from_state(MENU_HIGH_ONLY)
        self.assertFalse(selection_is_confirmed(state, result))


# ---------------------------------------------------------------------------
# Ref hardening tests
# ---------------------------------------------------------------------------

class TestRefHardening(unittest.TestCase):
    """Tests proving ref is action locator, not model truth."""

    def test_ref_checked_but_no_family_evidence(self) -> None:
        from model_router import ModelSelection
        state = """\
[42] <div role=menuitemradio aria-checked=true>High"""
        selection = ModelSelection(
            requested_tier=TIER_PRO,
            selected_tier=TIER_HIGH,
            display_name="High",
            ref="42",
            downgraded=True,
            evidence="test",
        )
        self.assertFalse(selection_is_confirmed(state, selection))

    def test_extra_high_must_not_match_high(self) -> None:
        """Extra High checked must not be confirmed as High."""
        from model_router import ModelSelection
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[43] <div role=menuitemradio aria-checked=true>Extra High"""
        selection = ModelSelection(
            requested_tier=TIER_PRO,
            selected_tier=TIER_HIGH,
            display_name="High",
            ref="43",
            downgraded=True,
            evidence="test",
        )
        self.assertFalse(selection_is_confirmed(state, selection))

    def test_correct_high_family_verified_ref_changed(self) -> None:
        """Correct High, family verified, ref changed after DOM refresh → True."""
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[99] <div role=menuitemradio aria-checked=true>High"""
        selection = resolve_model_from_state(MENU_HIGH_ONLY)
        self.assertTrue(selection_is_confirmed(state, selection))


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases(unittest.TestCase):
    """Edge case and integration tests."""

    def test_supported_tiers_only_pro_and_high(self) -> None:
        self.assertEqual(SUPPORTED_TIERS, (TIER_PRO, TIER_HIGH))

    def test_pro_only_menu_selects_pro(self) -> None:
        result = resolve_model_from_state(MENU_PRO_ONLY)
        self.assertEqual(result.selected_tier, TIER_PRO)
        self.assertFalse(result.downgraded)
        self.assertEqual(result.display_name, "Pro")

    def test_candidate_ref_extracted(self) -> None:
        candidates = discover_model_candidates(MENU_PRO_AND_HIGH)
        refs = {c.ref for c in candidates}
        self.assertIn("41", refs)
        self.assertIn("42", refs)


# ---------------------------------------------------------------------------
# Execution-level tests (mocked browser boundary)
# ---------------------------------------------------------------------------

MOCK_SESSION = "test-session"


class TestExecutionRouting(unittest.TestCase):
    """Tests that ensure_best_available_model() drives the correct flow."""

    # A: Medium checked, Pro available → click Pro → verify → Pro
    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.click_ref")
    @patch("run_gpt56_sol_pro_consult.find_model_button")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_a_medium_upgrades_to_pro(
        self, mock_opencli, mock_find_btn, mock_click, mock_get_state
    ):
        from run_gpt56_sol_pro_consult import ensure_best_available_model

        menu_picker = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio data-testid=model-switcher-gpt-5-pro aria-checked=false>Pro
[42] <div role=menuitemradio aria-checked=false>High
[44] <div role=menuitemradio aria-checked=true>Medium"""

        menu_after_pro_click = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio data-testid=model-switcher-gpt-5-pro aria-checked=true>Pro
[42] <div role=menuitemradio aria-checked=false>High"""

        mock_get_state.side_effect = [
            "initial-state",
            menu_picker,
            "after-pro-click",
            menu_after_pro_click,
        ]
        mock_find_btn.return_value = "10"
        mock_opencli.return_value = ""

        selection = ensure_best_available_model(MOCK_SESSION)
        self.assertEqual(selection.selected_tier, TIER_PRO)
        self.assertFalse(selection.downgraded)

    # B: Medium checked, High available → click High → verify → High
    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.click_ref")
    @patch("run_gpt56_sol_pro_consult.find_model_button")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_b_medium_upgrades_to_high(
        self, mock_opencli, mock_find_btn, mock_click, mock_get_state
    ):
        from run_gpt56_sol_pro_consult import ensure_best_available_model

        menu_picker = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[42] <div role=menuitemradio aria-checked=false>High
[44] <div role=menuitemradio aria-checked=true>Medium"""

        menu_after_high_click = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[42] <div role=menuitemradio aria-checked=true>High
[44] <div role=menuitemradio aria-checked=false>Medium"""

        mock_get_state.side_effect = [
            "initial-state",
            menu_picker,
            "after-high-click",
            menu_after_high_click,
        ]
        mock_find_btn.return_value = "10"
        mock_opencli.return_value = ""

        selection = ensure_best_available_model(MOCK_SESSION)
        self.assertEqual(selection.selected_tier, TIER_HIGH)
        self.assertTrue(selection.downgraded)

    # C: Medium only → fail
    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.click_ref")
    @patch("run_gpt56_sol_pro_consult.find_model_button")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_c_medium_only_fails(
        self, mock_opencli, mock_find_btn, mock_click, mock_get_state
    ):
        from run_gpt56_sol_pro_consult import ConsultError, ensure_best_available_model

        menu = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[44] <div role=menuitemradio aria-checked=true>Medium"""

        mock_get_state.side_effect = ["initial-state", menu]
        mock_find_btn.return_value = "10"
        mock_opencli.return_value = ""

        with self.assertRaises(ConsultError) as ctx:
            ensure_best_available_model(MOCK_SESSION)
        self.assertIn("No verified GPT-5.6 Sol Pro or High", str(ctx.exception))

    # D: Extra High only → fail
    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.click_ref")
    @patch("run_gpt56_sol_pro_consult.find_model_button")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_d_extra_high_only_fails(
        self, mock_opencli, mock_find_btn, mock_click, mock_get_state
    ):
        from run_gpt56_sol_pro_consult import ConsultError, ensure_best_available_model

        menu = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[43] <div role=menuitemradio aria-checked=true>Extra High"""

        mock_get_state.side_effect = ["initial-state", menu]
        mock_find_btn.return_value = "10"
        mock_opencli.return_value = ""

        with self.assertRaises(ConsultError) as ctx:
            ensure_best_available_model(MOCK_SESSION)
        self.assertIn("No verified GPT-5.6 Sol Pro or High", str(ctx.exception))

    # E: High already checked, Pro absent → no click → verify → High
    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.click_ref")
    @patch("run_gpt56_sol_pro_consult.find_model_button")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_e_high_already_checked_no_click(
        self, mock_opencli, mock_find_btn, mock_click, mock_get_state
    ):
        from run_gpt56_sol_pro_consult import ensure_best_available_model

        menu = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[42] <div role=menuitemradio aria-checked=true>High"""

        mock_get_state.side_effect = ["initial-state", menu]
        mock_find_btn.return_value = "10"
        mock_opencli.return_value = ""

        selection = ensure_best_available_model(MOCK_SESSION)
        self.assertEqual(selection.selected_tier, TIER_HIGH)
        self.assertEqual(mock_click.call_count, 1)

    # F: High checked, Pro present → upgrade Pro
    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.click_ref")
    @patch("run_gpt56_sol_pro_consult.find_model_button")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_f_upgrades_high_to_pro(
        self, mock_opencli, mock_find_btn, mock_click, mock_get_state
    ):
        from run_gpt56_sol_pro_consult import ensure_best_available_model

        menu_picker = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio data-testid=model-switcher-gpt-5-pro aria-checked=false>Pro
[42] <div role=menuitemradio aria-checked=true>High"""

        menu_after_pro_click = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio data-testid=model-switcher-gpt-5-pro aria-checked=true>Pro
[42] <div role=menuitemradio aria-checked=false>High"""

        mock_get_state.side_effect = [
            "initial-state",
            menu_picker,
            "after-pro-click",
            menu_after_pro_click,
        ]
        mock_find_btn.return_value = "10"
        mock_opencli.return_value = ""

        selection = ensure_best_available_model(MOCK_SESSION)
        self.assertEqual(selection.selected_tier, TIER_PRO)
        self.assertFalse(selection.downgraded)

    # G: click High succeeds but fresh DOM says Medium → verification failure
    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.click_ref")
    @patch("run_gpt56_sol_pro_consult.find_model_button")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_g_verification_failure(
        self, mock_opencli, mock_find_btn, mock_click, mock_get_state
    ):
        from run_gpt56_sol_pro_consult import ConsultError, ensure_best_available_model

        menu_picker = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[42] <div role=menuitemradio aria-checked=false>High
[44] <div role=menuitemradio aria-checked=true>Medium"""

        menu_still_medium = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[42] <div role=menuitemradio aria-checked=false>High
[44] <div role=menuitemradio aria-checked=true>Medium"""

        mock_get_state.side_effect = [
            "initial-state",
            menu_picker,
            "after-click",
            menu_still_medium,
        ]
        mock_find_btn.return_value = "10"
        mock_opencli.return_value = ""

        with self.assertRaises(ConsultError) as ctx:
            ensure_best_available_model(MOCK_SESSION)
        self.assertIn("post-selection verification failed", str(ctx.exception))

    # H: bare High without family → fail
    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.click_ref")
    @patch("run_gpt56_sol_pro_consult.find_model_button")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_h_bare_high_fails(
        self, mock_opencli, mock_find_btn, mock_click, mock_get_state
    ):
        from run_gpt56_sol_pro_consult import ConsultError, ensure_best_available_model

        menu = """\
[42] <div role=menuitemradio aria-checked=true>High"""

        mock_get_state.side_effect = ["initial-state", menu]
        mock_find_btn.return_value = "10"
        mock_opencli.return_value = ""

        with self.assertRaises(ConsultError):
            ensure_best_available_model(MOCK_SESSION)

    # I: GPT-5.5 Pro → fail
    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.click_ref")
    @patch("run_gpt56_sol_pro_consult.find_model_button")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_i_gpt55_pro_fails(
        self, mock_opencli, mock_find_btn, mock_click, mock_get_state
    ):
        from run_gpt56_sol_pro_consult import ConsultError, ensure_best_available_model

        menu = """\
[12] <div role=menuitemradio data-testid=model-switcher-gpt-5-5-pro aria-checked=true>GPT 5.5 Pro"""

        mock_get_state.side_effect = ["initial-state", menu]
        mock_find_btn.return_value = "10"
        mock_opencli.return_value = ""

        with self.assertRaises(ConsultError):
            ensure_best_available_model(MOCK_SESSION)

    # J: Pro Extended → fail
    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.click_ref")
    @patch("run_gpt56_sol_pro_consult.find_model_button")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_j_pro_extended_fails(
        self, mock_opencli, mock_find_btn, mock_click, mock_get_state
    ):
        from run_gpt56_sol_pro_consult import ConsultError, ensure_best_available_model

        menu = """\
[13] <div role=menuitemradio aria-checked=true>Pro Extended"""

        mock_get_state.side_effect = ["initial-state", menu]
        mock_find_btn.return_value = "10"
        mock_opencli.return_value = ""

        with self.assertRaises(ConsultError):
            ensure_best_available_model(MOCK_SESSION)

    # K: selection_is_confirmed mismatch → False, not ValueError
    def test_k_confirmation_mismatch_is_false(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[42] <div role=menuitemradio aria-checked=false>High"""
        selection = resolve_model_from_state(MENU_HIGH_ONLY)
        result = selection_is_confirmed(state, selection)
        self.assertFalse(result)

    # L: Mixed family – GPT-5.5 Pro checked, GPT-5.6 Sol High available
    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.click_ref")
    @patch("run_gpt56_sol_pro_consult.find_model_button")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_l_gpt55_pro_checked_gpt56_high_available(
        self, mock_opencli, mock_find_btn, mock_click, mock_get_state
    ):
        from run_gpt56_sol_pro_consult import ensure_best_available_model

        menu = """\
[10] <div role=menuitem>
  GPT-5.5
[12] <div role=menuitemradio data-testid=model-switcher-gpt-5-5-pro aria-checked=true>GPT 5.5 Pro
[20] <div role=menuitem>
  GPT-5.6 Sol
[42] <div role=menuitemradio aria-checked=false>High"""

        menu_after_high_click = """\
[10] <div role=menuitem>
  GPT-5.5
[12] <div role=menuitemradio data-testid=model-switcher-gpt-5-5-pro aria-checked=false>GPT 5.5 Pro
[20] <div role=menuitem>
  GPT-5.6 Sol
[42] <div role=menuitemradio aria-checked=true>High"""

        mock_get_state.side_effect = [
            "initial-state",
            menu,
            "after-high-click",
            menu_after_high_click,
        ]
        mock_find_btn.return_value = "10"
        mock_opencli.return_value = ""

        selection = ensure_best_available_model(MOCK_SESSION)
        # Must select GPT-5.6 Sol High, never GPT-5.5 Pro
        self.assertEqual(selection.selected_tier, TIER_HIGH)
        self.assertTrue(selection.downgraded)

    # M: Mixed family – GPT-5.6 Sol Pro available, GPT-5.5 High checked
    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.click_ref")
    @patch("run_gpt56_sol_pro_consult.find_model_button")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_m_gpt56_pro_available_gpt55_high_checked(
        self, mock_opencli, mock_find_btn, mock_click, mock_get_state
    ):
        from run_gpt56_sol_pro_consult import ensure_best_available_model

        menu = """\
[10] <div role=menuitem>
  GPT-5.5
[15] <div role=menuitemradio aria-checked=true>High
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio data-testid=model-switcher-gpt-5-pro aria-checked=false>Pro"""

        menu_after_pro_click = """\
[10] <div role=menuitem>
  GPT-5.5
[15] <div role=menuitemradio aria-checked=false>High
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio data-testid=model-switcher-gpt-5-pro aria-checked=true>Pro"""

        mock_get_state.side_effect = [
            "initial-state",
            menu,
            "after-pro-click",
            menu_after_pro_click,
        ]
        mock_find_btn.return_value = "10"
        mock_opencli.return_value = ""

        selection = ensure_best_available_model(MOCK_SESSION)
        # Must select GPT-5.6 Sol Pro, never treat GPT-5.5 High as fallback
        self.assertEqual(selection.selected_tier, TIER_PRO)
        self.assertFalse(selection.downgraded)


# ---------------------------------------------------------------------------
# Mixed family A/B – GPT-5.5 checked + only Medium in GPT-5.6 → fail
# ---------------------------------------------------------------------------

class TestMixedFamilyFailures(unittest.TestCase):
    """GPT-5.5 Pro/High checked with only unsupported GPT-5.6 Sol tiers → fail."""

    def test_a_gpt55_pro_checked_gpt56_medium_only(self) -> None:
        state = """\
[10] <div role=menuitem>
  GPT-5.5
[12] <div role=menuitemradio aria-checked=true>GPT 5.5 Pro
[20] <div role=menuitem>
  GPT-5.6 Sol
[44] <div role=menuitemradio aria-checked=false>Medium"""
        candidates = discover_model_candidates(state)
        self.assertEqual(candidates, [])

    def test_b_gpt55_high_checked_gpt56_medium_only(self) -> None:
        state = """\
[10] <div role=menuitem>
  GPT-5.5
[15] <div role=menuitemradio aria-checked=true>High
[20] <div role=menuitem>
  GPT-5.6 Sol
[44] <div role=menuitemradio aria-checked=false>Medium"""
        candidates = discover_model_candidates(state)
        self.assertEqual(candidates, [])

    def test_c_gpt55_pro_checked_gpt56_high_available(self) -> None:
        state = """\
[10] <div role=menuitem>
  GPT-5.5
[12] <div role=menuitemradio aria-checked=true>GPT 5.5 Pro
[20] <div role=menuitem>
  GPT-5.6 Sol
[42] <div role=menuitemradio aria-checked=false>High"""
        result = resolve_model_from_state(state)
        self.assertEqual(result.selected_tier, TIER_HIGH)
        self.assertTrue(result.downgraded)

    def test_d_gpt55_high_checked_gpt56_pro_available(self) -> None:
        state = """\
[10] <div role=menuitem>
  GPT-5.5
[15] <div role=menuitemradio aria-checked=true>High
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio data-testid=model-switcher-gpt-5-pro aria-checked=false>Pro"""
        result = resolve_model_from_state(state)
        self.assertEqual(result.selected_tier, TIER_PRO)
        self.assertFalse(result.downgraded)


# ---------------------------------------------------------------------------
# Exact tier matching – no substring match for unsupported tiers
# ---------------------------------------------------------------------------

class TestExactTierMatching(unittest.TestCase):
    """Unsupported tier variants must be rejected by exact allowlist, not substring."""

    def test_ultra_high_rejected(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[43] <div role=menuitemradio aria-checked=true>Ultra High"""
        self.assertEqual(discover_model_candidates(state), [])

    def test_high_extended_rejected(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[43] <div role=menuitemradio aria-checked=true>High Extended"""
        self.assertEqual(discover_model_candidates(state), [])

    def test_high_plus_rejected(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[43] <div role=menuitemradio aria-checked=true>High Plus"""
        self.assertEqual(discover_model_candidates(state), [])

    def test_pro_max_rejected(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio aria-checked=true>Pro Max"""
        self.assertEqual(discover_model_candidates(state), [])

    def test_pro_plus_rejected(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio aria-checked=true>Pro Plus"""
        self.assertEqual(discover_model_candidates(state), [])

    def test_pro_extended_rejected(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio aria-checked=true>Pro Extended"""
        self.assertEqual(discover_model_candidates(state), [])

    def test_extra_high_rejected(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[43] <div role=menuitemradio aria-checked=true>Extra High"""
        self.assertEqual(discover_model_candidates(state), [])

    def test_exact_high_accepted(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[42] <div role=menuitemradio aria-checked=true>High"""
        candidates = discover_model_candidates(state)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].tier, TIER_HIGH)

    def test_exact_pro_accepted(self) -> None:
        state = """\
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio aria-checked=true>Pro"""
        candidates = discover_model_candidates(state)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].tier, TIER_PRO)


# ---------------------------------------------------------------------------
# Confirmation cross-family leakage
# ---------------------------------------------------------------------------

class TestConfirmationCrossFamily(unittest.TestCase):
    """Pro unchecked beside unrelated checked model → not confirmed."""

    def test_pro_unchecked_high_checked_other_family_not_confirmed(self) -> None:
        state = """\
[10] <div role=menuitem>
  GPT-5.5
[15] <div role=menuitemradio aria-checked=true>High
[20] <div role=menuitem>
  GPT-5.6 Sol
[41] <div role=menuitemradio data-testid=model-switcher-gpt-5-pro aria-checked=false>Pro"""
        selection = resolve_model_from_state(state)
        # Pro is the selected tier, but it's unchecked; the checked High is GPT-5.5
        self.assertFalse(selection_is_confirmed(state, selection))

    def test_high_unchecked_pro_checked_other_family_not_confirmed(self) -> None:
        state = """\
[10] <div role=menuitem>
  GPT-5.5
[12] <div role=menuitemradio aria-checked=true>Pro
[20] <div role=menuitem>
  GPT-5.6 Sol
[42] <div role=menuitemradio aria-checked=false>High"""
        selection = resolve_model_from_state(state)
        self.assertFalse(selection_is_confirmed(state, selection))


if __name__ == "__main__":
    unittest.main()
