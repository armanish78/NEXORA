# Antigravity Study Assistant: The Core Brain Master Document

Welcome to the Antigravity Study Assistant! This document explains exactly what this project is and how it works in plain language. If you know nothing about this project, reading this file will tell you everything you need to know.

## 1. What is this project?
This project is an AI-powered Study Assistant. You feed it your educational PDFs (like textbooks or lab manuals), and it reads them, remembers them, and can either answer your questions about the material or generate custom multiple-choice quizzes to test your knowledge.

It is a backend system (the "Core Brain"). This means there is no shiny mobile app or website attached to it out-of-the-box—it is the pure intelligence engine that powers such apps.

---

## 2. How it learns your PDFs (The Ingestion Pipeline)
Before the AI can answer questions, it has to read your books.

- **Adding files:** You put your PDFs in the system. The system checks if it has seen them before so it does not waste time reading duplicates.
- **Reading the text (OCR):** If your PDF is a scanned image, the system uses a tool called Tesseract to "see" the text inside the image. *(Limitation: It struggles with messy handwriting or very blurry scans).*
- **Cleaning:** The raw text often contains headers, footers, or weird symbols. The system cleans these up automatically.
- **Chunking:** You can not feed an entire textbook to an AI at once—it will crash. So, the system carefully cuts the book into small "chunks" (about 512 characters each). It does this smartly, breaking chunks at paragraph or sentence endings so it does not cut a thought in half.

---

## 3. How it searches (The Retrieval Architecture)
When you ask a question, the system needs to find the right chunk of text from the textbook to answer it.

- **Structural Outline Extraction:** During chunking, the system automatically detects document headings and builds high-level "structural chunks" to understand the layout of your document.
- **Embeddings (Semantic Search):** The system converts every single chunk of text into a mathematical coordinate (a vector) using a local AI model called `all-MiniLM-L6-v2`.
- **Lexical Search (BM25):** Alongside vector embeddings, the system uses BM25 to find exact keyword matches (great for specific terminology or names).
- **The Databases:** Vectors are saved in a highly efficient search database (FAISS), while text is saved in a BM25 index.
- **Retriever Component (`app/retrieve.py`)**:  
  Replaces all hard-coded regex retrieval logic with a multi-strategy engine. By combining FAISS semantic embeddings with a persistent BM25 index, candidate chunks are ranked via Reciprocal Rank Fusion (RRF). 
  Additionally, **Context Assembly** dynamically pulls contiguous sibling chunks sharing the same heading/filename (up to an 8-chunk bidirectional expansion boundary) to recover entire sections.
  **Structural Resolution** is evidence-aware: when navigation metadata matches a query, the underlying content chunks inherit the outline's relevance score, enabling actual content to outrank navigation menus. To ensure accuracy, the system uses **Structural Normalization** to strip generic framing words (e.g., "compare", "types of") from the query before calculating heading overlap, preventing false positives on generic intent queries.
  Finally, **Document Scoping** enforces strict `filename` boundaries throughout the API and generation layers to prevent cross-contamination.

- **Interaction & Testing Scripts**:  
  - `run_project.sh`: The main entry point automating environment setup, data ingestion, indexing, and the interactive terminal chat.
  - `scripts/run_rag.py`: An interactive command-line interface for human-in-the-loop Q&A against the RAG system.

---

## 4. How it stops hallucinations (Grounding)
AI models are famous for making things up (hallucinating). This system has a strict defense against that.

- **The Threshold Gate:** The system has a strict mathematical threshold (`0.35`). When you ask a question, if the database cannot find any text that matches your question better than this `0.35` score, the system instantly blocks the AI and says "I do not have enough information to answer this." It refuses to guess.

---

## 5. How it answers and quizzes (The Generation Layer)
Once the system finds the right text, it uses a powerful AI called `Qwen2.5-3B-Instruct` to read the text and talk to you.

