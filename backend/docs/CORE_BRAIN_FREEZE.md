# CORE BRAIN FREEZE

## 1. Final Architecture
The final architecture represents a provider-agnostic Retrieval-Augmented Generation (RAG) study assistant. It is strictly limited to core backend ingestion, chunking, retrieval, LLM interaction, quiz generation, grading, and personalization logic.

## 2. Every Module and its Responsibility
- **`app/main.py` & `app/config.py`**: Configuration, environment management, and high-level integrations.
- **`app/chunking.py`**: Handles semantic chunking of text to preserve logical boundaries (implementing `CHUNK_OVERLAP = 0` with adjacent chunk expansion).
- **`app/cleaning.py` & `app/preprocessing.py`**: Optical character recognition (OCR) cleaning and artifact removal.
- **`app/database.py`**: SQLite database layer for progress tracking, state management, and personalized history.
- **`app/llm.py`**: Provider-agnostic LLM interface (supporting Local HuggingFace, OpenAI, etc.) and model loading (with auto device maps).
- **`app/retrieve.py` & `app/reranker.py`**: Hybrid retrieval (BM25 + Semantic Search), utilizing adjacent chunk expansion.
- **`app/quiz_generator.py` & `app/generation.py`**: Logic for prompting LLMs to create structured MCQs with distinct difficulty and personalization.
- **`app/evaluator.py` & `app/answer_evaluator.py`**: Deterministic evaluation of answers and quiz correctness validation.
- **`app/progress.py` & `app/personalization.py`**: Tracking user performance and generating personalized knowledge gaps to target.

## 3. Complete Data Flow (PDF -> Answer/Quiz)
1. **Ingestion**: PDFs/text are read and cleaned (`cleaning.py`/`preprocessing.py`).
2. **Chunking**: Text is split at semantic boundaries (`CHUNK_OVERLAP = 0`).
3. **Indexing**: Chunks are embedded and indexed (Vector + BM25).
4. **Retrieval**: User queries trigger hybrid retrieval, yielding top chunks. Adjacent chunk expansion provides missing context.
5. **Generation**: The `quiz_generator` or QA logic uses the `LLMProvider` with the retrieved context to strictly output a factual JSON response or quiz.

## 4. Complete Data Flow (Quiz Answer -> Progress -> Personalization)
1. **Evaluation**: User answers are deterministically verified (`answer_evaluator.py`).
2. **Tracking**: The result (pass/fail, latency) is stored in the local SQLite DB (`database.py`, `progress.py`).
3. **Personalization**: Historical performance creates a knowledge gap profile.
4. **Next Quiz**: Future quiz generation uses the weak topic history to adjust prompts (`personalization.py`).

## 5. LLM/Provider Architecture
- Uses a `Provider` interface allowing swapability.
- Default Provisioned: `Qwen/Qwen2.5-3B-Instruct` (or `0.5B` fallback).
- Loads via PyTorch `device_map="auto"` utilizing GPU (`cuda` if available) with CPU offloading for large models/constrained VRAM.

## 6. Retrieval and Grounding Architecture
- **Hybrid Retrieval**: BM25 keyword matching + Dense embeddings.
- **Grounding**: Strict refusal logic ensures out-of-corpus queries are rejected. S-tag (Source Tags) tracking tracks provenance.
- **Chunk Setup**: Verified that `CHUNK_OVERLAP=0` is the active setting, relying on adjacent chunk expansion to prevent context tearing.

## 7. Difficulty Architecture
- Supported Difficulties: Easy, Medium, Hard.
- Modifies constraints for distractors, semantic similarity of options, and depth of reasoning in the generation prompt.

## 8. Database Architecture
- SQLite-based for lightweight offline support. Tracks chunk processing hashes, test histories, and personalization vectors.

## 9. Real-Model Validation Results
- Model tested: `Qwen/Qwen2.5-3B-Instruct`.
- Loads onto GPU with `device_map="auto"` with VRAM constraint awareness.
- **Observations**: Smoke tests reveal 3B struggles with strict schema adherence (e.g. dropping `source_chunk_ids`) requiring 2-3 retries for passing output. Grounded factual correctness and refusal of out-of-corpus hallucination traps remain strong.

## 10. Test Results
- **Test Count**: 234 tests run.
- **Result**: 234 passed. 0 errors, 0 failures, 0 regressions.

## 11. Known Limitations
- Small Parameter Local LLMs (`Qwen2.5-3B` and below) often fail to strictly follow structural constraints (S-tags, JSON keys), leading to retries and schema validation failures.
- No conversational memory beyond explicit quiz tracking.

## 12. Known Technical Debt
- Strict prompt format may need future decomposition to better support small parameter local models (SLMs).
- `CHUNK_OVERLAP=0` adjacent chunk expansion can theoretically double context windows linearly, slowing small local inference times.

## 13. Intentionally Deferred (API/Mobile Stage)
- FastAPI / REST API wrapping.
- Mobile application / UI.
- Authentication & Multi-user isolation.
- Cloud deployment & Asynchronous task infrastructure (Celery/Redis).
- Advanced Cloud LLM integration.

## 14. PROVEN vs NOT YET PROVEN
- **PROVEN**: Ingestion, BM25+Dense retrieval, deterministic schema validation, deterministic progress tracking, strict refusal (hallucination prevention), offline PyTest framework.
- **NOT YET PROVEN**: Consistent single-shot schema adherence by small local models, production-scale concurrent processing, mobile device battery impact for local retrieval.
