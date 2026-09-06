# NEXORA

## Neural Knowledge Retrieval & Reasoning Engine

NEXORA is a **file-grounded AI Study Assistant** designed to help students learn directly from their own study material.

Instead of behaving like a general-purpose chatbot, NEXORA is built around a strict principle:

> **The AI should answer from the user's study material, not from whatever it happens to know.**

The system combines a local Retrieval-Augmented Generation (RAG) pipeline with a Flutter application to provide grounded question answering, quiz generation, answer evaluation, and personalized learning.

---

## Project Status

> **Current Stage: Flutter Application Development**

The NEXORA **Core Brain** has been developed around a local RAG pipeline using document ingestion, semantic chunking, embeddings, FAISS retrieval, grounding validation, and the Qwen LLM.

The project is now moving through the **Flutter application development phase**, where the intelligence layer is being connected to a polished cross-platform user experience.

### Current architecture

```text
                    NEXORA
                       │
          ┌────────────┴────────────┐
          │                         │
     Flutter App               Core Brain
     (Frontend)                 (Backend)
          │                         │
          │                      Python
          │                      FastAPI
          │                         │
          │                    RAG Pipeline
          │                         │
          │                  FAISS + Embeddings
          │                         │
          │                    Qwen 2.5 3B
          │                         │
          └────────────── API ───────┘
```

The heavy AI workload runs on the backend rather than on the user's mobile device.

---

# What is NEXORA?

NEXORA is a personalized study environment built around the user's own educational material.

A typical workflow is:

```text
Study Material
     ↓
PDF / Document Ingestion
     ↓
Text Extraction / OCR
     ↓
Text Cleaning
     ↓
Semantic Chunking
     ↓
Embeddings
     ↓
FAISS Vector Index
     ↓
Relevant Context Retrieval
     ↓
Grounding Gate
     ↓
Qwen LLM
     ↓
Grounded Answer / Quiz
     ↓
Evaluation
     ↓
Learning Progress
```

The Flutter application provides the user-facing experience while the backend handles the computationally expensive intelligence layer.

---

# Core Features

## 📚 Material-Based Learning

NEXORA works with the user's own educational material rather than relying on unrestricted general knowledge.

Supported material processing includes:

* Digital PDFs
* Scanned PDFs
* Image-based material
* OCR extraction
* Text cleaning
* Semantic chunking
* Vector indexing

---

## 🧠 Grounded Question Answering

Users can ask questions about their uploaded material.

The system:

1. Converts the material into searchable semantic chunks.
2. Retrieves the most relevant chunks.
3. Checks whether sufficient context exists.
4. Passes grounded context to the LLM.
5. Generates an answer constrained by the retrieved material.
6. Returns source references alongside the answer.

If the required information cannot be sufficiently supported by the material, NEXORA refuses to answer instead of guessing.

```text
Question
   ↓
Semantic Retrieval
   ↓
Relevance Check
   ↓
Grounding Gate
   │
   ├── Insufficient → Refuse
   │
   └── Sufficient
          ↓
        Qwen
          ↓
   Grounded Answer
          ↓
       Sources
```

---

# 🔒 Grounding & Hallucination Control

One of the main design goals of NEXORA is reducing hallucination in educational use cases.

The retrieval system uses a calibrated relevance threshold.

Current grounding threshold:

```text
0.35
```

If the retrieved context does not meet the required relevance threshold, the request is rejected with:

```text
INSUFFICIENT_SOURCE_CONTEXT
```

This prevents the system from unnecessarily invoking the LLM when the available material does not contain sufficient evidence.

The LLM is therefore not treated as the source of truth.

The **study material is the source of truth**.

---

# 📝 Quiz Generation

NEXORA can generate multiple-choice quizzes from the user's study material.

### Difficulty Levels

| Difficulty | Context Requirement |
| ---------- | ------------------- |
| Easy       | 1 relevant chunk    |
| Medium     | 2 relevant chunks   |
| Hard       | 4 relevant chunks   |

Each question contains:

* Question
* Four answer options
* One correct answer
* Explanation
* Source chunk references

The generation pipeline uses structured JSON validation to ensure the model output conforms to the expected format.

---

# 🎯 Answer Evaluation

Quiz answers are evaluated deterministically.

The system does not ask the LLM whether the user was correct.

Instead:

```text
User Selection
      ↓
Correct Option
      ↓
Deterministic Comparison
      ↓
Correct / Incorrect
```

This makes answer evaluation predictable and independent of model variability.

---

# 📈 Learning Progress

NEXORA tracks quiz performance using the backend state database.

The system records information such as:

* Quiz attempts
* Correct answers
* Incorrect answers
* Pass/fail outcomes
* Topic performance

