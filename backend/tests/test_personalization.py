import pytest
import tempfile
import os
import json
from unittest.mock import MagicMock

from app.personalization import PersonalizationEngine
from app.quiz_generator import QuizGenerator
from app.database import initialize_db, create_user, create_quiz, add_question, save_user_answer

class MockQuizGenerator:
    def __init__(self):
        self.last_user_id = None
        self.last_topic = None
        self.last_difficulty = None
        self.last_num_questions = None
        self.last_filename = None
        
    def generate_quiz(self, user_id, topic, difficulty="medium", num_questions=1, filename=None):
        self.last_user_id = user_id
        self.last_topic = topic
        self.last_difficulty = difficulty
        self.last_num_questions = num_questions
        self.last_filename = filename
        return {"success": True, "quiz_id": 999, "message": "Success"}

def test_personalized_quiz_targets_weakest_topic(monkeypatch):
    # Mock progress to return two topics
    mock_weak_topics = [
        {"topic": "Bayesian Learning", "attempts": 10, "accuracy": 30.0},
        {"topic": "Machine Learning", "attempts": 10, "accuracy": 50.0}
    ]
    monkeypatch.setattr("app.personalization.get_weak_topics", lambda uid, limit: mock_weak_topics[:limit])
    
    mock_qg = MockQuizGenerator()
    engine = PersonalizationEngine(mock_qg)
    
    result = engine.generate_personalized_quiz(user_id=1, difficulty="hard", num_questions=3)
    
    # Assert QuizGenerator received the correct instructions
    assert mock_qg.last_user_id == 1
    assert mock_qg.last_topic == "Bayesian Learning"
    assert mock_qg.last_difficulty == "hard"
    assert mock_qg.last_num_questions == 3
    
    # Assert output structure
    assert result["personalized"] is True
    assert result["selected_topic"] == "Bayesian Learning"
    assert result["difficulty"] == "hard"
    assert result["quiz_id"] == 999
    assert "30.0% accuracy" in result["explanation"]
    assert "10 attempts" in result["explanation"]
    
def test_no_history_raises_error(monkeypatch):
    monkeypatch.setattr("app.personalization.get_weak_topics", lambda uid, limit: [])
    
    mock_qg = MockQuizGenerator()
    engine = PersonalizationEngine(mock_qg)
    
    with pytest.raises(ValueError, match="Insufficient history"):
        engine.generate_personalized_quiz(user_id=1)

def test_invalid_difficulty():
    mock_qg = MockQuizGenerator()
    engine = PersonalizationEngine(mock_qg)
    
    with pytest.raises(ValueError, match="Invalid difficulty"):
        engine.generate_personalized_quiz(user_id=1, difficulty="extreme")

def test_user_isolation(monkeypatch):
    def fake_get_weak(uid, limit):
        if uid == 1:
            return [{"topic": "Topic A", "attempts": 5, "accuracy": 20.0}]
        else:
            return [{"topic": "Topic B", "attempts": 5, "accuracy": 10.0}]
            
    monkeypatch.setattr("app.personalization.get_weak_topics", fake_get_weak)
    
    mock_qg = MockQuizGenerator()
    engine = PersonalizationEngine(mock_qg)
    
    res1 = engine.generate_personalized_quiz(user_id=1)
    assert res1["selected_topic"] == "Topic A"
    
    res2 = engine.generate_personalized_quiz(user_id=2)
    assert res2["selected_topic"] == "Topic B"

def test_quiz_generator_error_propagates(monkeypatch):
    monkeypatch.setattr("app.personalization.get_weak_topics", lambda uid, limit: [{"topic": "T", "attempts": 5, "accuracy": 10.0}])
    
    class FailingQG:
        def generate_quiz(self, *args, **kwargs):
            raise RuntimeError("LLM Failure")
            
    engine = PersonalizationEngine(FailingQG())
    
    with pytest.raises(RuntimeError, match="LLM Failure"):
        engine.generate_personalized_quiz(user_id=1)

# =====================================================================
# INTEGRATION TEST
# =====================================================================
@pytest.fixture
def test_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    initialize_db(path)
    yield path
    os.unlink(path)

def test_integration_personalization(test_db, monkeypatch):
    # Setup data
    user_id = create_user(test_db)
    quiz_id = create_quiz(user_id, "medium", test_db)
    
    def simulate_topic(topic, correct, total):
        for i in range(total):
            q_id = add_question(quiz_id, f"Q {i}", "MCQ", "medium", "A", ["A","B","C","D"], "Exp", topic, [], test_db)
            save_user_answer(q_id, "A" if i < correct else "B", i < correct, test_db)
            
    # Bayesian Learning: 3/10 (30%)
    simulate_topic("Bayesian Learning", 3, 10)
    # Machine Learning: 8/10 (80%)
    simulate_topic("Machine Learning", 8, 10)
    # Neural Networks: 9/10 (90%)
    simulate_topic("Neural Networks", 9, 10)

    # Monkeypatch the progress analyzer to use the test_db path
    import app.progress
    original_get = app.progress.get_weak_topics
    def get_weak_topics_test_db(uid, limit=3):
        return original_get(uid, limit=limit, db_path=test_db)
        
    monkeypatch.setattr("app.personalization.get_weak_topics", get_weak_topics_test_db)
    
    # We use MockQuizGenerator to verify correct routing
    mock_qg = MockQuizGenerator()
    engine = PersonalizationEngine(mock_qg)
    
    # Action
    result = engine.generate_personalized_quiz(user_id=user_id, difficulty="medium", num_questions=3)
    
    # Assertions
    assert result["selected_topic"] == "Bayesian Learning"
    assert result["difficulty"] == "medium"
    assert mock_qg.last_topic == "Bayesian Learning"
    assert mock_qg.last_num_questions == 3
    assert "30.0% accuracy" in result["explanation"]
