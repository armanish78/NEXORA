#!/bin/bash
set -e

echo "--- 2. Environment & Setup ---"
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
.venv/bin/python -m pip install -r requirements.txt

echo "--- 3. Data Pipelines (Ingestion to Indexing) ---"
echo "Running Ingestion Pipeline..."
python scripts/run_ingestion.py

echo "Running Cleaning Pipeline..."
python -m scripts.run_cleaning

echo "Running Chunking & Indexing..."
python scripts/run_indexing.py


echo "--- 5. Interacting with the AI ---"
echo "Starting Terminal Chat..."
python scripts/run_rag.py
