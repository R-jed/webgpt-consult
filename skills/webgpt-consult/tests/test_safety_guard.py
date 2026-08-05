#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import safety_guard  # noqa: E402


class SafetyGuardTests(unittest.TestCase):
    def severities(self, text: str) -> set[tuple[str, str]]:
        return {(item["severity"], item["type"]) for item in safety_guard.scan(text)}

    def test_blocks_literal_openai_key(self) -> None:
        findings = self.severities("OPENAI_API_KEY=sk-proj-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456")
        self.assertIn(("block", "openai_key"), findings)

    def test_blocks_payment_card_number(self) -> None:
        findings = self.severities("card=4242 4242 4242 4242")
        self.assertIn(("block", "payment_card_number"), findings)

    def test_code_references_do_not_block(self) -> None:
        for text in (
            'api_key = os.getenv("OPENAI_API_KEY")',
            "password = get_secret()",
            "token = settings.token",
            "client_secret = config.client_secret",
            "password = None",
            "token: null",
        ):
            with self.subTest(text=text):
                self.assertFalse(any(item["severity"] == "block" for item in safety_guard.scan(text)))

    def test_email_is_warning_only(self) -> None:
        findings = safety_guard.scan("Contact alice@example.com about the review.")
        self.assertIn(("warn", "email"), {(item["severity"], item["type"]) for item in findings})
        self.assertFalse(any(item["severity"] == "block" for item in findings))


if __name__ == "__main__":
    unittest.main()
