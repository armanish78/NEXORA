"""
scripts/run_cleaning.py
=======================
Phase 5 CLI runner for text cleaning.

Reads all JSON files in data/processed/, applies the cleaning pipeline,
and saves the output to data/cleaned/.

Usage:
    PYTHONPATH=. .venv/bin/python scripts/run_cleaning.py
"""

import json
import logging
from pathlib import Path

from app.cleaning import clean_pages

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    processed_dir = Path("data/processed")
    cleaned_dir = Path("data/cleaned")
    
    if not processed_dir.exists():
        logger.error(f"Directory not found: {processed_dir}")
        return
        
    cleaned_dir.mkdir(parents=True, exist_ok=True)
    
    for json_file in processed_dir.glob("*.json"):
        logger.info(f"Processing: {json_file.name}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            pages = json.load(f)
            
        # Count characters before
        char_count_before = sum(len(p.get("text", "")) for p in pages)
        
        # Clean
        cleaned_pages = clean_pages(pages)
        
        # Count characters after
        char_count_after = sum(len(p.get("text", "")) for p in cleaned_pages)
        diff = char_count_before - char_count_after
        
        logger.info(f"  Pages: {len(pages)}")
        logger.info(f"  Chars before: {char_count_before}")
        logger.info(f"  Chars after:  {char_count_after} (removed {diff} chars)")
        
        out_path = cleaned_dir / json_file.name
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_pages, f, indent=2, ensure_ascii=False)
            
        logger.info(f"  Saved to: {out_path}")


if __name__ == "__main__":
    main()
