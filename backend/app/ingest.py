"""
app/ingest.py
=============
Phases 2 & 3 — Document Ingestion and OCR

PURPOSE
-------
This module is the entry point for raw document processing.
It discovers supported files in data/raw/, extracts raw text
from each page (using native PDF text or OCR as a fallback),
attaches metadata (filename, page number, source type, quality),
and serialises the result to data/processed/ as a JSON file.

A SHA-256 hash of the file content is computed before processing.
If a processed output already exists for the same hash, the file
is skipped. This prevents expensive re-processing on subsequent runs.

Phase 3 change:
OCR is now delegated to app/ocr.py, which applies evidence-based
preprocessing (grayscale) and returns quality metadata per page.
Content type detection (printed vs handwritten) is applied per-file
based on filename conventions.

WHAT THIS MODULE DOES NOT DO
-----------------------------
- Text cleaning / normalisation  (Phase 5 — cleaning.py)
- Chunking                        (Phase 6 — chunking.py)
- OCR image preprocessing         (Phase 4 — preprocessing.py)
- Embeddings / indexing           (Phases 7–8)

OUTPUTS
-------
For each file processed, one JSON file is written to data/processed/.

Example output file: data/processed/BCS602-module-4-textbook.json

Each JSON file contains a list of page records:
[
    {
        "filename": "BCS602-module-4-textbook.pdf",
        "page": 1,
        "text": "...",
        "source": "text"   # or "ocr" or "image_ocr"
    },
    ...
]

SUPPORTED INPUT TYPES (Phase 2)
--------------------------------
- Native PDF  (text layer present)
- Scanned PDF (image-only pages fall back to basic OCR)
- JPG / JPEG / PNG standalone images (basic OCR)
"""

import hashlib
import io
import json
import logging
import os
import time
from pathlib import Path

import pymupdf
from PIL import Image

from app.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    CACHE_DIR,
)
from app.ocr import run_ocr, detect_content_type, ContentType, page_to_image

# ============================================================
# LOGGING
# ============================================================
logger = logging.getLogger(__name__)

# ============================================================
# SUPPORTED FILE EXTENSIONS
# ============================================================
SUPPORTED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

# Minimum character threshold to accept a page's native text
# rather than falling back to OCR.
# Pages with fewer characters than this are assumed to be
# image-only pages (e.g., diagrams) and are sent to OCR.
NATIVE_TEXT_MINIMUM = 30


# ============================================================
# HASHING
# ============================================================

def compute_file_hash(file_path: str) -> str:
    """
    Compute the SHA-256 hash of a file's raw bytes.

    WHY:
    SHA-256 produces a unique 64-character fingerprint for
    every unique file. If the file has not changed since the
    last run, its hash will be identical, and we can skip
    reprocessing it. This avoids running OCR again on large
    scanned PDFs.

    Returns:
        A lowercase hex string, e.g.
        "a3f2...d91b"
    """
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def hash_cache_path(file_hash: str) -> str:
    """
    Return the path where a hash record is stored.

    The cache directory records which file hashes have already
    been fully processed, preventing redundant work.
    """
    return os.path.join(CACHE_DIR, f"{file_hash}.done")


def is_already_processed(file_hash: str) -> bool:
    """Return True if this exact file content was already processed."""
    return os.path.exists(hash_cache_path(file_hash))


def mark_as_processed(file_hash: str, original_path: str) -> None:
    """
    Write a small marker file to the cache directory.

    The marker stores the original filename for traceability
    so a developer can tell which file a hash corresponds to.
    """
    cache_path = hash_cache_path(file_hash)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(f"processed: {original_path}\n")


# ============================================================
# PROCESSED OUTPUT PATHS
# ============================================================

def processed_output_path(filename: str) -> str:
    """
    Derive the output JSON path from the original filename.

    Example:
        "BCS602-module-4-textbook.pdf"
        →
        "data/processed/BCS602-module-4-textbook.json"
    """
    stem = Path(filename).stem
    return os.path.join(PROCESSED_DATA_DIR, f"{stem}.json")


