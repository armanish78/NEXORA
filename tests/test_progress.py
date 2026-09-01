import pytest
import tempfile
import os
import json
from app.database import initialize_db, create_user, create_quiz, add_question, save_user_answer
from app.progress import (
    get_overall_progress,
    get_topic_performance,
    get_difficulty_performance,
    get_weak_topics,
    get_strong_topics,
    get_progress_over_time
)

@pytest.fixture
def test_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    initialize_db(path)
    yield path
    os.unlink(path)

@pytest.fixture
def test_data(test_db):
    user1 = create_user(test_db)
    user2 = create_user(test_db)
    
    quiz1 = create_quiz(user1, "medium", test_db)
    quiz2 = create_quiz(user1, "hard", test_db)
    quiz3 = create_quiz(user2, "easy", test_db)
    
    # Topic: Machine Learning (8/10 correct) - User 1
    for i in range(10):
        q_id = add_question(quiz1, f"ML Q{i}", "MCQ", "medium", "A", ["A","B","C","D"], "Exp", "Machine Learning", [], test_db)
        save_user_answer(q_id, "A" if i < 8 else "B", i < 8, test_db)
        
    # Topic: Bayesian Learning (3/10 correct) - User 1
    for i in range(10):
        q_id = add_question(quiz1, f"Bayesian Q{i}", "MCQ", "hard", "A", ["A","B","C","D"], "Exp", "Bayesian Learning", [], test_db)
        save_user_answer(q_id, "A" if i < 3 else "B", i < 3, test_db)
        
    # Topic: Neural Networks (9/10 correct) - User 1
    for i in range(10):
        q_id = add_question(quiz2, f"NN Q{i}", "MCQ", "medium", "A", ["A","B","C","D"], "Exp", "Neural Networks", [], test_db)
        save_user_answer(q_id, "A" if i < 9 else "B", i < 9, test_db)
        
    # Topic: Single attempt (1/1 correct) - User 1
    q_id = add_question(quiz2, "Single Q", "MCQ", "easy", "A", ["A","B","C","D"], "Exp", "Single", [], test_db)
    save_user_answer(q_id, "A", True, test_db)
    
    # User 2 data (User isolation check)
    q_id2 = add_question(quiz3, "User2 Q", "MCQ", "easy", "A", ["A","B","C","D"], "Exp", "Machine Learning", [], test_db)
    save_user_answer(q_id2, "B", False, test_db)
    
    return {"u1": user1, "u2": user2, "db": test_db}

def test_empty_user(test_db):
    user = create_user(test_db)
    prog = get_overall_progress(user, test_db)
    assert prog["total_questions"] == 0
    assert prog["accuracy"] == 0.0
    
    assert get_topic_performance(user, test_db) == []
    assert get_weak_topics(user, limit=3, db_path=test_db) == []
    assert get_strong_topics(user, limit=3, db_path=test_db) == []

def test_overall_progress(test_data):
    prog = get_overall_progress(test_data["u1"], test_data["db"])
    assert prog["total_questions"] == 31
    assert prog["correct"] == 21
    assert prog["incorrect"] == 10
    assert prog["quizzes_attempted"] == 2
    assert prog["accuracy"] == round((21 / 31) * 100, 1)

def test_topic_performance(test_data):
    topics = get_topic_performance(test_data["u1"], test_data["db"])
    assert len(topics) == 4
    
    # Check ML
    ml = next(t for t in topics if t["topic"] == "Machine Learning")
    assert ml["attempts"] == 10
    assert ml["accuracy"] == 80.0
    
    # Check Bayesian
    bayes = next(t for t in topics if t["topic"] == "Bayesian Learning")
    assert bayes["accuracy"] == 30.0

def test_difficulty_performance(test_data):
    diffs = get_difficulty_performance(test_data["u1"], test_data["db"])
    
    # 10 medium (ML), 10 hard (Bayesian), 10 medium (NN), 1 easy (Single)
    # ML (8 correct) + NN (9 correct) = 17 correct out of 20 medium
    assert diffs["medium"]["attempts"] == 20
    assert diffs["medium"]["correct"] == 17
    assert diffs["medium"]["accuracy"] == 85.0
    
    assert diffs["hard"]["attempts"] == 10
    assert diffs["hard"]["correct"] == 3
    assert diffs["hard"]["accuracy"] == 30.0
    
    assert diffs["easy"]["attempts"] == 1
    assert diffs["easy"]["accuracy"] == 100.0

def test_weak_topics(test_data):
    weak = get_weak_topics(test_data["u1"], limit=3, db_path=test_data["db"])
    # Bayesian should be weakest (30%)
    assert len(weak) == 3
    assert weak[0]["topic"] == "Bayesian Learning"
    assert weak[0]["accuracy"] == 30.0
    assert weak[1]["topic"] == "Machine Learning"
    assert weak[2]["topic"] == "Neural Networks"

def test_strong_topics(test_data):
    strong = get_strong_topics(test_data["u1"], limit=3, db_path=test_data["db"])
    # NN should be strongest (90%) among qualified
    # Note: "Single" has 100% but only 1 attempt, so it should be filtered out
    assert len(strong) == 3
    assert strong[0]["topic"] == "Neural Networks"
    assert strong[0]["accuracy"] == 90.0
    assert strong[1]["topic"] == "Machine Learning"
    assert strong[2]["topic"] == "Bayesian Learning"
    
    # Verify "Single" is not in there
    assert "Single" not in [t["topic"] for t in strong]

def test_user_isolation(test_data):
    prog2 = get_overall_progress(test_data["u2"], test_data["db"])
    assert prog2["total_questions"] == 1
    assert prog2["correct"] == 0
    
    topics2 = get_topic_performance(test_data["u2"], test_data["db"])
    assert len(topics2) == 1
    assert topics2[0]["topic"] == "Machine Learning"
    assert topics2[0]["accuracy"] == 0.0

def test_progress_over_time(test_data):
    history = get_progress_over_time(test_data["u1"], test_data["db"])
    assert len(history) >= 1
    # Check that it returns dictionaries with date, attempts, accuracy
    assert "date" in history[0]
    assert "attempts" in history[0]
    assert "accuracy" in history[0]
