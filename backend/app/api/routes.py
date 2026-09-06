from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from typing import List, Dict, Any
import os
import tempfile
import shutil

from app.api.schemas import (
    QAQuery, QAResponse, QuizRequest, QuizResponse, 
    PersonalizedQuizRequest, AnswerSubmission, AnswerResponse,
    HealthResponse
)
from app.api.dependencies import (
    get_rag_generator, get_quiz_generator, 
    get_personalization_engine, get_answer_evaluator, get_model_name, get_retriever
)
from app.ingest import ingest_file, load_processed
from app.cleaning import clean_pages
from app.chunking import chunk_pages
from app.embeddings import embed_chunks
from app.vector_store import create_index, save_index, load_index
from app.config import CHUNK_SIZE, CHUNK_OVERLAP, MINIMUM_CHUNK_SIZE
from app.progress import (
    get_overall_progress, get_topic_performance, 
    get_weak_topics, get_strong_topics
)

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "model": get_model_name()}

@router.post("/documents")
def upload_document(file: UploadFile = File(...), retriever = Depends(get_retriever)):
    """
    Upload and ingest a document.
    Executes synchronously in the FastAPI threadpool.
    """
    if not file.filename.lower().endswith((".pdf", ".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Unsupported file type")
        
    # Save uploaded file to temp path
    fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(file.filename)[1])
    os.close(fd)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Call the existing Core Brain ingestion logic
        pages = ingest_file(temp_path, force=True, original_filename=file.filename)
        if not pages:
            # Maybe cached or failed
            raise HTTPException(status_code=400, detail="Failed to ingest or extract text")
            
        # Run rest of pipeline (simulating app.main flow)
        cleaned = clean_pages(pages)
        chunks = chunk_pages(cleaned, CHUNK_SIZE, CHUNK_OVERLAP, MINIMUM_CHUNK_SIZE)
        
        embeddings = embed_chunks(retriever.model, chunks)
        
        index = create_index(embeddings)
        save_index(index, chunks)
        
        return {
            "success": True,
            "filename": file.filename,
            "pages": len(pages),
            "chunks_created": len(chunks)
        }
    finally:
        os.remove(temp_path)

@router.get("/documents/{filename}/topics")
def get_document_topics(filename: str):
    """
    Retrieve document headings/topics for generating specific study questions.
    """
    try:
        try:
            _, chunks, _ = load_index()
        except FileNotFoundError:
            return {"filename": filename, "topics": []}
            
        topics = set()
        for chunk in chunks:
            if chunk.get("filename") == filename:
                heading = chunk.get("heading")
                if heading and heading != "Document Outline":
                    topics.add(heading)
        
        return {"filename": filename, "topics": list(topics)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/questions", response_model=QAResponse)
def ask_question(request: QAQuery, generator = Depends(get_rag_generator)):
    """
    Ask a question against the ingested corpus.
    Delegates strictly to RAGGenerator.generate().
    """
    try:
        res = generator.generate(request.query, top_k=request.top_k, filename=request.filename)
        
        # Check for grounding refusal
        if not res.get("success", True) or res.get("answer") is None:
            return {
                "success": False,
                "reason": res.get("reason", "INSUFFICIENT_SOURCE_CONTEXT")
            }
            
        return {
            "success": True,
            "answer": res.get("answer"),
            "citations": res.get("used_chunks", []),
            "retrieved_chunks": res.get("retrieved_chunks", []),
            "raw_llm_output": res.get("raw_llm_output", ""),
            "first_raw_output": res.get("first_raw_output", ""),
            "retry_triggered": res.get("retry_triggered", False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quizzes", response_model=QuizResponse)
def generate_quiz(request: QuizRequest, generator = Depends(get_quiz_generator)):
    """
    Generate a standard quiz on a specific topic.
    Delegates to QuizGenerator.
    """
    try:
        res = generator.generate_quiz(
            user_id=request.user_id,
            topic=request.topic,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
            filename=request.filename
        )
        if not res.get("success"):
            # Could be INSUFFICIENT_SOURCE_CONTEXT or retry failure
            return {"success": False, "reason": res.get("reason", "Generation failed")}
            
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quizzes/personalized", response_model=QuizResponse)
def generate_personalized_quiz(request: PersonalizedQuizRequest, engine = Depends(get_personalization_engine)):
    """
    Generate a quiz targeted at the user's weakest topic.
    Delegates to PersonalizationEngine.
    """
    try:
        res = engine.generate_personalized_quiz(
            user_id=request.user_id,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
            filename=request.filename
        )
        if not res.get("success"):
            return {"success": False, "reason": res.get("reason", "Personalization failed")}
            
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answers", response_model=AnswerResponse)
def submit_answer(request: AnswerSubmission, evaluator = Depends(get_answer_evaluator)):
    """
    Submit an answer to a quiz question for grading.
    """
    try:
        res = evaluator.evaluate(request.question_id, request.user_answer)
        return {
            "is_correct": res.get("is_correct", False),
            "explanation": res.get("explanation", "")
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/progress")
def get_progress(user_id: int):
    """Retrieve overall progress analytics for a user."""
    return get_overall_progress(user_id)

@router.get("/users/{user_id}/weak-topics")
def weak_topics(user_id: int):
    """Retrieve weak topics for a user."""
    return get_weak_topics(user_id)

@router.get("/users/{user_id}/strong-topics")
def strong_topics(user_id: int):
    """Retrieve strong topics for a user."""
    return get_strong_topics(user_id)
