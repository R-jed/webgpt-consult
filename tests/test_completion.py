#!/usr/bin/env python3

"""Regression tests for wait_for_reply() – sentinel vs generating ordering."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


class TestWaitForReply(unittest.TestCase):
    """Verify sentinel presence != completion; page must stop generating first."""

    @patch("run_gpt56_sol_pro_consult.time")
    @patch("run_gpt56_sol_pro_consult.extract_current")
    @patch("run_gpt56_sol_pro_consult.get_state")
    def test_sentinel_while_generating_not_returned(
        self, mock_get_state, mock_extract, mock_time
    ):
        """Sentinel appears in partial response while stop-button is visible.

        wait_for_reply must NOT return the partial response.
        """
        from run_gpt56_sol_pro_consult import wait_for_reply, ConsultError

        generating_state = '[99] <button data-testid=stop-button aria-label="Stop generating">'
        stopped_state = '[99] <button data-testid=send-button>'

        # time.time() calls: deadline(0), while-1(1), while-2(2)
        mock_time.time.side_effect = [0, 1, 2, 1000]
        mock_time.sleep.return_value = None

        partial_reply = json.dumps({
            "content": "#### ChatGPT said:\nGPT56_SOL_PRO_RESULT_TEST\npartial..."
        })
        complete_reply = json.dumps({
            "content": "#### ChatGPT said:\nGPT56_SOL_PRO_RESULT_TEST\ncomplete answer"
        })

        # Poll 1: generating → extract NOT called, continues
        # Poll 2: stopped → extract called → returns complete reply
        mock_get_state.side_effect = [generating_state, stopped_state]
        mock_extract.return_value = complete_reply

        result = wait_for_reply("session", "GPT56_SOL_PRO_RESULT_TEST", 300, 0)

        # Must return the complete response, not the partial one
        self.assertIn("complete answer", result)
        # extract_current should have been called once (only after generation stopped)
        self.assertEqual(mock_extract.call_count, 1)

    @patch("run_gpt56_sol_pro_consult.time")
    @patch("run_gpt56_sol_pro_consult.extract_current")
    @patch("run_gpt56_sol_pro_consult.get_state")
    def test_sentinel_after_stop_returns(
        self, mock_get_state, mock_extract, mock_time
    ):
        """Sentinel present after generation stopped → return."""
        from run_gpt56_sol_pro_consult import wait_for_reply

        stopped_state = '[99] <button data-testid=send-button>'
        mock_time.time.side_effect = [0, 1, 1000]
        mock_time.sleep.return_value = None

        reply = json.dumps({
            "content": "#### ChatGPT said:\nGPT56_SOL_PRO_RESULT_OK\ndone"
        })
        mock_get_state.return_value = stopped_state
        mock_extract.return_value = reply

        result = wait_for_reply("session", "GPT56_SOL_PRO_RESULT_OK", 300, 0)
        self.assertIn("GPT56_SOL_PRO_RESULT_OK", result)

    @patch("run_gpt56_sol_pro_consult.time")
    @patch("run_gpt56_sol_pro_consult.extract_current")
    @patch("run_gpt56_sol_pro_consult.get_state")
    def test_no_sentinel_after_stop_raises(
        self, mock_get_state, mock_extract, mock_time
    ):
        """Generation stopped but no sentinel → timeout error."""
        from run_gpt56_sol_pro_consult import wait_for_reply, ConsultError

        stopped_state = '[99] <button data-testid=send-button>'
        mock_time.time.side_effect = [0, 1, 1000]
        mock_time.sleep.return_value = None

        reply = json.dumps({
            "content": "#### ChatGPT said:\nNo sentinel here"
        })
        mock_get_state.return_value = stopped_state
        mock_extract.return_value = reply

        with self.assertRaises(ConsultError) as ctx:
            wait_for_reply("session", "GPT56_SOL_PRO_RESULT_MISSING", 300, 0)
        self.assertIn("Sentinel not found", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
