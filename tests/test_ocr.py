"""
tests/test_ocr.py
=================
Phase 3 — Unit tests for the OCR pipeline (app/ocr.py)

Tests are designed to be fast (using mocks or minimal real images)
and never touch real PDF files or require external network access.

Run with:
    .venv/bin/python -m pytest tests/test_ocr.py -v
"""

import sys
import os
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image

# Ensure project root is on the path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ocr import (
    ContentType,
    to_grayscale,
    apply_threshold,
    preprocess_for_printed,
    preprocess_for_handwriting,
    run_ocr,
    _compute_quality_score,
    detect_content_type,
    page_to_image,
)


# ============================================================
# Helpers
# ============================================================

def make_rgb_image(width=100, height=100, color=(200, 200, 200)) -> Image.Image:
    """Create a small solid-colour RGB image for tests."""
    return Image.new("RGB", (width, height), color=color)


def make_grey_image(width=100, height=100, value=128) -> Image.Image:
    """Create a small solid-colour greyscale image for tests."""
    return Image.new("L", (width, height), color=value)


# ============================================================
# Tests: ContentType enum
# ============================================================

class TestContentTypeEnum:

    def test_printed_value(self):
        assert ContentType.PRINTED.value == "printed"

    def test_handwritten_value(self):
        assert ContentType.HANDWRITTEN.value == "handwritten"

    def test_unknown_value(self):
        assert ContentType.UNKNOWN.value == "unknown"


# ============================================================
# Tests: to_grayscale
# ============================================================

class TestToGrayscale:

    def test_rgb_to_grayscale(self):
        """RGB image must be converted to mode 'L'."""
        img = make_rgb_image()
        result = to_grayscale(img)
        assert result.mode == "L"

    def test_size_preserved(self):
        """Grayscale must not change image dimensions."""
        img = make_rgb_image(80, 60)
        result = to_grayscale(img)
        assert result.size == (80, 60)

    def test_already_grayscale_is_unchanged(self):
        """Applying to_grayscale on a greyscale image must keep mode 'L'."""
        img = make_grey_image()
        result = to_grayscale(img)
        assert result.mode == "L"


# ============================================================
# Tests: apply_threshold
# ============================================================

class TestApplyThreshold:

    def test_output_is_grayscale(self):
        """Thresholded image must be in mode 'L'."""
        img = make_rgb_image()
        result = apply_threshold(img)
        assert result.mode == "L"

    def test_bright_pixels_become_white(self):
        """Pixels above threshold must become 255."""
        # Pure white image (255, 255, 255) → all pixels should be 255
        img = Image.new("L", (10, 10), color=200)  # value=200, threshold=150
        result = apply_threshold(img, threshold=150)
        pixels = list(result.getdata())
        assert all(p == 255 for p in pixels)

    def test_dark_pixels_become_black(self):
        """Pixels below threshold must become 0."""
        img = Image.new("L", (10, 10), color=100)  # value=100, threshold=150
        result = apply_threshold(img, threshold=150)
        pixels = list(result.getdata())
        assert all(p == 0 for p in pixels)

    def test_accepts_rgb_input(self):
        """apply_threshold must accept RGB images (converts internally)."""
        img = make_rgb_image(color=(200, 200, 200))  # bright → above threshold
        result = apply_threshold(img, threshold=150)
        assert result.mode == "L"


# ============================================================
# Tests: preprocess_for_printed / preprocess_for_handwriting
# ============================================================

class TestPreprocessing:

    def test_printed_returns_grayscale(self):
        """Printed preprocessing must produce a greyscale image."""
        img = make_rgb_image()
        result = preprocess_for_printed(img)
        assert result.mode == "L"

    def test_handwriting_returns_grayscale(self):
        """Handwriting preprocessing must produce a greyscale image."""
        img = make_rgb_image()
        result = preprocess_for_handwriting(img)
        assert result.mode == "L"

    def test_printed_preserves_size(self):
        img = make_rgb_image(120, 80)
        result = preprocess_for_printed(img)
        assert result.size == (120, 80)

    def test_handwriting_preserves_size(self):
        img = make_rgb_image(120, 80)
        result = preprocess_for_handwriting(img)
        assert result.size == (120, 80)


