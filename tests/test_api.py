import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.api.dependencies import (
    get_rag_generator, get_quiz_generator,
    get_personalization_engine, get_answer_evaluator, get_model_name
)

class MockRAGGenerator:
    def generate(self, query, top_k=5):
        if query == "How to bake a cake?":
            return {"success": False, "reason": "INSUFFICIENT_SOURCE_CONTEXT", "answer": None}
        return {
            "success": True,
            "answer": "This is a mocked answer.",
            "citations": [{"source": "mock", "text": "mock"}],
            "retrieved_chunks": []
        }

class MockQuizGenerator:
    def generate_quiz(self, user_id, topic, difficulty="medium", num_questions=1):
        return {
            "success": True,
            "quiz_id": 1,
            "questions": [{"q": "test", "options": ["A","B","C","D"]}]
        }

class MockPersonalizationEngine:
    def generate_personalized_quiz(self, user_id, difficulty="medium", num_questions=1):
        return {
            "success": True,
            "quiz_id": 2,
            "questions": [{"q": "test", "options": ["A","B","C","D"]}]
        }

class MockAnswerEvaluator:
    def evaluate(self, question_id, user_answer):
        return {"is_correct": True, "explanation": "Good"}

@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setattr("app.config.DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setattr("app.config.FAISS_INDEX_PATH", str(tmp_path / "test_faiss.bin"))
    monkeypatch.setattr("app.api.main.init_core_brain", lambda: None)
    
    app.dependency_overrides[get_rag_generator] = lambda: MockRAGGenerator()
    app.dependency_overrides[get_quiz_generator] = lambda: MockQuizGenerator()
    app.dependency_overrides[get_personalization_engine] = lambda: MockPersonalizationEngine()
    app.dependency_overrides[get_answer_evaluator] = lambda: MockAnswerEvaluator()
    app.dependency_overrides[get_model_name] = lambda: "mock-model"
    
    with TestClient(app) as client:
        yield client
        
    app.dependency_overrides.clear()

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_invalid_request(client):
    response = client.post("/questions", json={"top_k": 5})
    assert response.status_code == 422 

def test_ask_question_success(client):
    response = client.post("/questions", json={"query": "What is AI?", "top_k": 5})
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["answer"] == "This is a mocked answer."

def test_ask_question_grounding_refusal(client):
    response = client.post("/questions", json={"query": "How to bake a cake?"})
    assert response.status_code == 200
    assert response.json()["success"] == False
    assert response.json()["reason"] == "INSUFFICIENT_SOURCE_CONTEXT"

def test_generate_quiz_success(client):
    response = client.post("/quizzes", json={"user_id": 1, "topic": "AI", "difficulty": "easy"})
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["quiz_id"] == 1

def test_personalized_quiz_success(client):
    response = client.post("/quizzes/personalized", json={"user_id": 1, "difficulty": "medium"})
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["quiz_id"] == 2

def test_submit_answer(client):
    response = client.post("/answers", json={"question_id": 1, "user_answer": "A"})
    assert response.status_code == 200
    assert response.json()["is_correct"] == True

from unittest.mock import patch
def test_progress_endpoints(client):
    with patch("app.api.routes.get_overall_progress", return_value={"total_questions": 10, "accuracy": 0.8}):
        response = client.get("/users/1/progress")
        assert response.status_code == 200
        assert response.json()["accuracy"] == 0.8

    with patch("app.api.routes.get_weak_topics", return_value=[{"topic": "Math", "accuracy": 0.2}]):
        response = client.get("/users/1/weak-topics")
        assert response.status_code == 200
        assert response.json()[0]["topic"] == "Math"
