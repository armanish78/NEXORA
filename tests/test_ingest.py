"""
tests/test_ingest.py
====================
Phase 2 — Unit and integration tests for the ingestion module.

Tests are structured by function being tested.
Each test creates a temporary directory so the real
data/ and model/ directories are never touched.

Run with:
    .venv/bin/python -m pytest tests/test_ingest.py -v
"""

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Ensure project root is on the path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# Helpers
# ============================================================

def make_temp_dirs():
    """Create a temporary directory structure that mirrors the project layout."""
    tmp = tempfile.mkdtemp()
    raw_dir = os.path.join(tmp, "data", "raw")
    processed_dir = os.path.join(tmp, "data", "processed")
    cache_dir = os.path.join(tmp, "model", "cache")
    os.makedirs(raw_dir)
    os.makedirs(processed_dir)
    os.makedirs(cache_dir)
    return tmp, raw_dir, processed_dir, cache_dir


def write_text_file(path: str, content: str = "hello world"):
    """Write a simple text file for hashing tests."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================
# Tests: compute_file_hash
# ============================================================

class TestComputeFileHash:

    def test_hash_is_hex_string(self, tmp_path):
        """hash must be a 64-character lowercase hex string."""
        from app.ingest import compute_file_hash
        p = tmp_path / "test.txt"
        p.write_text("hello")
        result = compute_file_hash(str(p))
        assert isinstance(result, str)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_same_content_same_hash(self, tmp_path):
        """Two files with identical content must produce the same hash."""
        from app.ingest import compute_file_hash
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("identical content")
        b.write_text("identical content")
        assert compute_file_hash(str(a)) == compute_file_hash(str(b))

    def test_different_content_different_hash(self, tmp_path):
        """Files with different content must produce different hashes."""
        from app.ingest import compute_file_hash
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("content A")
        b.write_text("content B")
        assert compute_file_hash(str(a)) != compute_file_hash(str(b))

    def test_hash_matches_sha256(self, tmp_path):
        """Verify the hash matches a manually computed SHA-256."""
        from app.ingest import compute_file_hash
        content = b"test content"
        expected = hashlib.sha256(content).hexdigest()
        p = tmp_path / "test.bin"
        p.write_bytes(content)
        assert compute_file_hash(str(p)) == expected


# ============================================================
# Tests: is_already_processed / mark_as_processed
# ============================================================

class TestHashCache:

    def test_not_processed_initially(self, tmp_path):
        """A new hash must not be marked as processed."""
        from app.ingest import is_already_processed
        with patch("app.ingest.CACHE_DIR", str(tmp_path)):
            assert not is_already_processed("nonexistent_hash")

    def test_marked_after_processing(self, tmp_path):
        """After marking, the hash must be detected as processed."""
        from app.ingest import is_already_processed, mark_as_processed
        with patch("app.ingest.CACHE_DIR", str(tmp_path)):
            mark_as_processed("abc123", "/some/file.pdf")
            assert is_already_processed("abc123")

    def test_marker_contains_original_path(self, tmp_path):
        """The cache marker file must record the original path."""
        from app.ingest import mark_as_processed
        with patch("app.ingest.CACHE_DIR", str(tmp_path)):
            mark_as_processed("abc123", "/some/file.pdf")
            marker = (tmp_path / "abc123.done").read_text()
            assert "/some/file.pdf" in marker


# ============================================================
# Tests: processed_output_path
# ============================================================

class TestProcessedOutputPath:

    def test_pdf_to_json(self, tmp_path):
        """PDF filename must map to a .json path in PROCESSED_DATA_DIR."""
        from app.ingest import processed_output_path
        with patch("app.ingest.PROCESSED_DATA_DIR", str(tmp_path)):
            result = processed_output_path("module.pdf")
            assert result.endswith("module.json")

    def test_image_to_json(self, tmp_path):
        """Image filename must also map to .json."""
        from app.ingest import processed_output_path
        with patch("app.ingest.PROCESSED_DATA_DIR", str(tmp_path)):
            result = processed_output_path("notes.jpg")
            assert result.endswith("notes.json")


# ============================================================
# Tests: extract_from_image (mocked pytesseract)
# ============================================================

class TestExtractFromImage:

    def test_returns_single_page_dict(self, tmp_path):
        """Image ingestion must return exactly one page dict."""
        from app.ingest import extract_from_image

        fake_image = tmp_path / "page.png"
        # Create a minimal valid 1x1 white PNG using Pillow
        from PIL import Image as PILImage
        img = PILImage.new("RGB", (100, 100), color=(255, 255, 255))
        img.save(str(fake_image))

        mock_ocr_result = {
            "text": "hello OCR",
            "quality": 0.98,
            "elapsed": 0.5,
            "psm": 3,
            "oem": 3,
            "lang": "eng",
            "content_type": "printed",
            "is_reliable": True,
        }

        with patch("app.ocr.pytesseract.image_to_string", return_value="hello OCR"):
            result = extract_from_image(str(fake_image))

        assert len(result) == 1
        assert result[0]["page"] == 1
        assert result[0]["source"] == "image_ocr"
        assert result[0]["text"] == "hello OCR"
        assert result[0]["filename"] == "page.png"
        assert "ocr_quality" in result[0]
        assert "ocr_reliable" in result[0]

    def test_filename_is_basename_only(self, tmp_path):
        """filename field must be the basename, not the full path."""
        from app.ingest import extract_from_image
        from PIL import Image as PILImage

        fake_image = tmp_path / "notes.jpg"
        img = PILImage.new("RGB", (10, 10))
        img.save(str(fake_image))

        with patch("app.ocr.pytesseract.image_to_string", return_value=""):
            result = extract_from_image(str(fake_image))

        assert result[0]["filename"] == "notes.jpg"


# ============================================================
# Tests: ingest_file (mocked extract functions)
# ============================================================

class TestIngestFile:

    def _patch_dirs(self, processed_dir, cache_dir):
        """Return a context manager that patches both directory constants."""
        import unittest.mock as mock
        return mock.patch.multiple(
            "app.ingest",
            PROCESSED_DATA_DIR=processed_dir,
            CACHE_DIR=cache_dir,
        )

    def test_unsupported_extension_returns_none(self, tmp_path):
        """Files with unsupported extensions must be skipped gracefully."""
        from app.ingest import ingest_file
        fake = tmp_path / "document.docx"
        fake.write_text("some word document")

        cache = tmp_path / "cache"
        cache.mkdir()
        processed = tmp_path / "processed"
        processed.mkdir()

        with self._patch_dirs(str(processed), str(cache)):
            result = ingest_file(str(fake))

        assert result is None

    def test_already_cached_file_is_skipped(self, tmp_path):
        """A file whose hash is already in the cache must not be reprocessed."""
        from app.ingest import ingest_file, compute_file_hash, mark_as_processed

        fake = tmp_path / "doc.pdf"
        fake.write_bytes(b"%PDF-fake")
        cache = tmp_path / "cache"
        cache.mkdir()
        processed = tmp_path / "processed"
        processed.mkdir()

        file_hash = compute_file_hash(str(fake))

        with self._patch_dirs(str(processed), str(cache)):
            mark_as_processed(file_hash, str(fake))
            result = ingest_file(str(fake))

        assert result is None

    def test_force_flag_bypasses_cache(self, tmp_path):
        """force=True must reprocess even if the file is cached."""
        from app.ingest import ingest_file, compute_file_hash, mark_as_processed

        fake = tmp_path / "doc.pdf"
        fake.write_bytes(b"%PDF-fake")
        cache = tmp_path / "cache"
        cache.mkdir()
        processed = tmp_path / "processed"
        processed.mkdir()

        file_hash = compute_file_hash(str(fake))
        mock_pages = [{"filename": "doc.pdf", "page": 1, "text": "hello", "source": "text"}]

        with self._patch_dirs(str(processed), str(cache)):
            mark_as_processed(file_hash, str(fake))
            with patch("app.ingest.extract_from_pdf", return_value=mock_pages):
                result = ingest_file(str(fake), force=True)

        assert result is not None
        assert len(result) == 1

    def test_processed_json_is_saved(self, tmp_path):
        """After ingestion, a JSON file must exist in PROCESSED_DATA_DIR."""
        from app.ingest import ingest_file

        fake = tmp_path / "lecture.pdf"
        fake.write_bytes(b"%PDF-fake")
        cache = tmp_path / "cache"
        cache.mkdir()
        processed = tmp_path / "processed"
        processed.mkdir()

        mock_pages = [{"filename": "lecture.pdf", "page": 1, "text": "content", "source": "text"}]

        with self._patch_dirs(str(processed), str(cache)):
            with patch("app.ingest.extract_from_pdf", return_value=mock_pages):
                ingest_file(str(fake))

            output = processed / "lecture.json"
            assert output.exists()
            data = json.loads(output.read_text())
            assert data[0]["text"] == "content"


# ============================================================
# Tests: load_processed
# ============================================================

class TestLoadProcessed:

    def test_raises_if_not_found(self, tmp_path):
        """Loading a non-existent processed file must raise FileNotFoundError."""
        from app.ingest import load_processed
        with patch("app.ingest.PROCESSED_DATA_DIR", str(tmp_path)):
            with pytest.raises(FileNotFoundError, match="Run ingestion first"):
                load_processed("ghost.pdf")

    def test_returns_list_of_dicts(self, tmp_path):
        """load_processed must deserialise and return a list of page dicts."""
        from app.ingest import load_processed
        data = [{"filename": "x.pdf", "page": 1, "text": "hello", "source": "text"}]
        (tmp_path / "x.json").write_text(json.dumps(data))

        with patch("app.ingest.PROCESSED_DATA_DIR", str(tmp_path)):
            result = load_processed("x.pdf")

        assert result == data
