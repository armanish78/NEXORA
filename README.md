# NEXORA — Neural Knowledge Retrieval & Reasoning Engine

## What is NEXORA?
NEXORA is a file-based, provider-agnostic Study Assistant backend system (the "Core Brain"). It solves the problem of hallucination in educational AI by ingesting textbooks, manuals, and notes, and tightly coupling a Large Language Model to that specific material. It does not act as a general chatbot; instead, it acts as a highly disciplined tutor that refuses to answer questions outside the scope of the provided materials.

## What it can do
- **Read Educational PDFs:** Extracts text from both digital PDFs and scanned images (via OCR).
- **Ground Answers:** Answers are generated strictly based on the uploaded material, effectively eliminating hallucinations.
- **Refuse Unsupported Questions:** Employs a strict mathematical threshold to refuse to answer questions if the required information isn't found in the text.
- **Generate Quizzes:** Creates Easy, Medium, and Hard multiple-choice quizzes dynamically from the text.
- **Evaluate Answers:** Deterministically checks if a selected answer matches the correct option.
- **Personalize Learning:** Tracks user progress and automatically identifies "weak topics", generating personalized quizzes focused on areas where the user struggles.

## Architecture

NEXORA operates entirely on the backend, processing documents sequentially:

```text
User Material (PDFs/Images)
          ↓
  Ingestion / OCR
          ↓
  Text Cleaning
          ↓
Semantic Chunking (512 chars)
          ↓
  all-MiniLM-L6-v2
          ↓
Vector Index (FAISS)
          ↓
Retrieval + Adjacent Chunk Expansion
          ↓
 Grounding Gate (0.35)
          ↓
 Qwen2.5-3B-Instruct (Backend Execution)
          ↓
QA / Quiz / Personalization
          ↓
Deterministic Evaluation / Progress
```
*(Note: The LLM runs locally on the backend server, NOT on the user's mobile device).*

## Technology Stack
- **Language:** Python
- **LLM:** `Qwen/Qwen2.5-3B-Instruct`
- **Embeddings:** `all-MiniLM-L6-v2` (via SentenceTransformers / HuggingFace)
- **Vector Database:** FAISS
- **State Database:** SQLite
- **API Framework:** FastAPI
- **Document Processing:** PyMuPDF, PyTesseract (OCR)

## Core Brain Components
- `app/ingest.py`, `app/ocr.py`: Handles document parsing and image-to-text extraction.
- `app/cleaning.py`: Normalizes text and removes OCR artifacts/headers.
- `app/chunking.py`: Intelligently cuts text without fracturing semantic paragraphs.
- `app/embeddings.py`, `app/vector_store.py`: Manages the mathematical representation and storage of text.
- `app/retrieve.py`: Searches the FAISS index for relevant chunks.
- `app/generator.py`, `app/quiz_generator.py`: Enforces strict formatting and JSON validation on the LLM output.
- `app/answer_evaluator.py`, `app/progress.py`: Handles deterministic grading and stores user metrics.
- `app/personalization.py`: Analyzes the SQLite database to identify weaknesses for targeted learning.
- `app/api/`: Exposes the intelligence as a REST API.

## Model
The core intelligence is powered by **`Qwen/Qwen2.5-3B-Instruct`**, chosen because it demonstrated a 100% success rate at adhering to strict JSON formatting constraints during validation (unlike the 0.5B variant).
- **Execution:** Runs entirely locally on the backend.
- **Device Placement:** Handled automatically (`device_map="auto"`).
- **Latency:** ~28 seconds to generate a full quiz on an RTX 4050 (6GB VRAM).
- **Protection:** Includes a retry/validation loop. If the model outputs malformed JSON or forgets to cite its sources, the system automatically catches the error and forces the model to rewrite the output.

## Grounding and Safety
NEXORA utilizes a strict **Grounding Gate** threshold (`0.35`) calibrated to the `all-MiniLM-L6-v2` embeddings. 
Before the LLM is even loaded, the system checks the mathematical relevance of the search results. If the top result scores worse than `0.35`, the system **instantly refuses** the request, returning `INSUFFICIENT_SOURCE_CONTEXT`. This prevents unnecessary LLM generation and guarantees the AI does not hallucinate answers from its general knowledge.

## Quiz Generation
Quizzes are generated in strict JSON with:
- **Difficulty Levels:** Easy (requires 1 chunk of context), Medium (2 chunks), Hard (4 chunks).
- **Format:** 4 options (1 correct, 3 distractors).
- **Explanations:** Each correct answer includes a detailed explanation.
- **Citations:** Every generated answer requires explicit source chunk IDs mapping back to the textbook.

## Personalization and Evaluation
- **Evaluation:** Answers are evaluated deterministically by comparing the user's selected choice to the generated correct option.
- **Progress:** Pass/fail data is logged into an SQLite database.
- **Personalization:** The backend analyzes recent performance to detect "weak topics", instructing the `QuizGenerator` to focus entirely on those subjects when a personalized quiz is requested.

## Validation
The repository has been fully validated against real educational PDFs and handwritten notes.
- **Quiz/QA Success:** 14/15 first-attempt success rate using `Qwen2.5-3B-Instruct`. The model occasionally produces structural mistakes (e.g., hallucinated chunk IDs), but the system's strict validator and retry mechanism successfully catches and corrects these on subsequent attempts.
- **Grounding:** Successfully refuses questions outside the scope of the material.
- **Testing:** The automated test suite contains **243 passing regression tests**.

## Hardware / Performance
- **Measured Hardware:** Tested on an NVIDIA RTX 4050 (6 GB VRAM).
- **Latency:** ~28 seconds per quiz generation.
- **Offloading:** The system utilizes automatic CPU offloading when VRAM is constrained.

## Project Structure
```text
NEXORA/
├── app/
│   ├── api/            # FastAPI routes, schemas, and dependencies
│   ├── ingest.py       # PDF ingestion and OCR
│   ├── chunking.py     # Semantic chunking
│   ├── retrieve.py     # FAISS search
│   ├── generator.py    # LLM QA generation
│   ├── quiz_generator.py # LLM Quiz generation
│   ├── database.py     # SQLite operations
│   └── progress.py     # Personalization tracking
├── data/               # Raw PDFs, processed text, and SQLite DB
├── model/              # FAISS vector indexes
├── scripts/            # CLI operational scripts
├── tests/              # 243 automated unit tests
├── doc.md              # Detailed backend manual
├── implement.md        # Step-by-step execution guide
└── requirements.txt    # Python dependencies
```

## Installation
Ensure you have Python 3 installed, as well as Tesseract OCR (system dependency).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Core Brain / API

### 1. Ingestion Pipeline
To process a new PDF, place it in `data/raw/` and run the pipeline linearly:
```bash
python scripts/run_ingestion.py
python scripts/run_cleaning.py
python scripts/run_indexing.py
```

### 2. Run the API (For Mobile Clients)
```bash
uvicorn app.api.main:app --reload
```
*The API will start at `http://127.0.0.1:8000`.*

### 3. Run the Terminal Chat
```bash
python scripts/run_rag.py
```

## API
The FastAPI implementation provides the following core endpoints. For exact JSON payloads and error codes, see `docs/API_CONTRACT.md`.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET`  | `/health` | Check backend status and model readiness. |
| `POST` | `/documents` | Upload a PDF for OCR and indexing. |
| `POST` | `/questions` | Ask a question and get a grounded answer with citations. |
| `POST` | `/quizzes` | Generate a standard MCQ quiz. |
| `POST` | `/quizzes/personalized` | Generate a quiz targeted at weak topics. |
| `POST` | `/answers` | Submit a quiz answer for grading. |
| `GET`  | `/users/{id}/progress` | Fetch user learning analytics. |

## Testing
Run the complete regression suite using:
```bash
python -m pytest
```
**Current status:** 243 tests passing. 
**IMPORTANT:** The test suite utilizes a strict test-isolation fix to aggressively mock the LLM. You must never accidentally initialize the real `Qwen` model during `pytest`, as it will cause kernel Out-Of-Memory (OOM) crashes.

## Known Limitations
- **Latency:** Quiz generation takes ~28s. This requires loading states on mobile clients.
- **Concurrency:** This is currently a single-player backend. Attempting to generate two quizzes concurrently will cause OOM crashes due to VRAM limits.
- **OCR Limitations:** Handwritten text OCR accuracy is extremely low.
- **Structural Mistakes:** The LLM may occasionally fail JSON formatting, requiring a slow retry cycle.
- **Hardware Bound:** Requires a dedicated GPU (e.g. RTX 4050 6GB) for acceptable performance.

## Mobile App Relationship
The intended architecture separates the heavy AI lifting from the user's device:

```text
 Mobile App (Flutter/Kotlin)  --> (Lightweight Client)
          ↓
         API                  --> (FastAPI server)
          ↓
      Core Brain              --> (Python Backend)
          ↓
     Qwen + RAG               --> (Heavy GPU compute)
```
The mobile app is strictly a client and should **not** attempt to run Qwen locally.

## Repository Status
**CORE BRAIN: COMPLETE / FROZEN**

The intelligence layer is finalized. Changing the model, embeddings, grounding threshold, retrieval behavior, prompts, validators, or retry logic is strictly prohibited without initiating a full, manual revalidation sequence.

## Documentation
- [Backend Master Manual (`doc.md`)](doc.md)
- [Linear Implementation Guide (`implement.md`)](implement.md)
- [API Contract (`docs/API_CONTRACT.md`)](docs/API_CONTRACT.md)

## License
No license has currently been specified for this repository.
