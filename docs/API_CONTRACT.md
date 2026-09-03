# Antigravity Study Assistant API Contract

This document provides the exact specifications for the Antigravity Study Assistant REST API. It is written specifically for Flutter, Kotlin, and other frontend developers integrating with the Core Brain backend. 

The API is built using FastAPI. By default, it runs on `http://127.0.0.1:8000`.

---

## General Concepts

### User ID (`user_id`)
Most endpoints require a `user_id`. In this system, `user_id` is passed simply as an **integer** in the JSON body or URL path (e.g., `123`). There is no complex authentication (JWT/OAuth) implemented in the Core Brain. Your mobile app can simply generate a local integer ID for the user and pass it.

### File Uploads
Files are uploaded as `multipart/form-data`. The system accepts `.pdf`, `.jpg`, `.jpeg`, and `.png`. Text extraction, OCR, and indexing happen synchronously during the upload.

### Grounding Refusal (Hallucination Prevention)
If the user asks a question or requests a quiz about a topic that does NOT exist in the uploaded documents, the AI will refuse to generate it. This is represented by:
```json
{
  "success": false,
  "reason": "INSUFFICIENT_SOURCE_CONTEXT"
}
```
**Mobile App Handling:** If your app receives `success: false`, it should display the `reason` to the user and prompt them to upload relevant documents.

### Quiz Difficulty
Allowed difficulty values are exactly `"easy"`, `"medium"`, and `"hard"`.

---

## 1. System Health

### `GET /health`
**Purpose:** Check if the backend is running and which AI model is loaded.
**Request:** None
**Response:**
```json
{
  "status": "ok",
  "model": "Qwen2.5-3B-Instruct"
}
```

---

## 2. Ingestion

### `POST /documents`
**Purpose:** Upload a PDF or image, extract its text, chunk it, and add it to the search database.
**HTTP Form Data:** `file` (UploadFile, required)
**Response (Success 200):**
```json
{
  "success": true,
  "filename": "textbook.pdf",
  "pages": 42,
  "chunks_created": 150
}
```
**Errors:**
- `400 Bad Request`: "Unsupported file type"
- `400 Bad Request`: "Failed to ingest or extract text"

---

## 3. Q&A Generation

### `POST /questions`
**Purpose:** Ask a question and get a grounded answer with citations.
**Request JSON:**
```json
{
  "query": "What is generative AI?",
  "top_k": 5,
  "filename": "textbook.pdf"
}
```
*Note: `top_k` is optional and defaults to 5. `filename` is optional but HIGHLY RECOMMENDED. When `filename` is supplied, retrieval is strictly scoped to that document only.*

**Response (Success 200):**
```json
{
  "success": true,
  "answer": "Generative AI refers to algorithms that can create new content... [S1]",
  "citations": [
    {"chunk_id": "S1", "text": "Generative AI is..."}
  ],
  "retrieved_chunks": [
    {"id": "S1", "text": "Generative AI is...", "score": 0.82}
  ]
}
```
**Response (Refusal 200):**
```json
{
  "success": false,
  "reason": "INSUFFICIENT_SOURCE_CONTEXT"
}
```

---

## 4. Quiz Generation

### `POST /quizzes`
**Purpose:** Generate a multiple-choice quiz on a specific topic.
**Request JSON:**
```json
{
  "user_id": 1,
  "topic": "Machine Learning",
  "difficulty": "medium",
  "num_questions": 3
}
```
*Note: `difficulty` defaults to "medium" if omitted. `num_questions` must be between 1 and 5 (defaults to 1).*

**Response (Success 200):**
```json
{
  "success": true,
  "quiz_id": 42,
  "questions": [
    {
      "id": 101,
      "text": "What does a neural network do?",
      "options": ["Predicts patterns", "Cooks food", "Drives cars"],
      "type": "MCQ"
    }
  ],
  "reason": null
}
```

### `POST /quizzes/personalized`
**Purpose:** Generate a quiz targeted at the user's weakest topic (calculated automatically by the backend).
**Request JSON:**
```json
{
  "user_id": 1,
  "difficulty": "hard",
  "num_questions": 2
}
```
**Response:** Same structure as `/quizzes`.

---

## 5. Grading

### `POST /answers`
**Purpose:** Submit a user's selected option for grading.
**Request JSON:**
```json
{
  "question_id": 101,
  "user_answer": "Predicts patterns"
}
```
**Response (Success 200):**
```json
{
  "is_correct": true,
  "explanation": "Neural networks are designed to recognize and predict patterns in data."
}
```
**Errors:**
- `404 Not Found`: "Question 101 does not exist"

---

## 6. Progress & Analytics

### `GET /users/{user_id}/progress`
**Purpose:** Fetch overall stats.
**Response:** JSON dictionary representing overall pass rates and quiz counts.

### `GET /users/{user_id}/weak-topics`
**Purpose:** Fetch a list of topics the user struggles with.
**Response:** JSON array of topic strings and scores.

### `GET /users/{user_id}/strong-topics`
**Purpose:** Fetch a list of topics the user excels at.
**Response:** JSON array of topic strings and scores.

---

## Mobile Developer Quick Start Sequence

Here is the exact minimum sequence a Flutter/Kotlin app should implement to use the Core Brain:

1. **Check server health:** Call `GET /health` to ensure the AI is ready.
2. **Upload a document:** Call `POST /documents` with the user's PDF file as `multipart/form-data`.
3. **Ask a question:** Call `POST /questions` sending `{"query": "..."}` and display the `answer` string.
4. **Generate a quiz:** Call `POST /quizzes` sending `{"user_id": 1, "topic": "...", "num_questions": 3}`. Display the returned list of questions.
5. **Submit an answer:** When the user taps an option, call `POST /answers` sending `{"question_id": 101, "user_answer": "Selected text"}` and display whether it is correct or incorrect.
6. **Fetch progress:** Call `GET /users/1/progress` to populate the user's profile screen.
