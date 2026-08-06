#!/usr/bin/env python3

from __future__ import annotations

import codecs
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import build_attachment_bundle as bundle  # noqa: E402


class AttachmentBundleTests(unittest.TestCase):
    def _embedded_text(self, bundle_text: str, language: str) -> str:
        opening = f"````{language}\n"
        start = bundle_text.index(opening) + len(opening)
        end = bundle_text.index("````\n", start)
        return bundle_text[start:end]

    def test_complete_bundle_has_one_content_hash_and_relative_labels(self) -> None:
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
            first_hash = hashlib.sha256(first.read_bytes()).hexdigest()

            self.assertTrue(result["ok"])
            self.assertEqual(result["files"], 2)
            self.assertIn("`project/a.py`", text)
            self.assertIn("`project/notes.md`", text)
            self.assertIn("encoding=utf-8", text)
            self.assertIn(f"sha256={first_hash}", text)
            self.assertNotIn("source_sha256=", text)
            self.assertNotIn("included_sha256=", text)
            self.assertIn("status=full", text)
            self.assertNotIn(str(root.resolve()), text)

    def test_preserves_trailing_whitespace_and_hashes_embedded_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "exact.txt"
            original = "value with spaces  \n\n"
            source.write_text(original, encoding="utf-8")
            output = Path(tmp) / "bundle.md"

            bundle.build_bundle([source], output)
            text = output.read_text(encoding="utf-8")
            embedded = self._embedded_text(text, "txt")
            digest = hashlib.sha256(original.encode("utf-8")).hexdigest()

            self.assertEqual(embedded, original)
            self.assertIn(f"source_bytes={len(original.encode('utf-8'))}", text)
            self.assertIn(f"included_bytes={len(original.encode('utf-8'))}", text)
            self.assertIn(f"sha256={digest}", text)

    def test_oversized_file_fails_closed_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "large.txt"
            source.write_text("x" * 100, encoding="utf-8")
            output = Path(tmp) / "bundle.md"

            with self.assertRaises(bundle.BundleError):
                bundle.build_bundle([source], output, max_file_bytes=20)
            self.assertFalse(output.exists())

    def test_partial_bundle_hashes_only_the_included_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "large.txt"
            source.write_text("x" * 100, encoding="utf-8")
            output = Path(tmp) / "bundle.md"

            result = bundle.build_bundle([source], output, max_file_bytes=20, allow_partial=True)
            text = output.read_text(encoding="utf-8")
            included = "x" * 20
            digest = hashlib.sha256(included.encode("utf-8")).hexdigest()

            self.assertEqual(result["partial_files"], 1)
            self.assertIn("status=truncated", text)
            self.assertIn("source_bytes=100", text)
            self.assertIn("included_bytes=20", text)
            self.assertIn(f"sha256={digest}", text)
            self.assertIn("PARTIAL FILE", text)
            self.assertNotIn("source_sha256=", text)
            self.assertNotIn("included_sha256=", text)

    def test_utf8_bom_is_decoded_strictly_and_not_embedded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "bom.txt"
            original = "hello 世界\n"
            source.write_bytes(codecs.BOM_UTF8 + original.encode("utf-8"))
            output = Path(tmp) / "bundle.md"

            bundle.build_bundle([source], output)
            text = output.read_text(encoding="utf-8")
            embedded = self._embedded_text(text, "txt")
            digest = hashlib.sha256(original.encode("utf-8")).hexdigest()

            self.assertEqual(embedded, original)
            self.assertNotIn("\ufeff", embedded)
            self.assertIn("encoding=utf-8-bom", text)
            self.assertIn(f"sha256={digest}", text)

    def test_bom_declared_utf16_is_transcoded_to_utf8_without_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "utf16.txt"
            original = "hello 世界\r\n"
            raw = original.encode("utf-16")
            source.write_bytes(raw)
            output = Path(tmp) / "bundle.md"

            bundle.build_bundle([source], output)
            text = output.read_text(encoding="utf-8")
            embedded = self._embedded_text(text, "txt")
            included_raw = original.encode("utf-8")

            self.assertEqual(embedded, original)
            self.assertIn("encoding=utf-16", text)
            self.assertIn(f"source_bytes={len(raw)}", text)
            self.assertIn(f"included_bytes={len(included_raw)}", text)
            self.assertIn(f"sha256={hashlib.sha256(included_raw).hexdigest()}", text)

    def test_bom_declared_utf32_is_transcoded_to_utf8_without_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "utf32.txt"
            original = "plain text\n"
            raw = original.encode("utf-32")
            source.write_bytes(raw)
            output = Path(tmp) / "bundle.md"

            bundle.build_bundle([source], output)
            text = output.read_text(encoding="utf-8")
            embedded = self._embedded_text(text, "txt")

            self.assertEqual(embedded, original)
            self.assertIn("encoding=utf-32", text)
            self.assertIn(f"sha256={hashlib.sha256(original.encode('utf-8')).hexdigest()}", text)

    def test_invalid_non_bom_encoding_still_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "broken.txt"
            source.write_bytes(b"hello\xffworld")
            output = Path(tmp) / "bundle.md"

            with self.assertRaises(bundle.BundleError):
                bundle.build_bundle([source], output)
            self.assertFalse(output.exists())

    def test_nul_bytes_without_unicode_bom_are_rejected_as_binary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "binary.txt"
            source.write_bytes(b"hello\x00world")
            output = Path(tmp) / "bundle.md"

            with self.assertRaises(bundle.BundleError):
                bundle.build_bundle([source], output)
            self.assertFalse(output.exists())

    def test_secret_blocks_bundle_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "secret.txt"
            source.write_text("OPENAI_API_KEY=sk-proj-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456\n", encoding="utf-8")
            output = Path(tmp) / "bundle.md"

            with self.assertRaises(bundle.BundleError):
                bundle.build_bundle([source], output)
            self.assertFalse(output.exists())

    def test_markdown_with_four_backticks_gets_longer_outer_fence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "nested.md"
            source.write_text("# Example\n````python\nprint('nested')\n````\n", encoding="utf-8")
            output = Path(tmp) / "bundle.md"

            bundle.build_bundle([source], output)
            text = output.read_text(encoding="utf-8")

            self.assertIn("`````markdown", text)
            self.assertIn("````python", text)
            self.assertIn("print('nested')", text)


if __name__ == "__main__":
    unittest.main()
