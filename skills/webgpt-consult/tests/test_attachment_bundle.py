#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import build_attachment_bundle as bundle  # noqa: E402


class AttachmentBundleTests(unittest.TestCase):
    def test_complete_bundle_has_manifest_hashes_and_relative_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            first = root / "a.py"
            second = root / "notes.md"
            first.write_text("print('hello')\n", encoding="utf-8")
            second.write_text("# Notes\nimportant context\n", encoding="utf-8")
            output = Path(tmp) / "bundle.md"

            result = bundle.build_bundle([root], output)
            text = output.read_text(encoding="utf-8")

            self.assertTrue(result["ok"])
            self.assertEqual(result["files"], 2)
            self.assertIn("`project/a.py`", text)
            self.assertIn("`project/notes.md`", text)
            self.assertIn(hashlib.sha256(first.read_bytes()).hexdigest(), text)
            self.assertIn("status=full", text)
            self.assertNotIn(str(root.resolve()), text)

    def test_oversized_file_fails_closed_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "large.txt"
            source.write_text("x" * 100, encoding="utf-8")
            output = Path(tmp) / "bundle.md"

            with self.assertRaises(bundle.BundleError):
                bundle.build_bundle([source], output, max_file_bytes=20)
            self.assertFalse(output.exists())

    def test_partial_bundle_requires_explicit_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "large.txt"
            source.write_text("x" * 100, encoding="utf-8")
            output = Path(tmp) / "bundle.md"

            result = bundle.build_bundle([source], output, max_file_bytes=20, allow_partial=True)
            text = output.read_text(encoding="utf-8")

            self.assertEqual(result["partial_files"], 1)
            self.assertIn("status=truncated", text)
            self.assertIn("PARTIAL FILE", text)

    def test_secret_blocks_bundle_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "secret.txt"
            source.write_text("OPENAI_API_KEY=sk-proj-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456\n", encoding="utf-8")
            output = Path(tmp) / "bundle.md"

            with self.assertRaises(bundle.BundleError):
                bundle.build_bundle([source], output)
            self.assertFalse(output.exists())

    def test_invalid_utf8_in_supported_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "broken.txt"
            source.write_bytes(b"hello\xffworld")
            output = Path(tmp) / "bundle.md"

            with self.assertRaises(bundle.BundleError):
                bundle.build_bundle([source], output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