# ============================================================
# TEXT EXTRACTION — PDF
# ============================================================

def extract_from_pdf(pdf_path: str, filename: str | None = None) -> list[dict]:
    """
    Extract text from every page of a PDF.

    Strategy per page:
    1. Try to get the native text layer (fast, lossless).
    2. If the text layer is too short (< NATIVE_TEXT_MINIMUM chars),
       render the page as a PNG image at 200 DPI and run OCR via
       app/ocr.py (Phase 3: evidence-based preprocessing + config).

    The content type (printed vs handwritten) is detected from the
    filename and passed to the OCR module so it can apply the
    appropriate preprocessing and reliability flag.

    Returns:
        A list of page dicts, one per page.
        Each dict contains: filename, page, text, source,
                            ocr_quality, ocr_reliable.
    """
    filename = filename if filename else Path(pdf_path).name
    content_type = detect_content_type(filename)
    pages = []

    document = pymupdf.open(pdf_path)

    for page_number, page in enumerate(document, start=1):
        raw_text = page.get_text().strip()

        if len(raw_text) >= NATIVE_TEXT_MINIMUM:
            # Native text layer is usable — no OCR needed.
            pages.append({
                "filename": filename,
                "page": page_number,
                "text": raw_text,
                "source": "text",
                "ocr_quality": None,
                "ocr_reliable": True,
            })

        else:
            # Page has no usable text layer — render image and OCR.
            image = page_to_image(pdf_path, page_number, dpi=200)
            ocr_result = run_ocr(image, content_type=content_type)

            pages.append({
                "filename": filename,
                "page": page_number,
                "text": ocr_result["text"],
                "source": "ocr",
                "ocr_quality": ocr_result["quality"],
                "ocr_reliable": ocr_result["is_reliable"],
            })

    document.close()

    return pages


# ============================================================
# TEXT EXTRACTION — STANDALONE IMAGE
# ============================================================

def extract_from_image(image_path: str, filename: str | None = None) -> list[dict]:
    """
    Extract text from a standalone image file (JPG/JPEG/PNG).

    Standalone images are treated as single-page documents.
    The entire image is sent through the OCR module (app/ocr.py)
    which applies evidence-based preprocessing and returns quality metadata.

    WHY:
    Students sometimes photograph lecture slides or handwritten notes.
    This allows those images to enter the RAG pipeline alongside PDFs.

    NOTE on handwriting:
    Tesseract's accuracy on handwritten text is significantly lower
    than on printed text (quality scores 0.82–0.90, but word-level
    accuracy is much worse). Phase 3 confirmed no preprocessing
    configuration reliably improves handwriting recognition.

    Returns:
        A list containing exactly one page dict.
    """
    filename = filename if filename else Path(image_path).name
    content_type = detect_content_type(filename)
    image = Image.open(image_path)
    ocr_result = run_ocr(image, content_type=content_type)

    return [{
        "filename": filename,
        "page": 1,
        "text": ocr_result["text"],
        "source": "image_ocr",
        "ocr_quality": ocr_result["quality"],
        "ocr_reliable": ocr_result["is_reliable"],
    }]


# ============================================================
# SINGLE-FILE INGESTION
# ============================================================

