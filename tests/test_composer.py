#!/usr/bin/env python3

"""Regression tests for fill_composer() fail-closed behavior."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

COMPOSER_STATE = '[10] <div id=prompt-textarea contenteditable=true role=textbox>'


class TestFillComposer(unittest.TestCase):
    """Verify fill_composer fails closed: fresh DOM truth always required."""

    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_malformed_fill_no_marker_raises(self, mock_opencli, mock_get_state):
        """OpenCLI returns malformed JSON + sentinel absent from fresh DOM → fail."""
        from run_gpt56_sol_pro_consult import fill_composer, ConsultError

        mock_opencli.return_value = "NOT_JSON_RESPONSE"
        mock_get_state.return_value = COMPOSER_STATE

        with self.assertRaises(ConsultError) as ctx:
            fill_composer("session", COMPOSER_STATE, "packet", "GPT56_SOL_PRO_RESULT_X")
        self.assertIn("sentinel not visible", str(ctx.exception).lower())

    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_claimed_success_no_marker_raises(self, mock_opencli, mock_get_state):
        """OpenCLI claims filled=true but sentinel absent from fresh DOM → fail."""
        from run_gpt56_sol_pro_consult import fill_composer, ConsultError

        mock_opencli.return_value = json.dumps({"filled": True, "verified": True})
        mock_get_state.return_value = COMPOSER_STATE

        with self.assertRaises(ConsultError) as ctx:
            fill_composer("session", COMPOSER_STATE, "packet", "GPT56_SOL_PRO_RESULT_Y")
        self.assertIn("sentinel not visible", str(ctx.exception).lower())

    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_dom_marker_present_continues(self, mock_opencli, mock_get_state):
        """Fresh DOM contains sentinel → continue, regardless of JSON response."""
        from run_gpt56_sol_pro_consult import fill_composer

        mock_opencli.return_value = "{}"  # even empty JSON is fine
        state_with_sentinel = f'{COMPOSER_STATE}\nGPT56_SOL_PRO_RESULT_Z'
        mock_get_state.return_value = state_with_sentinel

        result = fill_composer("session", COMPOSER_STATE, "packet", "GPT56_SOL_PRO_RESULT_Z")
        self.assertIn("GPT56_SOL_PRO_RESULT_Z", result)

    @patch("run_gpt56_sol_pro_consult.get_state")
    @patch("run_gpt56_sol_pro_consult.run_opencli")
    def test_fill_fails_raises(self, mock_opencli, mock_get_state):
        """OpenCLI returns filled=false → immediate failure."""
        from run_gpt56_sol_pro_consult import fill_composer, ConsultError

        mock_opencli.return_value = json.dumps({"filled": False, "error": "ref not found"})
        mock_get_state.return_value = COMPOSER_STATE

        with self.assertRaises(ConsultError) as ctx:
            fill_composer("session", COMPOSER_STATE, "packet", "GPT56_SOL_PRO_RESULT_A")
        self.assertIn("fill failed", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
