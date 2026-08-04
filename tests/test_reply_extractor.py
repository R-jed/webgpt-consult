#!/usr/bin/env python3

"""Regression tests for extract_chatgpt_reply.py – fenced code awareness."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from extract_chatgpt_reply import split_latest_assistant, _is_outside_fences


class TestFencedCodeAwareness(unittest.TestCase):
    """Assistant markers inside fenced code blocks must be ignored."""

    def test_marker_inside_fenced_code_ignored(self) -> None:
        content = (
            "#### ChatGPT said:\n"
            "Real answer starts here.\n\n"
            "```markdown\n"
            "#### ChatGPT:\n"
            "This is an example\n"
            "```\n\n"
            "Conclusion"
        )
        result = split_latest_assistant(content)
        self.assertIn("Real answer starts here", result)
        self.assertIn("Conclusion", result)

    def test_marker_inside_triple_backtick_ignored(self) -> None:
        content = (
            "#### ChatGPT said:\n"
            "First real answer.\n\n"
            "```\n"
            "#### ChatGPT:\n"
            "fake\n"
            "```\n\n"
            "Second part."
        )
        result = split_latest_assistant(content)
        self.assertIn("First real answer", result)
        self.assertIn("Second part", result)

    def test_multiple_real_turns_extracts_latest(self) -> None:
        content = (
            "#### ChatGPT said:\n"
            "First turn answer.\n\n"
            "#### You said:\n"
            "follow up\n\n"
            "#### ChatGPT said:\n"
            "Second turn answer.\n"
            "More detail."
        )
        result = split_latest_assistant(content)
        self.assertIn("Second turn answer", result)
        self.assertNotIn("First turn answer", result)

    def test_sentinel_retained_in_full_response(self) -> None:
        content = (
            "#### ChatGPT said:\n"
            "WEBGPT_CONSULT_RESULT_20260726_TEST\n"
            "Analysis follows...\n"
            "Detailed response."
        )
        result = split_latest_assistant(content)
        self.assertIn("WEBGPT_CONSULT_RESULT_20260726_TEST", result)
        self.assertIn("Analysis follows", result)

    def test_plain_marker_not_in_fence(self) -> None:
        content = (
            "#### ChatGPT said:\n"
            "Direct answer."
        )
        result = split_latest_assistant(content)
        self.assertEqual(result, "Direct answer.")

    def test_marker_inside_fence_only_no_real_marker(self) -> None:
        content = (
            "Some preamble\n\n"
            "```python\n"
            "#### ChatGPT:\n"
            "example()\n"
            "```"
        )
        with self.assertRaises(ValueError) as ctx:
            split_latest_assistant(content)
        self.assertIn("No assistant marker", str(ctx.exception))


class TestIsOutsideFences(unittest.TestCase):
    """_is_outside_fences correctly identifies position context."""

    def test_outside_single_fence(self) -> None:
        content = "line1\n```\ncode\n```\nline3"
        self.assertTrue(_is_outside_fences(content, 0))   # "line1"
        self.assertTrue(_is_outside_fences(content, 19))  # "line3"

    def test_inside_single_fence(self) -> None:
        content = "line1\n```\ncode\n```\nline3"
        self.assertFalse(_is_outside_fences(content, 10))  # "code"

    def test_outside_double_fence(self) -> None:
        content = "a\n```\nx\n```\nb\n```\ny\n```\nc"
        self.assertTrue(_is_outside_fences(content, 0))   # "a"
        self.assertTrue(_is_outside_fences(content, 12))  # "b"
        self.assertTrue(_is_outside_fences(content, 24))  # "c"

    def test_inside_double_fence(self) -> None:
        content = "a\n```\nx\n```\nb\n```\ny\n```\nc"
        self.assertFalse(_is_outside_fences(content, 6))   # "x"
        self.assertFalse(_is_outside_fences(content, 18))  # "y"

    # --- Tilde fences ---

    def test_tilde_fence_opened(self) -> None:
        content = "before\n~~~\ncode\n~~~\nafter"
        self.assertTrue(_is_outside_fences(content, 0))
        self.assertFalse(_is_outside_fences(content, 10))  # "code"
        self.assertTrue(_is_outside_fences(content, 20))   # "after"

    def test_tilde_fence_with_info_string(self) -> None:
        content = "before\n~~~python\ncode\n~~~\nafter"
        self.assertFalse(_is_outside_fences(content, 14))  # "code"

    # --- Leading spaces ---

    def test_three_space_backtick_fence(self) -> None:
        content = "before\n   ```\ncode\n   ```\nafter"
        self.assertFalse(_is_outside_fences(content, 12))  # "code"
        self.assertTrue(_is_outside_fences(content, 22))   # "after"

    def test_three_space_tilde_fence(self) -> None:
        content = "before\n   ~~~\ncode\n   ~~~\nafter"
        self.assertFalse(_is_outside_fences(content, 12))  # "code"

    def test_four_space_not_fence(self) -> None:
        """Four leading spaces = code block, not fenced delimiter."""
        content = "before\n    ```\ncode\n    ```\nafter"
        # Four-space indent means ``` is NOT a fence delimiter (CommonMark rule).
        result = _is_outside_fences(content, 13)
        self.assertTrue(result)  # "code" is outside any fence

    # --- Longer closing fence ---

    def test_longer_closes_shorter(self) -> None:
        content = "a\n```\ncode\n````\nb"
        self.assertFalse(_is_outside_fences(content, 6))   # "code"
        self.assertTrue(_is_outside_fences(content, 16))   # "b"

    # --- Shorter closing fence does NOT close ---

    def test_shorter_does_not_close(self) -> None:
        content = "a\n````\ncode\n```\nmore\n````\nb"
        # Opening ````, then ``` cannot close, more code, ```` closes
        self.assertFalse(_is_outside_fences(content, 8))   # "code"
        self.assertFalse(_is_outside_fences(content, 18))  # "more"
        self.assertFalse(_is_outside_fences(content, 26))  # "b" inside unclosed ````

    # --- Mismatched fence character ---

    def test_tilde_not_closed_by_backtick(self) -> None:
        content = "a\n~~~\ncode\n```\nmore\n~~~\nb"
        self.assertFalse(_is_outside_fences(content, 6))   # "code"
        self.assertFalse(_is_outside_fences(content, 14))  # "more"
        self.assertFalse(_is_outside_fences(content, 24))  # "b" inside unclosed ~~~

    def test_backtick_not_closed_by_tilde(self) -> None:
        content = "a\n```\ncode\n~~~\nmore\n```\nb"
        self.assertFalse(_is_outside_fences(content, 6))   # "code"
        self.assertFalse(_is_outside_fences(content, 14))  # "more"
        self.assertFalse(_is_outside_fences(content, 24))  # "b" inside unclosed ```


class TestTildeFenceExtraction(unittest.TestCase):
    """tilde fences properly suppress fake markers."""

    def test_tilde_fence_marker_ignored(self) -> None:
        content = (
            "#### ChatGPT:\n"
            "Real answer starts.\n\n"
            "~~~markdown\n"
            "#### ChatGPT:\n"
            "fake assistant marker\n"
            "~~~\n\n"
            "Real answer continues."
        )
        result = split_latest_assistant(content)
        self.assertIn("Real answer starts", result)
        self.assertIn("Real answer continues", result)

    def test_indented_backtick_fence_marker_ignored(self) -> None:
        content = (
            "#### ChatGPT:\n"
            "Real answer.\n\n"
            "   ```markdown\n"
            "   #### ChatGPT:\n"
            "   fake marker\n"
            "   ```\n\n"
            "Conclusion."
        )
        result = split_latest_assistant(content)
        self.assertIn("Real answer", result)
        self.assertIn("Conclusion", result)

    def test_indented_tilde_fence_marker_ignored(self) -> None:
        content = (
            "#### ChatGPT said:\n"
            "Real answer.\n\n"
            "  ~~~text\n"
            "  #### ChatGPT said:\n"
            "  fake marker\n"
            "  ~~~\n\n"
            "Conclusion."
        )
        result = split_latest_assistant(content)
        self.assertIn("Real answer", result)
        self.assertIn("Conclusion", result)

    def test_longer_closes_shorter_fence(self) -> None:
        content = (
            "#### ChatGPT:\n"
            "first\n\n"
            "```\n"
            "#### ChatGPT:\n"
            "fake\n"
            "````\n\n"
            "second"
        )
        result = split_latest_assistant(content)
        self.assertIn("first", result)
        self.assertIn("second", result)

    def test_shorter_does_not_close_longer(self) -> None:
        content = (
            "#### ChatGPT:\n"
            "first\n\n"
            "````\n"
            "#### ChatGPT:\n"
            "fake\n"
            "```\n"
            "more fake\n"
            "````\n\n"
            "second"
        )
        result = split_latest_assistant(content)
        self.assertIn("first", result)
        self.assertIn("second", result)

    def test_mismatched_fence_not_closed(self) -> None:
        content = (
            "#### ChatGPT:\n"
            "first\n\n"
            "~~~\n"
            "#### ChatGPT:\n"
            "fake\n"
            "```\n"
            "~~~\n\n"
            "second"
        )
        result = split_latest_assistant(content)
        self.assertIn("first", result)
        self.assertIn("second", result)

    def test_marker_after_valid_closing_fence(self) -> None:
        content = (
            "#### ChatGPT:\n"
            "first\n\n"
            "~~~\n"
            "#### ChatGPT:\n"
            "fake\n"
            "~~~\n\n"
            "#### ChatGPT:\n"
            "second"
        )
        result = split_latest_assistant(content)
        # Latest real marker is the one after the fence
        self.assertIn("second", result)
        self.assertNotIn("first", result)


if __name__ == "__main__":
    unittest.main()
