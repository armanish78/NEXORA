# NEXORA — Neural Knowledge Retrieval & Reasoning Engine

## What is NEXORA?
NEXORA is a file-based, provider-agnostic Study Assistant backend system (the "Core Brain"). It solves the problem of hallucination in educational AI by ingesting textbooks, manuals, and notes, and tightly coupling a Large Language Model to that specific material. It does not act as a general chatbot; instead, it acts as a highly disciplined tutor that refuses to answer questions outside the scope of the provided materials.

## What it can do

### Mobile/Desktop App Features (Frontend)
- **Interactive Study Sessions:** Chat dynamically with the AI about specific documents via a beautiful, clean messaging interface.
- **Customized Quizzes:** Set up and take interactive multiple-choice quizzes with rich UI feedback and instantaneous grading.
- **Progress Tracking & Analytics:** Visualize your learning journey with dynamic progress rings, detailed stats, and historical performance tracking.
- **Smart Weakness Targeting:** The app's dashboard highlights topics that "Need Attention" and lets you instantly launch personalized quizzes focused on your specific weaknesses.
- **Document Library:** Clean UI to manage, view, and select your uploaded study materials.
- **Cross-Platform:** Built in Flutter, providing a native, beautiful experience across Mobile, Desktop (Linux/Windows/macOS), and Web.

### Core Brain Intelligence (Backend)
- **Read Educational PDFs:** Extracts text from both digital PDFs and scanned images (via OCR).
- **Zero Hallucinations (Strict Grounding):** Employs a strict mathematical threshold to instantly refuse questions if the required information isn't found in the text.
- **Dynamic Content Generation:** Creates Easy, Medium, and Hard multiple-choice quizzes directly from textbook material on the fly.
- **Deterministic Evaluation:** Automatically grades answers and logs pass/fail metrics into a SQLite database to power the frontend analytics.

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
- **Quantization:** Uses `bitsandbytes` 4-bit (`nf4`) quantization to fit the 3B parameter model completely within a 6GB VRAM limit without CPU offloading.
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
├── backend/            # Core Brain Python Backend
│   ├── app/            # FastAPI, RAG, Chunking, LLM generation
│   ├── data/           # Raw PDFs, processed text, and SQLite DB
│   ├── model/          # FAISS vector indexes
│   ├── scripts/        # CLI operational scripts
│   ├── tests/          # Automated unit tests
│   ├── docs/           # Detailed backend manuals
│   └── requirements.txt
├── frontend/           # User-Facing Mobile/Desktop App
│   └── nexora_app/     # Full Flutter application implementation
└── README.md
```

## Installation
Ensure you have Python 3 installed, as well as Tesseract OCR for the backend, and the Flutter SDK for the frontend.

### Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend/nexora_app
flutter pub get
```

## Running the System

### 1. Ingestion Pipeline (Backend)
To process a new PDF, place it in `backend/data/raw/` and run the pipeline linearly from the `backend/` directory:
```bash
cd backend
python scripts/run_ingestion.py
python scripts/run_cleaning.py
python scripts/run_indexing.py
```

### 2. Run the Core Brain API (Backend)
Start the FastAPI server to serve the frontend:
```bash
cd backend
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

### 3. Run the Mobile/Desktop App (Frontend)
With the backend API running, launch the Flutter application:
```bash
cd frontend/nexora_app
flutter run
```

## API
The FastAPI implementation provides the following core endpoints. For exact JSON payloads and error codes, see `backend/docs/API_CONTRACT.md`.

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
Run the complete regression suite for the backend using:
```bash
cd backend
python -m pytest
```
**IMPORTANT:** The test suite utilizes a strict test-isolation fix to aggressively mock the LLM. You must never accidentally initialize the real `Qwen` model during `pytest`, as it will cause kernel Out-Of-Memory (OOM) crashes.

## Known Limitations
- **Latency:** Quiz generation takes ~28s. This requires loading states on mobile clients.
- **Concurrency:** This is currently a single-player backend. Attempting to generate two quizzes concurrently will cause OOM crashes due to VRAM limits.
- **OCR Limitations:** Handwritten text OCR accuracy is extremely low.
- **Structural Mistakes:** The LLM may occasionally fail JSON formatting, requiring a slow retry cycle.
- **Hardware Bound:** Requires a dedicated GPU (e.g. RTX 4050 6GB) for acceptable performance.

## Mobile App Relationship & Repository Status
The project architecture successfully separates the heavy AI lifting from the user's device:

```text
 Mobile App (Flutter)         --> (Lightweight Cross-Platform UI)
          ↓
         API                  --> (FastAPI server)
          ↓
      Core Brain              --> (Python Backend)
          ↓
     Qwen + RAG               --> (Heavy GPU compute / 4-bit)
```

**REPOSITORY STATUS: FULLY INTEGRATED & OPERATIONAL**

- **Frontend (Flutter):** Fully developed and actively communicating with the backend. It dynamically fetches topics, renders study material, handles quiz sessions, and displays real-time progress.
- **Backend (Python):** Complete and frozen. The 4-bit quantized `Qwen2.5-3B-Instruct` model successfully runs locally on a 6GB VRAM GPU without memory leaks.

## Documentation
- [Backend Master Manual (`backend/docs/doc.md`)](backend/docs/doc.md)
- [Linear Implementation Guide (`backend/docs/implement.md`)](backend/docs/implement.md)
- [API Contract (`backend/docs/API_CONTRACT.md`)](backend/docs/API_CONTRACT.md)

## License
No license has currently been specified for this repository.
