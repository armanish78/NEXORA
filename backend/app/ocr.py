"""
app/ocr.py
==========
Phase 3 — OCR Pipeline

PURPOSE
-------
This module is responsible for Optical Character Recognition (OCR):
converting a page image into machine-readable text.

It is called by app/ingest.py whenever a PDF page or standalone image
does not have a usable native text layer.

DESIGN PRINCIPLES
-----------------
1.  Separation of concerns.
    ingest.py decides WHEN to call OCR.
    This module decides HOW to perform OCR.

2.  Modular preprocessing.
    Image preprocessing steps (grayscale, thresholding) are defined as
    separate, composable functions. They can be chained independently and
    benchmarked individually. Phase 4 may add more preprocessing steps
    (deskewing, denoising) here.

3.  Evidence-based configuration.
    All default values (PSM mode, OEM mode, DPI, preprocessing choices)
    are derived from benchmarking experiments run in Phase 3, not from
    guesswork. See doc.md Section 14 for the full experiment log.

4.  Content-type awareness.
    The module distinguishes between printed scanned text and handwritten
    text. It does NOT claim accurate handwriting recognition — it simply
    applies the best available configuration and flags the result.

WHAT THIS MODULE DOES NOT DO
-----------------------------
- Deciding whether OCR is needed      (app/ingest.py — Phase 2)
- Advanced deskewing / denoising      (app/preprocessing.py — Phase 4)
- Text cleaning / normalisation       (app/cleaning.py — Phase 5)
- Chunking, embedding, or retrieval   (later phases)

TESSERACT CONFIGURATION NOTES
-------------------------------
PSM (Page Segmentation Mode):
  PSM=3  — Fully automatic segmentation. Best general-purpose mode.
            Tested against PSM=6 (single block): PSM=3 is equal or better
            on scanned textbook pages. PSM=6 introduced artefacts.

OEM (OCR Engine Mode):
  OEM=3  — Default: uses LSTM neural network if available, else legacy.
            We keep OEM=3 because Tesseract 5.x with LSTM is significantly
            more accurate than the legacy engine.

DPI:
  200 DPI is the project default.
  300 DPI was tested: +35% time, no measurable quality improvement
  on the scanned PDFs in this dataset. Not worth the cost.

HANDWRITING WARNING
--------------------
Tesseract is designed for printed text recognition. On handwritten text,
character quality scores consistently fall in the 0.82–0.90 range, but
the actual word-level accuracy is far lower because individual characters
may be correct while words are completely garbled.

Example of handwriting OCR output from this project:
  "Zl?rb'tvme sl Lmkmr% AS:M%MA gy" (intended: "Instance-based Learning")

Do NOT use this module to claim reliable handwriting recognition.
"""

import io
import logging
import time
from enum import Enum
from typing import Optional

import pytesseract
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


# ============================================================
# CONTENT TYPE
# ============================================================

class ContentType(Enum):
    """
    Describes the nature of the content being OCR'd.

    PRINTED:
        Standard printed text from books, textbooks, printed notes,
        printed lab manuals. This is what Tesseract was designed for.
        Expected quality: high.

    HANDWRITTEN:
        Handwritten notes, diagrams with handwritten labels.
        Tesseract is NOT reliable for this content type.
        Expected quality: low. Results should be used with caution.

    UNKNOWN:
        Content type has not been determined. The module will treat it
        like PRINTED (best-effort) but flag it in the result.
    """
    PRINTED = "printed"
    HANDWRITTEN = "handwritten"
    UNKNOWN = "unknown"


# ============================================================
# OCR CONFIGURATION
# ============================================================

# Tesseract PSM=3: Fully automatic page segmentation (default).
# Chosen after benchmarking against PSM=4, PSM=6 on real scanned pages.
# See doc.md Section 14 for benchmark details.
DEFAULT_PSM = 3

# Tesseract OEM=3: Use LSTM engine (neural network-based), fallback to legacy.
# LSTM is significantly more accurate on printed text.
DEFAULT_OEM = 3

# Tesseract language: English only in Phase 3.
# Multilingual support is deferred to Phase 19.
DEFAULT_LANG = "eng"


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def to_grayscale(image: Image.Image) -> Image.Image:
    """
    Convert an RGB image to grayscale (single-channel).

    WHY:
    Tesseract works on luminance (brightness) values, not colour.
    Converting to grayscale removes irrelevant colour information
    and reduces the pixel data that must be processed.

    MEASURED EFFECT on this dataset:
    - Colour input:    ~3.15s per page
    - Grayscale input: ~2.33s per page
    - Quality score:   identical (0.969)

    Conclusion: grayscale is a worthwhile preprocessing step —
    it reduces OCR time by ~26% with no quality loss.
    """
    return ImageOps.grayscale(image)