This information is then used by the personalization system.

---

# 🎯 Personalized Learning

NEXORA can identify areas where the learner is struggling.

The personalization pipeline analyzes previous performance and identifies weak topics.

A personalized quiz can then be generated around those topics.

```text
Quiz Attempts
     ↓
Performance Data
     ↓
Weak Topic Detection
     ↓
Personalized Context
     ↓
Targeted Quiz
```

The goal is to move beyond simply generating questions and instead create a feedback loop for learning.

---

# 🏗️ Architecture

NEXORA is divided into two major systems.

## 1. Flutter Application

The Flutter application is the user-facing layer.

It is responsible for:

* Navigation
* Study material management
* User interaction
* Question and answer interfaces
* Quiz interfaces
* Progress visualization
* Communication with the backend API

The application is being developed with a focus on a clean, modern study-oriented experience.

---

## 2. Core Brain

The Core Brain is the computational intelligence layer.

It is responsible for:

* Document ingestion
* OCR
* Text cleaning
* Semantic chunking
* Embeddings
* Vector search
* Retrieval
* Context expansion
* Grounding
* LLM generation
* Quiz generation
* Answer evaluation
* Progress tracking
* Personalization

---

# Core Brain Architecture

```text
PDF / Image
     ↓
Ingestion
     ↓
OCR
     ↓
Cleaning
     ↓
Semantic Chunking
     ↓
all-MiniLM-L6-v2
     ↓
FAISS
     ↓
Retrieval
     ↓
Adjacent Chunk Expansion
     ↓
Grounding Gate
     ↓
Qwen2.5-3B-Instruct
     ↓
 ┌───────────────┬────────────────┐
 │               │                │
 QA          Quiz Generation   Personalization
 │               │                │
 └───────────────┴────────────────┘
                 ↓
          Deterministic Evaluation
                 ↓
              Progress
```

---

# Technology Stack

## Frontend

* **Framework:** Flutter
* **Language:** Dart
* **State Management:** Riverpod
* **UI:** Material 3
* **Platform:** Cross-platform

---

## Backend

* **Language:** Python
* **API:** FastAPI
* **Database:** SQLite
* **Vector Search:** FAISS
* **Embeddings:** `all-MiniLM-L6-v2`
* **LLM:** `Qwen/Qwen2.5-3B-Instruct`

---

## Document Processing

* **PDF Processing:** PyMuPDF
* **OCR:** PyTesseract
* **Text Processing:** Custom cleaning and semantic chunking pipeline

---

## Model Execution

The Qwen model runs locally on the backend.

The Flutter application does **not** run the 3B parameter model directly on the user's device.

```text
Flutter Device
      │
      │ HTTP
      ↓
FastAPI Backend
      │
      ↓
RAG Pipeline
      │
      ↓
Qwen 2.5 3B
      │
      ↓
Grounded Response
      │
      ↓
Flutter Device
```

---

# Model

NEXORA currently uses:

```text
Qwen/Qwen2.5-3B-Instruct
```

The model was selected after validation against structured generation requirements.

### Configuration

* 4-bit quantization
* `bitsandbytes`
* `nf4`
* Automatic device mapping
* Local backend execution

The model is designed to run within a constrained GPU environment rather than requiring a large cloud inference service.

---

# Performance

The Core Brain has been tested on:

```text
GPU: NVIDIA RTX 4050
VRAM: 6 GB
```

Approximate quiz generation latency:

```text
~28 seconds
```

Because generation is computationally expensive, the Flutter application is designed around asynchronous requests and appropriate loading states.

---

# Repository Structure

```text
NEXORA/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── ingest.py
│   │   ├── ocr.py
│   │   ├── cleaning.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retrieve.py
│   │   ├── generator.py
│   │   ├── quiz_generator.py
│   │   ├── answer_evaluator.py
│   │   ├── progress.py
│   │   └── personalization.py
│   │
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   │
│   ├── model/
│   │
│   ├── scripts/
│   │
│   ├── tests/
│   │
│   ├── docs/
│   │
│   └── requirements.txt
│
├── frontend/
│   └── nexora_app/
│       ├── lib/
│       ├── assets/
│       ├── test/
│       └── pubspec.yaml
│
└── README.md
```

---

# Flutter Application

The Flutter application is currently under active development.

Its purpose is to turn the Core Brain capabilities into a complete study experience.

The application is being developed around several major areas:

```text
Home
  ↓
Library
  ↓
Study Material
  ↓
Ask / Learn
  ↓
Quiz
  ↓
Results
  ↓
Progress
```

The frontend communicates with the Core Brain through the FastAPI backend.

---

# Frontend Development Principles

The Flutter application follows several principles:

### Clean Separation

UI logic should remain separate from backend communication and data processing.

