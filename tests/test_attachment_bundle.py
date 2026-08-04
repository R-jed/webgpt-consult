#!/usr/bin/env python3

"""Regression tests for build_attachment_bundle.py – symlink escape and output exclusion."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from build_attachment_bundle import iter_files


class TestSymlinkEscape(unittest.TestCase):
    """Symlinks pointing outside the root must never be included."""

    def test_symlink_outside_root_excluded(self) -> None:
        """symlink pointing to /tmp/outside-secret.txt must not appear in bundle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            root.mkdir()
            (root / "a.txt").write_text("safe content", encoding="utf-8")

            outside = Path(tmpdir) / "outside-secret.txt"
            outside.write_text("SECRET_STUFF", encoding="utf-8")

            # Create symlink inside root pointing outside
            link = root / "link.txt"
            link.symlink_to(outside)

            files = iter_files([root])
            contents = [f.read_text(encoding="utf-8") for f in files]
            self.assertNotIn("SECRET_STUFF", contents)

    def test_symlink_inside_root_excluded(self) -> None:
        """Even symlinks within root are skipped (defense in depth)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            root.mkdir()
            (root / "real.txt").write_text("real", encoding="utf-8")
            (root / "link.txt").symlink_to(root / "real.txt")

            files = iter_files([root])
            # Only real.txt should be included, not link.txt
            labels = [f.name for f in files]
            self.assertIn("real.txt", labels)
            self.assertNotIn("link.txt", labels)

    def test_ordinary_internal_file_included(self) -> None:
        """Normal files inside root are included."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            root.mkdir()
            (root / "a.py").write_text("print('hi')", encoding="utf-8")
            (root / "b.md").write_text("# Hello", encoding="utf-8")

            files = iter_files([root])
            labels = [f.name for f in files]
            self.assertIn("a.py", labels)
            self.assertIn("b.md", labels)


class TestOutputSelfExclusion(unittest.TestCase):
    """The output bundle file must not be recursively included in its own input."""

    def test_output_bundle_excluded_from_own_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            root.mkdir()
            (root / "a.txt").write_text("content", encoding="utf-8")
            output = root / "review-bundle.md"
            output.write_text("# Bundle", encoding="utf-8")

            files = iter_files([root], exclude_output=output)
            self.assertNotIn(output.resolve(), [f.resolve() for f in files])

    def test_output_outside_root_still_excluded(self) -> None:
        """Output file outside root is also excluded (by resolve comparison)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            root.mkdir()
            (root / "a.txt").write_text("content", encoding="utf-8")
            output = Path(tmpdir) / "other" / "bundle.md"

            files = iter_files([root], exclude_output=output)
            self.assertEqual(len(files), 1)

    def test_excluded_output_not_in_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            root.mkdir()
            (root / "code.py").write_text("x=1", encoding="utf-8")
            bundle = root / "bundle.md"
            bundle.write_text("# Review", encoding="utf-8")

            files = iter_files([root], exclude_output=bundle)
            labels = [f.name for f in files]
            self.assertIn("code.py", labels)
            self.assertNotIn("bundle.md", labels)


class TestBundleBlocking(unittest.TestCase):
    """Credential bundles must fail closed: exit non-zero, no output file."""

    def test_credential_bundle_exits_nonzero(self) -> None:
        """Bundle with secret content must exit non-zero."""
        import subprocess
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            root.mkdir()
            (root / "secret.txt").write_text(
                "access_token=VERY_SECRET_VALUE_123456", encoding="utf-8"
            )
            output = Path(tmpdir) / "bundle.md"
            result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "build_attachment_bundle.py"),
                 str(root), "-o", str(output)],
                text=True, capture_output=True, timeout=30,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_credential_bundle_no_output_file(self) -> None:
        """When blocked, the final output file must not exist."""
        import subprocess
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            root.mkdir()
            (root / "secret.txt").write_text(
                "access_token=VERY_SECRET_VALUE_123456", encoding="utf-8"
            )
            output = Path(tmpdir) / "bundle.md"
            subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "build_attachment_bundle.py"),
                 str(root), "-o", str(output)],
                text=True, capture_output=True, timeout=30,
            )
            self.assertFalse(output.exists())

    def test_credential_bundle_no_raw_secret_in_stderr(self) -> None:
        """Error output must not contain the raw secret value."""
        import subprocess
        secret = "VERY_SECRET_VALUE_123456"
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            root.mkdir()
            (root / "secret.txt").write_text(
                f"access_token={secret}", encoding="utf-8"
            )
            output = Path(tmpdir) / "bundle.md"
            result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "build_attachment_bundle.py"),
                 str(root), "-o", str(output)],
                text=True, capture_output=True, timeout=30,
            )
            self.assertNotIn(secret, result.stderr)
            self.assertNotIn(secret, result.stdout)

    def test_clean_bundle_exits_zero(self) -> None:
        """Clean bundle without credentials must succeed."""
        import subprocess
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            root.mkdir()
            (root / "safe.py").write_text("print('hello')", encoding="utf-8")
            output = Path(tmpdir) / "bundle.md"
            result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "build_attachment_bundle.py"),
                 str(root), "-o", str(output)],
                text=True, capture_output=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
