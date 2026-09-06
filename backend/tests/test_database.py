import os
import sqlite3
import json
import pytest

from app.database import (
    initialize_db,
    create_user,
    create_quiz,
    add_question,
    save_user_answer,
    get_user_answers,
    get_db_connection
)

@pytest.fixture
def temp_db_path(tmp_path):
    """Provide a temporary database file for tests."""
    db_file = tmp_path / "test_study_assistant.db"
    db_path = str(db_file)
    initialize_db(db_path)
    return db_path

def test_database_initialization(temp_db_path):
    """Test that all tables are created successfully."""
    with get_db_connection(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row['name'] for row in cursor.fetchall()]
        assert "users" in tables
        assert "quizzes" in tables
        assert "questions" in tables
        assert "user_answers" in tables

def test_create_user(temp_db_path):
    """Test user creation."""
    user_id = create_user(temp_db_path)
    assert user_id == 1
    
    with get_db_connection(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        assert user is not None
        assert user['id'] == user_id
        assert user['created_at'] is not None

def test_create_quiz(temp_db_path):
    """Test quiz creation and foreign key relationship to user."""
    user_id = create_user(temp_db_path)
    quiz_id = create_quiz(user_id=user_id, requested_difficulty="medium", db_path=temp_db_path)
    assert quiz_id == 1
    
    with get_db_connection(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        quiz = cursor.fetchone()
        assert quiz is not None
        assert quiz['user_id'] == user_id
        assert quiz['requested_difficulty'] == "medium"

def test_invalid_user_fk(temp_db_path):
    """Test foreign key enforcement when creating a quiz for a non-existent user."""
    with pytest.raises(sqlite3.IntegrityError):
        create_quiz(user_id=999, requested_difficulty="medium", db_path=temp_db_path)

def test_add_question(temp_db_path):
    """Test adding a question with JSON serialization."""
    user_id = create_user(temp_db_path)
    quiz_id = create_quiz(user_id, "hard", temp_db_path)
    
    options = ["A", "B", "C", "D"]
    metadata = {"chunk_id": 42, "page": 5}
    
    q_id = add_question(
        quiz_id=quiz_id,
        question_text="What is X?",
        question_type="MCQ",
        difficulty="hard",
        correct_answer="A",
        options=options,
        explanation="Because A.",
        topic="Testing",
        source_metadata=metadata,
        db_path=temp_db_path
    )
    assert q_id == 1
    
    with get_db_connection(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE id = ?", (q_id,))
        q = cursor.fetchone()
        assert q['question_text'] == "What is X?"
        assert q['topic'] == "Testing"
        
        # Verify JSON was stored correctly
        stored_options = json.loads(q['options'])
        assert stored_options == options
        
        stored_meta = json.loads(q['source_metadata'])
        assert stored_meta['chunk_id'] == 42

def test_invalid_quiz_fk(temp_db_path):
    """Test foreign key enforcement on questions."""
    with pytest.raises(sqlite3.IntegrityError):
        add_question(
            quiz_id=999,  # Doesn't exist
            question_text="Invalid?",
            question_type="MCQ",
            difficulty="easy",
            correct_answer="A",
            db_path=temp_db_path
        )

def test_save_user_answer(temp_db_path):
    """Test saving an answer and fetching it."""
    user_id = create_user(temp_db_path)
    quiz_id = create_quiz(user_id, "easy", temp_db_path)
    q_id = add_question(
        quiz_id=quiz_id,
        question_text="Test",
        question_type="MCQ",
        difficulty="easy",
        correct_answer="True",
        db_path=temp_db_path
    )
    
    ans_id = save_user_answer(question_id=q_id, user_input="True", is_correct=True, db_path=temp_db_path)
    assert ans_id == 1
    
    with get_db_connection(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_answers WHERE id = ?", (ans_id,))
        ans = cursor.fetchone()
        assert ans['is_correct'] == 1  # SQLite stores bool as 1/0
        assert ans['user_input'] == "True"

def test_invalid_question_fk(temp_db_path):
    """Test foreign key enforcement on answers."""
    with pytest.raises(sqlite3.IntegrityError):
        save_user_answer(question_id=999, user_input="A", is_correct=False, db_path=temp_db_path)

def test_multiple_records(temp_db_path):
    """Test inserting multiple quizzes, questions, and answers for a user."""
    user_id = create_user(temp_db_path)
    
    # Create two quizzes
    q1_id = create_quiz(user_id, "easy", temp_db_path)
    q2_id = create_quiz(user_id, "medium", temp_db_path)
    
    # Add questions
    qq1 = add_question(q1_id, "Q1", "MCQ", "easy", "A", topic="T1", db_path=temp_db_path)
    qq2 = add_question(q2_id, "Q2", "MCQ", "medium", "B", topic="T2", db_path=temp_db_path)
    
    # Answer them
    save_user_answer(qq1, "A", True, temp_db_path)
    save_user_answer(qq2, "C", False, temp_db_path)
    
    # Retrieve all answers using the helper function
    answers = get_user_answers(user_id, temp_db_path)
    assert len(answers) == 2
    
    # Ensure correct join behavior
    topics = set(a['topic'] for a in answers)
    assert "T1" in topics
    assert "T2" in topics

def test_persistence_reopen(tmp_path):
    """Test that data survives closing and reopening the connection/file."""
    db_file = tmp_path / "persist.db"
    db_path = str(db_file)
    initialize_db(db_path)
    
    # Session 1: Create and write
    user_id = create_user(db_path)
    
    # Session 2: Read
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        assert user is not None
        assert user['id'] == user_id
