#!/bin/bash
set -e

echo "--- Phase 1: Environment Setup ---"
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "--- Phase 2: Processing Documents ---"
echo "Running Ingestion (OCR & Text Extraction)..."
python scripts/run_ingestion.py

echo "Running Cleaning..."
python -m scripts.run_cleaning

echo "Running Indexing (Building the Search Database)..."
python scripts/run_indexing.py

echo "--- Phase 3: Interacting with the AI ---"
echo "Starting Terminal Chat..."
python scripts/run_rag.py
