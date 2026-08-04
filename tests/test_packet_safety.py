#!/usr/bin/env python3

"""Regression tests for check_packet_safety.py – credential detection + redaction."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from check_packet_safety import scan


SECRET_VALUE = "abcdefghijklmnopqrstuvwxyz123456"


class TestCredentialDetection(unittest.TestCase):
    """All common credential assignments must be detected."""

    def _assert_detected(self, text: str, expected_type: str) -> None:
        result = scan(text)
        high_findings = [f for f in result["findings"] if f["severity"] == "high"]
        types = [f["type"] for f in high_findings]
        self.assertIn(expected_type, types, f"Expected {expected_type} in {types}")
        # Critical: secret value must never appear in any excerpt
        for f in result["findings"]:
            self.assertNotIn(SECRET_VALUE, f.get("excerpt", ""), "Secret leaked in excerpt")

    def test_token_detected(self) -> None:
        self._assert_detected(f"token={SECRET_VALUE}", "credential_assignment")

    def test_api_key_detected(self) -> None:
        self._assert_detected(f"api_key={SECRET_VALUE}", "credential_assignment")

    def test_access_token_detected(self) -> None:
        self._assert_detected(f"access_token={SECRET_VALUE}", "credential_assignment")

    def test_refresh_token_detected(self) -> None:
        self._assert_detected(f"refresh_token={SECRET_VALUE}", "credential_assignment")

    def test_client_secret_detected(self) -> None:
        self._assert_detected(f"client_secret={SECRET_VALUE}", "credential_assignment")

    def test_session_token_detected(self) -> None:
        self._assert_detected(f"session_token={SECRET_VALUE}", "credential_assignment")

    def test_auth_token_detected(self) -> None:
        self._assert_detected(f"auth_token={SECRET_VALUE}", "credential_assignment")

    def test_password_detected(self) -> None:
        self._assert_detected(f"password={SECRET_VALUE}", "credential_assignment")

    def test_passwd_detected(self) -> None:
        self._assert_detected(f"passwd={SECRET_VALUE}", "credential_assignment")

    def test_pwd_detected(self) -> None:
        self._assert_detected(f"pwd={SECRET_VALUE}", "credential_assignment")

    def test_secret_detected(self) -> None:
        self._assert_detected(f"secret={SECRET_VALUE}", "credential_assignment")

    def test_bearer_token_detected(self) -> None:
        self._assert_detected(f"bearer_token={SECRET_VALUE}", "credential_assignment")


class TestCredentialRedaction(unittest.TestCase):
    """Credential values must never appear in scanner output."""

    def test_no_raw_secret_in_findings(self) -> None:
        token = "sk-abc123def456ghi789jkl012"
        result = scan(f"token={token}")
        for finding in result["findings"]:
            self.assertNotIn(token, finding.get("excerpt", ""))
            self.assertNotIn(token, json.dumps(finding))

    def test_no_raw_password_in_findings(self) -> None:
        pw = "SuperSecret12345678"
        result = scan(f"password={pw}")
        for finding in result["findings"]:
            self.assertNotIn(pw, finding.get("excerpt", ""))

    def test_redacted_key_preserved(self) -> None:
        result = scan(f"api_key={SECRET_VALUE}")
        high = [f for f in result["findings"] if f["severity"] == "high"]
        self.assertTrue(any("api_key" in f["excerpt"] for f in high))
        self.assertTrue(any("REDACTED" in f["excerpt"] for f in high))

    def test_aws_key_not_in_excerpt(self) -> None:
        key = "AKIA" + "A" * 16
        result = scan(f"key_id={key}")
        for finding in result["findings"]:
            self.assertNotIn(key, finding.get("excerpt", ""))


class TestHighRiskPatterns(unittest.TestCase):
    """Direct high-risk pattern detection (non-assignment)."""

    def test_private_key_detected(self) -> None:
        text = "-----BEGIN RSA PRIVATE KEY-----"
        result = scan(text)
        self.assertTrue(result["high_count"] > 0)

    def test_aws_access_key_detected(self) -> None:
        result = scan("AKIAIOSFODNN7EXAMPLE")
        self.assertTrue(result["high_count"] > 0)

    def test_github_token_detected(self) -> None:
        result = scan("ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef")
        self.assertTrue(result["high_count"] > 0)

    def test_openai_key_detected(self) -> None:
        result = scan("sk-proj1234567890abcdefghijklmnop")
        self.assertTrue(result["high_count"] > 0)

    def test_jwt_detected(self) -> None:
        result = scan("eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U")
        self.assertTrue(result["high_count"] > 0)

    def test_no_false_positive_on_normal_text(self) -> None:
        text = "This is a normal project context with business details."
        result = scan(text)
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