### Reactive State

Riverpod is used for application state and asynchronous backend data.

### Material 3

The application uses Material 3 components and a consistent design system.

### Study-First UX

The interface should prioritize:

* Reading
* Understanding
* Asking questions
* Practicing
* Reviewing mistakes
* Tracking progress

### Backend Intelligence

Heavy AI processing remains on the backend.

The Flutter application should remain lightweight.

---

# API

The FastAPI backend exposes the Core Brain through REST endpoints.

| Method | Endpoint                | Purpose                           |
| ------ | ----------------------- | --------------------------------- |
| GET    | `/health`               | Backend health and readiness      |
| POST   | `/documents`            | Upload and process study material |
| POST   | `/questions`            | Ask a grounded question           |
| POST   | `/quizzes`              | Generate a quiz                   |
| POST   | `/quizzes/personalized` | Generate a personalized quiz      |
| POST   | `/answers`              | Evaluate a quiz answer            |
| GET    | `/users/{id}/progress`  | Retrieve learning progress        |

The complete API contract is maintained separately in:

```text
backend/docs/API_CONTRACT.md
```

---

# Installation

## Requirements

You will need:

* Python 3
* Flutter SDK
* Tesseract OCR
* NVIDIA GPU recommended for local Qwen inference

---

## Backend Setup

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Frontend Setup

```bash
cd frontend/nexora_app

flutter pub get
```

---

# Running NEXORA

## 1. Prepare Study Material

Place the source material inside:

```text
backend/data/raw/
```

Run the ingestion pipeline:

```bash
cd backend

python scripts/run_ingestion.py
python scripts/run_cleaning.py
python scripts/run_indexing.py
```

---

## 2. Start the Backend

```bash
cd backend

uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

The backend will expose the API on port `8000`.

---

## 3. Start the Flutter Application

```bash
cd frontend/nexora_app

flutter run
```

For Flutter Web:

```bash
flutter run -d chrome
```

---

# Testing

The backend contains an automated regression suite.

Run:

```bash
cd backend
python -m pytest
```

The test suite is designed to prevent accidental initialization of the real Qwen model during testing.

This is important because loading the model unnecessarily during tests can consume significant GPU memory.

---

# Validation

The Core Brain has been validated against educational PDFs and handwritten study material.

Current validation includes:

* Grounded question answering
* Out-of-context refusal
* Quiz generation
* JSON validation
* Retry handling
* Deterministic answer evaluation
* Progress tracking
* Personalization logic

The backend regression suite currently contains:

```text
243 passing tests
```

---

# Known Limitations

NEXORA is still under active development.

### LLM Latency

Quiz generation can take approximately:

```text
~28 seconds
```

depending on hardware and workload.

### Hardware Requirements

Local Qwen inference benefits from a dedicated NVIDIA GPU.

The current tested configuration is:

```text
RTX 4050 — 6 GB VRAM
```

### OCR

OCR quality can degrade significantly with handwritten or low-quality source material.

### Model Output

Although structured output validation is implemented, the LLM can occasionally produce invalid structures or incorrect source identifiers.

A validation and retry mechanism is therefore used.

### Concurrency

The current local model setup is not intended for heavy concurrent inference.

Multiple simultaneous generation requests may exceed available VRAM.

### Frontend

The Flutter application is actively being developed and should not yet be considered a finished production application.

---

#

---

# Development Philosophy

NEXORA is intentionally not designed as another generic AI chatbot.

The core philosophy is:

```text
User Material
     ↓
Reliable Retrieval
     ↓
Evidence
     ↓
Grounded Reasoning
     ↓
Useful Learning
```

The LLM is a reasoning and generation component.

It is not the knowledge database.

This distinction is fundamental to the architecture.

---

# Future Direction

Potential future improvements include:

* Better multimodal document understanding
* Improved handwriting OCR
* More advanced retrieval strategies
* Better chunking algorithms
* Additional study modes
* Spaced repetition
* Flashcards
* More detailed learning analytics
* Improved personalization
* More efficient local inference
* Expanded document support

These features are intentionally secondary to establishing a reliable Core Brain and a solid Flutter study experience.

---

# Documentation

Detailed backend documentation is available in:

```text
backend/docs/
```

Important documents include:

```text
backend/docs/doc.md
backend/docs/implement.md
backend/docs/API_CONTRACT.md
```

---

# Project Goal

NEXORA aims to become a study environment where students can bring their own material and interact with it through an AI system that is:

* **Grounded**
* **Traceable**
* **Personalized**
* **Deterministic where appropriate**
* **Local-first for model inference**
* **Cross-platform**
* **Focused on actual learning rather than generic conversation**

---

# License

No license has currently been specified for this repository.