def ingest_file(file_path: str, force: bool = False, original_filename: str | None = None) -> list[dict] | None:
    """
    Ingest a single file: compute hash, check cache, extract,
    save to data/processed/, update cache.

    Args:
        file_path: Absolute or relative path to the file.
        force: If True, reprocess even if the hash cache says
               it has already been processed.
        original_filename: Optional original filename to use for identity instead of physical path.

    Returns:
        List of page dicts if processed, or None if skipped.
    """
    filename = original_filename if original_filename else Path(file_path).name
    extension = Path(original_filename if original_filename else file_path).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        logger.warning(f"Unsupported file type skipped: {filename}")
        return None

    # --------------------------------------------------------
    # Hash check — skip if already processed
    # --------------------------------------------------------
    file_hash = compute_file_hash(file_path)

    output_path = processed_output_path(filename)

    if not force and is_already_processed(file_hash) and os.path.exists(output_path):
        logger.info(f"Already processed (cached): {filename}")
        return None

    # --------------------------------------------------------
    # Extraction
    # --------------------------------------------------------
    logger.info(f"Processing: {filename}")
    start_time = time.perf_counter()

    try:
        if extension == ".pdf":
            pages = extract_from_pdf(file_path, filename=filename)
        else:
            pages = extract_from_image(file_path, filename=filename)
    except Exception as e:
        logger.error(f"Failed to process {filename}: {e}")
        return None

    elapsed = time.perf_counter() - start_time

    ocr_count = sum(1 for p in pages if p["source"] in ("ocr", "image_ocr"))
    text_count = len(pages) - ocr_count

    logger.info(
        f"  {filename}: {len(pages)} pages "
        f"({text_count} native text, {ocr_count} OCR) "
        f"in {elapsed:.2f}s"
    )

    # --------------------------------------------------------
    # Serialise to data/processed/
    # --------------------------------------------------------
    output_path = processed_output_path(filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    logger.info(f"  Saved: {output_path}")

    # --------------------------------------------------------
    # Mark as processed in cache
    # --------------------------------------------------------
    mark_as_processed(file_hash, file_path)

    return pages


# ============================================================
# BATCH INGESTION — ENTIRE data/raw/ DIRECTORY
# ============================================================

def ingest_all(force: bool = False) -> dict:
    """
    Discover and ingest all supported files in data/raw/.

    Files are processed in alphabetical order for reproducibility.

    Args:
        force: If True, reprocess all files ignoring the cache.

    Returns:
        A summary dict with counts and timing information.
    """
    raw_files = sorted([
        os.path.join(RAW_DATA_DIR, f)
        for f in os.listdir(RAW_DATA_DIR)
        if Path(f).suffix.lower() in SUPPORTED_EXTENSIONS
    ])

    if not raw_files:
        logger.warning(f"No supported files found in: {RAW_DATA_DIR}")
        return {"total": 0, "processed": 0, "skipped": 0, "failed": 0}

    logger.info(f"Found {len(raw_files)} file(s) in {RAW_DATA_DIR}")

    total = len(raw_files)
    processed = 0
    skipped = 0
    failed = 0

    overall_start = time.perf_counter()

    for file_path in raw_files:
        result = ingest_file(file_path, force=force)

        if result is None:
            # Could be skipped (cached) or failed (logged inside ingest_file)
            filename = Path(file_path).name
            file_hash = compute_file_hash(file_path)
            if is_already_processed(file_hash):
                skipped += 1
            else:
                failed += 1
        else:
            processed += 1

    overall_elapsed = time.perf_counter() - overall_start

    summary = {
        "total": total,
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
        "elapsed_seconds": round(overall_elapsed, 2),
    }

    logger.info(
        f"Ingestion complete: "
        f"{processed} processed, {skipped} skipped, {failed} failed "
        f"in {overall_elapsed:.2f}s"
    )

    return summary


# ============================================================
# LOAD PROCESSED OUTPUT
# ============================================================

def load_processed(filename: str) -> list[dict]:
    """
    Load previously processed pages from data/processed/.

    Later pipeline stages (cleaning, chunking, embedding) call
    this instead of re-reading the original PDF.

    Args:
        filename: The original file's basename, e.g.
                  "BCS602-module-4-textbook.pdf"

    Returns:
        List of page dicts.

    Raises:
        FileNotFoundError if the processed file does not exist.
    """
    output_path = processed_output_path(filename)

    if not os.path.exists(output_path):
        raise FileNotFoundError(
            f"No processed output found for '{filename}'. "
            f"Run ingestion first.\n"
            f"Expected path: {output_path}"
        )

    with open(output_path, "r", encoding="utf-8") as f:
        return json.load(f)