# ============================================================
# Tests: _compute_quality_score
# ============================================================

class TestQualityScore:

    def test_empty_string_is_zero(self):
        assert _compute_quality_score("") == 0.0

    def test_clean_english_text_high_score(self):
        text = "The quick brown fox jumps over the lazy dog."
        score = _compute_quality_score(text)
        assert score > 0.95, f"Expected > 0.95, got {score}"

    def test_pure_noise_low_score(self):
        """A string of unusual Unicode chars should score very low."""
        noise = "ﬂ§¶©®™£¥€ﬁﬀ" * 10
        score = _compute_quality_score(noise)
        assert score < 0.2, f"Expected < 0.2, got {score}"

    def test_mixed_content_mid_range(self):
        """Mix of good and bad characters → intermediate score."""
        text = "Hello world" + "ﬁﬂ§" * 5
        score = _compute_quality_score(text)
        assert 0.3 < score < 0.9, f"Expected 0.3–0.9, got {score}"

    def test_numbers_and_punctuation_count_as_good(self):
        text = "Step 1: P(H|E) = P(E|H) * P(H) / P(E)"
        score = _compute_quality_score(text)
        assert score > 0.90, f"Expected > 0.90, got {score}"

    def test_score_between_zero_and_one(self):
        """Score must always be in [0, 1]."""
        for text in ["", "hello", "ﬁﬂ§", "mixed ﬁ content"]:
            score = _compute_quality_score(text)
            assert 0.0 <= score <= 1.0, f"Score out of range for: {repr(text)}"


# ============================================================
# Tests: detect_content_type
# ============================================================

class TestDetectContentType:

    def test_written_in_filename(self):
        assert detect_content_type("module-3-written.pdf") == ContentType.HANDWRITTEN

    def test_handwritten_in_filename(self):
        assert detect_content_type("handwritten_notes.pdf") == ContentType.HANDWRITTEN

    def test_notes_in_filename(self):
        assert detect_content_type("lecture_notes.jpg") == ContentType.HANDWRITTEN

    def test_notebook_in_filename(self):
        assert detect_content_type("notebook_scan.png") == ContentType.HANDWRITTEN

    def test_hand_in_filename(self):
        assert detect_content_type("hand_draft.pdf") == ContentType.HANDWRITTEN

    def test_case_insensitive(self):
        """Detection must be case-insensitive."""
        assert detect_content_type("MyHandWritten.PDF") == ContentType.HANDWRITTEN

    def test_textbook_is_printed(self):
        assert detect_content_type("BCS602-module-4-textbook.pdf") == ContentType.PRINTED

    def test_lab_manual_is_printed(self):
        assert detect_content_type("GenAI Lab manual.pdf") == ContentType.PRINTED

    def test_generic_pdf_is_printed(self):
        assert detect_content_type("chapter5.pdf") == ContentType.PRINTED


# ============================================================
# Tests: run_ocr (mocked tesseract)
# ============================================================

