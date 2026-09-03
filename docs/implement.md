# Implementation Guide: How to Run the Core Brain

This document provides a strictly linear, step-by-step guide to running the Antigravity Study Assistant. If you follow these steps exactly in order, you will successfully process a PDF and interact with the AI, missing nothing.

---

## Phase 1: Environment Setup

Before doing anything, you need to set up the Python environment.

1. **Open a terminal** in the root of the project (`/home/nova/Desktop/RAG`).
2. **Create a virtual environment** (if not already created):
   ```bash
   python3 -m venv .venv
   ```
3. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The first time the system runs, it will automatically download the `all-MiniLM-L6-v2` embedding model and the `Qwen2.5-3B-Instruct` AI model. Ensure you have internet access and at least 10GB of free disk space).*

---

## Phase 2: Processing Your Documents (The Linear Pipeline)

The system needs to read, clean, and index your PDFs before it can answer questions. You must run these scripts **in this exact order**.

### Step 1: Add your PDF
Place the PDF you want to study into the `data/raw/` directory.
*(Example: `data/raw/my_textbook.pdf`)*

### Step 2: Run Ingestion (OCR & Text Extraction)
This step extracts text from the PDF. If the PDF contains scanned images, it will use Tesseract OCR to read them.
```bash
python scripts/run_ingestion.py
```
- **What it does:** Reads the PDFs in `data/raw/` and outputs raw JSON files into `data/processed/`. It also records the file hash in the SQLite database so it doesn't process the same file twice.

### Step 3: Run Cleaning
Raw OCR text often contains garbage characters, headers, and page numbers that confuse the AI.
```bash
python -m scripts.run_cleaning
```
- **What it does:** Reads from `data/processed/`, cleans the text using regex rules, and outputs clean JSON files into `data/cleaned/`.

### Step 4: Run Indexing (Building the Search Database)
The system must cut the cleaned text into "chunks" and embed them into a mathematical vector database (FAISS) so the AI can search them instantly.
```bash
python scripts/run_indexing.py
```
- **What it does:** Reads from `data/cleaned/`, chunks the text (512 characters), builds structural outline chunks, computes embeddings, and builds a BM25 lexical index. It saves the results to `model/indexes/v2/faiss.index`, `model/indexes/v2/chunks.pkl`, and `model/indexes/v2/bm25.pkl`.

---

## Phase 3: Interacting with the AI

Once the index is built (Phase 2 is complete), the Core Brain is fully active. You have multiple ways to use it.

### Option A: The Terminal Chat (Quickest)
You can chat with the AI directly in your terminal.
```bash
python scripts/run_rag.py
```
- You can ask questions based on your PDFs, or type `quiz` to have it generate a multiple-choice quiz based on your weak topics.


## Retrieval Architecture Updates
- `app/retrieve.py`
  - Replaces regex parsing with generic multi-strategy retrieval (FAISS + BM25).
  - Uses Reciprocal Rank Fusion (RRF) to merge candidate pools.
  - **Context Assembly**: Intelligently expands top chunks by fetching contiguous neighboring chunks that share the same heading and document filename (up to 8 chunks bidirectionally), smoothly assembling full logical sections for the LLM.
  - **Structural Resolution**: If a structural outline chunk is matched via query terms, the retriever identifies the matched heading. The underlying content chunks then mathematically inherit the outline's structural relevance. This uses **Structural Normalization** to strip generic query intent words (e.g. "compare", "types") so only domain-specific words calculate the heading overlap.
  - Accepts a generic `filename` filter for **Document Scoping** at the API level and in interactive scripts to prevent cross-document contamination.

## Generation Architecture Updates
- `app/generator.py`
  - **Single-Retry Citation Enforcement**: Checks the LLM's raw output for parsed `[S#]` citations. If missing, it automatically injects a correction prompt and retries generation. If it fails twice, a safe failure is returned to the user.
  - **Dynamic Generation Budget**: Initial generation and retry passes use `max_tokens=768` instead of the default 512, safely permitting long-form explanatory queries while remaining fast for short factual answers.

### Option B: The Web API (For frontends)
If you are connecting a mobile app or a frontend web interface, start the FastAPI server:
```bash
uvicorn app.api.main:app --reload
```
- The API will start at `http://127.0.0.1:8000`.
- You can view the interactive API documentation by visiting `http://127.0.0.1:8000/docs` in your browser.

---

## Troubleshooting & Safety

1. **Out of Memory (OOM) Crashes:** Do NOT run `run_rag.py` and the Web API at the same time. Generating AI text requires heavy RAM/VRAM. Running two instances of the `Qwen` model will crash your computer.
2. **Missing Module Errors:** Always make sure your virtual environment is activated (`source .venv/bin/activate`) before running any script.
3. **Stale Data:** If you delete a PDF and want to start completely fresh, you must run all three steps of Phase 2 again (Ingestion -> Cleaning -> Indexing).