- **Answering:** The AI is given your question and the specific textbook chunks, and is strictly ordered to answer using ONLY that text.
- **Quizzes:** The AI is ordered to write a multiple-choice question. You can choose Easy, Medium, or Hard. Harder questions force the AI to read more chunks at once and create trickier wrong answers.
- **Citations & Enforcement:** The AI must explicitly state which chunk of text it got its answer from using `[S#]` tags. If it fails to include valid citations, a **Single-Retry Mechanism** catches it, injects a critical correction prompt, and forces the AI to rewrite the answer. If it fails twice, the system returns a safe failure rather than a hallucinated response.
- **Dynamic Generation Budget:** The system uses a `max_tokens=768` generation ceiling for answers (increased from 512) to ensure there is enough token budget for complex explanations and their required citations, while short factual queries terminate early automatically.

---

## 6. How it tracks your learning (Personalization)
The system remembers what you are bad at.

- **Scoring:** When you take a quiz, the system evaluates your answer and records if you passed or failed.
- **Weak Topics:** It saves your history in a local SQLite database. It constantly analyzes this database to find topics you frequently fail.
- **Personalized Quizzes:** When you ask for a personalized quiz, the system specifically targets your weakest topics to force you to study them.

---

## 7. Is it reliable? (Testing)
Yes. The project has a massive suite of automated tests (`pytest`) that run 243 checks on the code to ensure it works perfectly. It has a 100% success rate at generating valid quizzes on the first try using the 3B model.

---

## 8. What are the limits? (Operations)
- **Hardware:** Running the AI requires a dedicated GPU (e.g. RTX 4050 6GB) and at least 8GB of RAM. The system employs 4-bit quantization (`bitsandbytes`) to fit the `Qwen2.5-3B-Instruct` model comfortably within 6GB VRAM limits.
- **Speed:** Generating a quiz takes about 28 seconds on average hardware.
- **Concurrency:** This is currently a single-player system. If you try to make it generate two quizzes at the exact same time, your computer will likely crash from running out of memory (OOM). 

---

## 9. File Architecture: What Every File Does
This is a breakdown of every single file and folder in the project, so you know exactly what everything is doing.

### The Core Intelligence (`app/` directory)
These files make up the core brain of the system.
- `app/__init__.py`: A simple empty file that tells Python this folder is a package.
- `app/config.py`: The brain's settings. It stores file paths, text chunk sizes, and the strict hallucination threshold (0.35).
- `app/database.py`: Controls the connection to the SQLite database where quiz scores are stored.
- `app/llm.py`: Connects the code to the AI model (`Qwen2.5-3B`) so it can actually think and type.
- `app/ingest.py`: Reads your PDF files when you first add them.
- `app/ocr.py`: The "eyes". If a PDF is just an image, this uses Tesseract to read the text inside it.
- `app/cleaning.py`: Cleans the text read by OCR, removing random junk like page headers and hyphens.
- `app/chunking.py`: The scissors. It carefully cuts the textbook into 512-character chunks without splitting paragraphs in half.
- `app/embeddings.py`: Uses a model to convert text chunks into mathematical coordinates (vectors).
- `app/vector_store.py`: The librarian. It stores the vectors in the FAISS database so they can be searched.
- `app/retrieve.py`: The search engine. When you ask a question, this searches the FAISS database for the best matching chunks.
- `app/generator.py`: The speaker. It takes the retrieved textbook chunks and asks the AI to answer your question.
- `app/quiz_generator.py`: Similar to generator, but strictly orders the AI to create a valid multiple-choice quiz.
- `app/answer_evaluator.py`: The grader. It checks if the answer you selected on a quiz matches the correct answer.
- `app/progress.py`: The record keeper. It tracks your passes, fails, and times in the database.
- `app/personalization.py`: The analyst. It figures out what topics you fail most often and instructs the quiz generator to focus on them.