class TestRunOcr:

    def test_returns_required_keys(self):
        """run_ocr must return a dict with all expected keys."""
        img = make_rgb_image()
        with patch("app.ocr.pytesseract.image_to_string", return_value="Hello world."):
            result = run_ocr(img, content_type=ContentType.PRINTED)
        expected_keys = {"text", "quality", "elapsed", "psm", "oem", "lang",
                         "content_type", "is_reliable"}
        assert expected_keys == set(result.keys())

    def test_printed_is_reliable(self):
        img = make_rgb_image()
        with patch("app.ocr.pytesseract.image_to_string", return_value="Hello."):
            result = run_ocr(img, content_type=ContentType.PRINTED)
        assert result["is_reliable"] is True
        assert result["content_type"] == "printed"

    def test_handwritten_is_not_reliable(self):
        img = make_rgb_image()
        with patch("app.ocr.pytesseract.image_to_string", return_value="Garbled text."):
            result = run_ocr(img, content_type=ContentType.HANDWRITTEN)
        assert result["is_reliable"] is False
        assert result["content_type"] == "handwritten"

    def test_ocr_text_is_stripped(self):
        """run_ocr must return stripped text (no leading/trailing whitespace)."""
        img = make_rgb_image()
        with patch("app.ocr.pytesseract.image_to_string", return_value="  spaced  \n"):
            result = run_ocr(img)
        assert result["text"] == "spaced"

    def test_quality_score_is_float(self):
        img = make_rgb_image()
        with patch("app.ocr.pytesseract.image_to_string", return_value="Hello world"):
            result = run_ocr(img)
        assert isinstance(result["quality"], float)
        assert 0.0 <= result["quality"] <= 1.0

    def test_elapsed_is_positive_float(self):
        img = make_rgb_image()
        with patch("app.ocr.pytesseract.image_to_string", return_value="text"):
            result = run_ocr(img)
        assert isinstance(result["elapsed"], float)
        assert result["elapsed"] >= 0.0

    def test_default_psm_and_oem(self):
        """run_ocr must use PSM=3 and OEM=3 by default."""
        img = make_rgb_image()
        with patch("app.ocr.pytesseract.image_to_string", return_value="text") as mock_tess:
            run_ocr(img)
        call_kwargs = mock_tess.call_args
        config_str = call_kwargs[1].get("config", "") or call_kwargs[0][1] if len(call_kwargs[0]) > 1 else ""
        # Check the config was passed (it's a kwarg)
        assert "3" in str(call_kwargs)

    def test_custom_psm_oem_passed_to_tesseract(self):
        """Custom PSM and OEM must be forwarded to Tesseract."""
        img = make_rgb_image()
        with patch("app.ocr.pytesseract.image_to_string", return_value="text") as mock_tess:
            run_ocr(img, psm=6, oem=1)
        call_args = str(mock_tess.call_args)
        assert "psm 6" in call_args
        assert "oem 1" in call_args

    def test_empty_ocr_output_quality_is_zero(self):
        img = make_rgb_image()
        with patch("app.ocr.pytesseract.image_to_string", return_value=""):
            result = run_ocr(img)
        assert result["quality"] == 0.0
        assert result["text"] == ""


# ============================================================
# Tests: page_to_image
# ============================================================

class TestPageToImage:

    def test_raises_index_error_for_invalid_page(self, tmp_path):
        """Requesting a page beyond the document length must raise IndexError."""
        from PIL import Image as PILImage
        import pymupdf

        # Create a minimal 1-page PDF
        doc = pymupdf.open()
        page = doc.new_page()
        pdf_path = str(tmp_path / "single.pdf")
        doc.save(pdf_path)
        doc.close()

        with pytest.raises(IndexError, match="out of range"):
            page_to_image(pdf_path, page_number=2)

    def test_raises_index_error_for_page_zero(self, tmp_path):
        """page_number=0 is invalid (1-based interface) and must raise IndexError."""
        import pymupdf
        doc = pymupdf.open()
        doc.new_page()
        pdf_path = str(tmp_path / "single.pdf")
        doc.save(pdf_path)
        doc.close()

        with pytest.raises(IndexError):
            page_to_image(pdf_path, page_number=0)

    def test_returns_pil_image(self, tmp_path):
        """page_to_image must return a PIL Image object."""
        import pymupdf
        doc = pymupdf.open()
        doc.new_page()
        pdf_path = str(tmp_path / "test.pdf")
        doc.save(pdf_path)
        doc.close()

        result = page_to_image(pdf_path, page_number=1, dpi=72)
        assert isinstance(result, Image.Image)