def apply_threshold(image: Image.Image, threshold: int = 150) -> Image.Image:
    """
    Apply a binary threshold to a grayscale image.

    Pixels brighter than `threshold` become white (255).
    Pixels darker than `threshold` become black (0).

    WHY THIS CAN HELP:
    Binarization removes background noise, stains, and grey shadows
    from scanned pages, giving Tesseract cleaner character shapes.

    MEASURED EFFECT on this dataset:
    - Baseline (colour):         quality=0.969, time=3.15s
    - Grayscale + threshold=150: quality=0.968, time=2.16s
    Quality is equivalent. No improvement for already-clean scans.

    WHEN IT HELPS:
    Thresholding is most useful for documents with uneven lighting,
    coffee stains, or yellowed paper. The PDFs in this dataset are
    clean scans, so the benefit is minimal beyond the grayscale speedup.

    Args:
        image: Must be a grayscale (mode='L') image.
               Call to_grayscale() first if needed.
        threshold: Pixel value cutoff, 0–255. Default 150.
    """
    if image.mode != "L":
        image = to_grayscale(image)
    return image.point(lambda p: 255 if p > threshold else 0)


def preprocess_for_printed(image: Image.Image) -> Image.Image:
    """
    Apply the evidence-based preprocessing pipeline for printed text.

    Based on Phase 3 benchmarks:
    - Grayscale conversion: reduces time by ~26%, same quality.
    - Thresholding: no additional quality benefit on clean scans.
    - Sharpening: no quality benefit, adds time.
    - 300 DPI: no quality benefit, +35% time.

    Decision: apply grayscale only.
    Additional steps are reserved for Phase 4 if needed for specific
    problem cases (low-contrast scans, skewed pages, etc.)

    Returns:
        A preprocessed PIL Image ready for Tesseract.
    """
    return to_grayscale(image)


def preprocess_for_handwriting(image: Image.Image) -> Image.Image:
    """
    Apply best-effort preprocessing for handwritten content.

    IMPORTANT: No preprocessing configuration was found to reliably
    improve handwriting recognition quality. Character quality scores
    for handwritten pages consistently fell in the 0.82–0.90 range
    regardless of preprocessing applied.

    The fundamental limitation is that Tesseract is a printed-text
    OCR engine. It was not trained on handwritten characters.

    We apply grayscale (for consistency and speed), but the output
    quality will remain poor for true handwritten content.

    Returns:
        A preprocessed PIL Image ready for Tesseract.
    """
    return to_grayscale(image)


# ============================================================
# OCR EXECUTION
# ============================================================

def run_ocr(
    image: Image.Image,
    content_type: ContentType = ContentType.PRINTED,
    psm: int = DEFAULT_PSM,
    oem: int = DEFAULT_OEM,
    lang: str = DEFAULT_LANG,
) -> dict:
    """
    Run Tesseract OCR on a PIL Image and return a result dict.

    This is the core OCR function. It:
    1. Applies appropriate preprocessing for the content type.
    2. Runs Tesseract with the specified configuration.
    3. Returns the raw OCR text along with quality and timing metadata.

    Args:
        image:        PIL Image to process. Can be RGB or grayscale.
        content_type: ContentType enum indicating printed vs handwritten.
        psm:          Tesseract Page Segmentation Mode (default: 3).
        oem:          Tesseract OCR Engine Mode (default: 3 = LSTM).
        lang:         Tesseract language code (default: 'eng').

    Returns:
        dict with keys:
            text      (str)   — raw OCR output (uncleaned)
            quality   (float) — heuristic character quality score 0.0–1.0
            elapsed   (float) — OCR time in seconds
            psm       (int)   — PSM mode used
            oem       (int)   — OEM mode used
            lang      (str)   — language used
            content_type (str) — 'printed', 'handwritten', or 'unknown'
            is_reliable (bool) — False for handwritten content
    """
    # Select preprocessing based on content type
    if content_type == ContentType.HANDWRITTEN:
        processed_image = preprocess_for_handwriting(image)
        is_reliable = False
    else:
        processed_image = preprocess_for_printed(image)
        is_reliable = True

    config = f"--psm {psm} --oem {oem}"

    start_time = time.perf_counter()
    raw_text = pytesseract.image_to_string(processed_image, lang=lang, config=config).strip()
    elapsed = time.perf_counter() - start_time

    quality = _compute_quality_score(raw_text)

    return {
        "text": raw_text,
        "quality": round(quality, 4),
        "elapsed": round(elapsed, 3),
        "psm": psm,
        "oem": oem,
        "lang": lang,
        "content_type": content_type.value,
        "is_reliable": is_reliable,
    }