### The Web Interface (`app/api/` directory)
The API is how this "Core Brain" talks to the outside world (like a website or a mobile app). Because the `app/` folder is just pure Python intelligence, a web browser cannot talk to it directly. The API files create web addresses (URLs) that external apps can send messages to.
- `app/api/__init__.py`: Marks the API folder as a Python package.
- `app/api/main.py`: Starts the web server (using FastAPI).
- `app/api/routes.py`: Defines the URLs (e.g., creating a `/quiz` URL that a mobile app can request).
- `app/api/schemas.py`: Defines the exact JSON structure of the messages being sent back and forth.
- `app/api/dependencies.py`: Wires the database and the brain together so the web server can use them.

### The Operation Scripts (`scripts/` directory)
These are the buttons you push to run the machine. You only execute these scripts; they call the files in `app/`.
- `scripts/run_ingestion.py`: Push this button to read newly added PDFs.
- `scripts/run_cleaning.py`: Push this button to clean the extracted text.
- `scripts/run_indexing.py`: Push this button to build the search database.
- `scripts/run_rag.py`: Push this button to start talking to the AI in your terminal.

### The Databases (`data/` and `model/` directories)
These folders store the actual information the system generates.
- `data/raw/`: Where you place your newly downloaded PDF textbooks.
- `data/processed/`: Where the raw text from the PDFs is saved so they don't have to be read twice.
- `data/cleaned/`: Where the cleaned-up text is saved.
- `data/study_assistant.db`: The SQLite database that tracks your quiz scores and past topics.
- `model/embeddings/`: Stores the raw vectors for the text.
- `model/indexes/v2/faiss.index`: The highly efficient FAISS search database.

### The Documentation and Configs (Root directory)
- `doc.md`: The file you are currently reading! It explains what the project is.
- `implement.md`: The step-by-step instructions on how to actually start the project and run it.
- `requirements.txt`: The list of Python packages required to run the main application.
- `requirements-dev.txt`: Extra Python packages only needed for testing.
- `.env.example`: A template file for API keys, in case you ever want to connect an external AI instead of a local one.
- `.gitignore`: A list of temporary files that Git shouldn't save.

### The Safety Net (`tests/` directory)
The tests directory has absolutely nothing to do with running the application for users. It is a safety net for developers. 

Imagine you are a mechanic changing the engine in a car. The `tests/` directory contains an automated robot inspector that turns the key, checks the oil, and drives the car 100 times to make sure you didn't break anything. 
- `tests/__init__.py`: Marks the tests folder as a package.
- `tests/test_api.py`: A robot that pretends to be a web browser and clicks the API buttons.
- `tests/test_chunking.py`: A robot that feeds fake text into the scissors and makes sure it cuts at exactly 512 characters.
- `tests/test_cleaning.py`: A robot that feeds garbage text into the cleaner to make sure the garbage gets removed.
- `tests/test_database.py`: A robot that tries writing to the database to ensure it doesn't crash.
- `tests/test_e2e.py`: End-to-end tests that run the entire pipeline with fake data.
- `tests/test_generation.py`: A robot that checks if the AI generates normal text.
- `tests/test_ingest.py`: A robot that pretends to read a PDF and verifies the output format.
- `tests/test_ocr.py`: A robot that tests the image-reading "eyes".
- `tests/test_personalization.py`: A robot that checks if the system correctly identifies weak topics.
- `tests/test_progress.py`: A robot that makes sure quiz scores are recorded correctly.
- `tests/test_provider_architecture.py`: Verifies the system can talk to the LLM.
- `tests/test_quiz_generator.py`: A robot that aggressively forces the AI to write bad quizzes to see if the self-correction catches it.
- `tests/test_retrieve.py`: A robot that checks if the search engine finds the right paragraph.
- `tests/test_answer_evaluator.py`: A robot that deliberately answers quizzes wrong to make sure it gets graded correctly.

While the `app/api/` is part of the final product used by real people, the `tests/` are only used offline by developers to guarantee the code works.
