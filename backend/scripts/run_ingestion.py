"""
scripts/run_ingestion.py
========================
Standalone runner for Phase 2 document ingestion.

Usage (from project root):
    .venv/bin/python scripts/run_ingestion.py
    .venv/bin/python scripts/run_ingestion.py --force
    .venv/bin/python scripts/run_ingestion.py --file data/raw/mypdf.pdf

Options:
    --force        Reprocess all files, ignoring the hash cache.
    --file PATH    Process a single specific file.
"""

import argparse
import logging
import sys
import os

# Ensure the project root is on the Python path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ingest import ingest_all, ingest_file
from app.config import RAW_DATA_DIR

# ============================================================
# LOGGING SETUP
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Educational RAG — Document Ingestion"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocess all files, ignoring the hash cache.",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Process a single specific file instead of all files in data/raw/.",
    )
    args = parser.parse_args()

    if args.file:
        # Single-file mode
        logger.info(f"Single-file ingestion: {args.file}")
        result = ingest_file(args.file, force=args.force)
        if result is None:
            logger.info("File was skipped or failed. Check logs above.")
        else:
            logger.info(f"Done. Extracted {len(result)} pages.")
    else:
        # Batch mode
        logger.info(f"Batch ingestion from: {RAW_DATA_DIR}")
        summary = ingest_all(force=args.force)
        print("\n" + "=" * 60)
        print("  INGESTION SUMMARY")
        print("=" * 60)
        print(f"  Total files found : {summary['total']}")
        print(f"  Processed         : {summary['processed']}")
        print(f"  Skipped (cached)  : {summary['skipped']}")
        print(f"  Failed            : {summary['failed']}")
        print(f"  Total time        : {summary['elapsed_seconds']:.2f}s")
        print("=" * 60)


if __name__ == "__main__":
    main()