def _compute_quality_score(text: str) -> float:
    """
    Compute a heuristic quality score for OCR output.

    Score = (count of 'good' characters) / (total characters)

    'Good' characters are: alphanumeric, space, and common punctuation.
    OCR noise typically introduces unusual Unicode characters, backslashes,
    brackets, and other artefacts that reduce the score.

    LIMITATIONS:
    This is a rough heuristic, not a true word-level accuracy measure.
    A score of 0.90 means 90% of characters look reasonable, but the
    text may still contain mis-recognised words.
    A score of 0.82 (typical for handwriting) means ~18% of characters
    are noise, which in practice makes many words unreadable.

    Scale (observed in this project):
        > 0.95 — Good: printed text, reliably OCR'd
        0.85–0.95 — Fair: some noise, may affect retrieval quality
        < 0.85 — Poor: handwriting or low-quality scan, use with caution

    Args:
        text: Raw OCR output string.

    Returns:
        Float between 0.0 (all noise) and 1.0 (all clean characters).
    """
    if not text:
        return 0.0

    GOOD_CHARS = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        " \t\n.,;:!?()-/'\"+=%<>[]{}@#*"
    )

    good = sum(1 for c in text if c in GOOD_CHARS)
    return good / len(text)


# ============================================================
# DETECTION HELPERS
# ============================================================

def detect_content_type(filename: str) -> ContentType:
    """
    Attempt to detect content type from filename conventions.

    This is a heuristic for batch processing. For production use,
    a user-supplied content type flag is more reliable.

    Current logic:
    - If the filename contains 'written', 'handwritten', 'notes',
      'notebook', or 'hand' → assume HANDWRITTEN.
    - Otherwise → assume PRINTED.

    This will be revisited once a UI exists (Phase 25) where users
    can explicitly label their uploads.

    Args:
        filename: Basename of the file, e.g. "module-3-written.pdf"

    Returns:
        ContentType enum value.
    """
    lower = filename.lower()
    handwriting_keywords = {"written", "handwritten", "notebook", "notes", "hand"}

    for keyword in handwriting_keywords:
        if keyword in lower:
            logger.debug(f"Detected handwriting content type for: {filename}")
            return ContentType.HANDWRITTEN

    return ContentType.PRINTED


# ============================================================
# IMAGE FROM PDF PAGE (helper used in tests)
# ============================================================

def page_to_image(pdf_path: str, page_number: int, dpi: int = 200) -> Image.Image:
    """
    Render a single PDF page to a PIL Image at the specified DPI.

    This helper is provided here so tests and evaluation scripts
    can render pages without depending on the full ingest pipeline.

    DPI=200 is the project default based on Phase 3 benchmarks:
    - 200 DPI: ~2.33s/page after greyscale, quality=0.969
    - 300 DPI: ~4.34s/page, quality=0.969 (no improvement, +86% time)

    IMPORTANT: The PIL Image is fully loaded into memory before the
    PDF document is closed. This avoids a ValueError caused by lazy
    loading from a BytesIO buffer that references a closed PyMuPDF
    pixmap.

    Args:
        pdf_path:    Path to the PDF file.
        page_number: 1-based page number (matches the 'page' metadata field).
        dpi:         Rendering resolution. Default: 200.

    Returns:
        PIL Image object (fully loaded in memory).

    Raises:
        IndexError: If page_number is out of range (< 1 or > total pages).
    """
    import pymupdf

    document = pymupdf.open(pdf_path)

    total_pages = len(document)

    # Validate page number (1-based)
    if page_number < 1 or page_number > total_pages:
        document.close()
        raise IndexError(
            f"Page {page_number} is out of range. "
            f"Document has {total_pages} pages."
        )

    # Convert from 1-based (human) to 0-based (PyMuPDF internal)
    page_index = page_number - 1
    page = document[page_index]
    pix = page.get_pixmap(dpi=dpi)

    # Load bytes into memory NOW, while the document is still open.
    # Calling Image.open() on BytesIO with a lazy-loaded image and then
    # closing the document causes a ValueError: 'document closed'.
    image_bytes = pix.tobytes("png")
    document.close()

    image = Image.open(io.BytesIO(image_bytes))
    image.load()  # Force full load into memory

    return image
