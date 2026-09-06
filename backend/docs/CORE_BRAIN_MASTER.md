# NEXORA CORE BRAIN: MASTER DOCUMENT

This is the definitive, authoritative documentation for the completed and frozen NEXORA Core Brain. It consolidates the historical design constraints, the final validated state of the system, the data flow, and the API surface.

---

## 1. Final Architecture vs. Historical Architecture

The system evolved significantly from its initial freeze state to its final validated state.

### Final Validated State (Current)
- **Retrieval Engine:** Pure FAISS semantic search using `all-MiniLM-L6-v2`.
- **API Surface:** FastAPI is fully implemented (`app/api/`) providing REST endpoints for mobile clients.
- **Model:** `Qwen2.5-3B-Instruct` running strictly on the backend with automatic GPU device placement.
- **Testing:** 243 passing regression tests.

### Historical State (From Initial Freeze)
- **Retrieval Engine:** Originally utilized a hybrid BM25 + Semantic Search with reranking. ( *Historical Note:* BM25, reranker, and preprocessing modules were purged during final optimization as they added complexity without measurable performance gains on the target dataset).
- **API Surface:** Originally deferred to a later stage.
- **Testing:** Originally 234 tests.

---

## 2. Complete Data Flow

The Core Brain processes documents and generates knowledge through two primary flows:

### A. Ingestion Flow (PDF -> Vector DB)
1. **Ingestion & OCR:** PDFs are parsed and images are read via PyTesseract (`app/ingest.py`, `app/ocr.py`).
2. **Cleaning:** Raw text is stripped of OCR artifacts and formatting junk (`app/cleaning.py`).
3. **Chunking:** Text is sliced into ~512-character chunks. The system explicitly uses `CHUNK_OVERLAP=0` but breaks at semantic boundaries (paragraphs) to prevent thought fracturing (`app/chunking.py`).
4. **Embedding:** Chunks are vectorized using `all-MiniLM-L6-v2` (`app/embeddings.py`).
5. **Indexing:** Vectors are stored in an offline FAISS index (`app/vector_store.py`).

### B. Generation Flow (User Query -> Answer/Quiz)
1. **Retrieval:** The query is embedded, and FAISS fetches the top-K chunks.
2. **Context Expansion:** The system silently grabs adjacent chunks to prevent context tearing (`app/retrieve.py`).
3. **Grounding Gate:** The system strictly enforces a similarity threshold of `0.35`. If no retrieved chunk meets this score, the LLM is bypassed, and the system instantly returns an `INSUFFICIENT_SOURCE_CONTEXT` refusal.
4. **Generation:** `Qwen2.5-3B-Instruct` is prompted with strict JSON schemas to output either a QA response or a Quiz (Easy/Medium/Hard) (`app/generator.py`, `app/quiz_generator.py`).

### C. Personalization Flow
1. **Evaluation:** Selected quiz options are deterministically compared against the generated correct answer (`app/answer_evaluator.py`).
2. **Tracking:** Pass/fail data is logged in a local SQLite database (`app/progress.py`).
3. **Gap Detection:** The system analyzes history to find the user's weakest topics, allowing for targeted personalized quiz generation (`app/personalization.py`).

---

## 3. Real-Model Validation Results

The Core Brain underwent rigorous validation with the `Qwen2.5-3B-Instruct` model against real educational PDFs.

- **Schema Adherence & Validation:** Small models like `Qwen2.5-3B` occasionally produce structural/schema mistakes (e.g., `source_chunk_id` hallucinations or missing fields). The system relies on a strict validator and retry mechanism to catch these failures. During real-file validation, the model achieved **14/15 first-attempt quiz successes**, with the remaining quiz succeeding after an automated retry. The system is therefore highly reliable with its validation/retry protection in place, even if the model itself is not perfectly schema-adherent.
- **Grounding Validation:** The system successfully demonstrated absolute refusal to answer out-of-corpus hallucination traps.
- **Performance:** End-to-end quiz generation averages ~28 seconds on an RTX 4050 (6GB VRAM) using auto device-mapping.
- **Regression Suite:** 243/243 tests passing with 0 failures. (Note: Tests utilize strict LLM mocking to prevent accidental OOM crashes during CI/CD).

---

## 4. API Contract Summary

The FastAPI implementation exposes the core intelligence to external clients (e.g., Flutter/Kotlin apps).
*(For the exact JSON payloads, refer to `docs/API_CONTRACT.md`)*

- `GET /health`: System status and loaded model.
- `POST /documents`: Synchronous PDF ingestion and indexing.
- `POST /questions`: Grounded QA generation.
- `POST /quizzes`: Standard MCQ generation.
- `POST /quizzes/personalized`: Weak-topic targeted MCQ generation.
- `POST /answers`: Deterministic answer grading.
- `GET /users/{id}/*`: Progress and analytic tracking endpoints.

---

## 5. Known Limitations & Technical Debt

- **Concurrency:** The system is single-player by design. Concurrent generation requests will cause Out-Of-Memory (OOM) crashes on standard consumer GPUs.
- **Latency:** ~28s generation times require asynchronous loading states on client applications.
- **Context Expansion Cost:** Relying on adjacent chunk expansion instead of chunk overlap can theoretically bloat the context window during retrieval, slowing inference.

---
**STATUS: FROZEN.** Any modifications to prompts, models, embeddings, or retrieval thresholds require a full manual revalidation sequence.
