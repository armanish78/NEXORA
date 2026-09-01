import sqlite3
import json
from contextlib import contextmanager
import logging

from app.config import DB_PATH

logger = logging.getLogger(__name__)

# ============================================================
# SCHEMA DEFINITION
# ============================================================

SCHEMA = """
-- Users table to track identity
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Quizzes table to track a study session
CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    requested_difficulty TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Questions table to track generated questions and their provenance
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    options TEXT, -- Stored as JSON string
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    topic TEXT,
    source_metadata TEXT, -- Stored as JSON string
    FOREIGN KEY(quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);

-- User answers table to track performance
CREATE TABLE IF NOT EXISTS user_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    user_input TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(question_id) REFERENCES questions(id) ON DELETE CASCADE
);
"""


# ============================================================
# CONNECTION MANAGEMENT
# ============================================================

@contextmanager
def get_db_connection(db_path=DB_PATH):
    """
    Context manager to safely get a database connection, enforce foreign keys,
    and ensure the connection is closed after use.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False, timeout=15.0)
    # Enable foreign key support which is off by default in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    # Return dictionary-like rows for easier attribute access
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def initialize_db(db_path=DB_PATH):
    """
    Create tables if they don't exist. Safely idempotent.
    """
    with get_db_connection(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


# ============================================================
# DATA ACCESS OBJECTS (DAO)
# ============================================================

def create_user(db_path=DB_PATH) -> int:
    """Create a new user and return their ID."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users DEFAULT VALUES")
        conn.commit()
        return cursor.lastrowid


def create_quiz(user_id: int, requested_difficulty: str, db_path=DB_PATH) -> int:
    """Create a new quiz session for a user and return the quiz ID."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO quizzes (user_id, requested_difficulty) VALUES (?, ?)",
            (user_id, requested_difficulty)
        )
        conn.commit()
        return cursor.lastrowid


def add_question(
    quiz_id: int,
    question_text: str,
    question_type: str,
    difficulty: str,
    correct_answer: str,
    options: list = None,
    explanation: str = None,
    topic: str = None,
    source_metadata: dict = None,
    db_path=DB_PATH
) -> int:
    """
    Add a generated question to a quiz.
    Lists and dicts (options, source_metadata) are safely serialized to JSON.
    """
    options_json = json.dumps(options) if options is not None else None
    metadata_json = json.dumps(source_metadata) if source_metadata is not None else None

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO questions 
            (quiz_id, question_text, question_type, difficulty, options, correct_answer, explanation, topic, source_metadata) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (quiz_id, question_text, question_type, difficulty, options_json, correct_answer, explanation, topic, metadata_json)
        )
        conn.commit()
        return cursor.lastrowid


def save_user_answer(question_id: int, user_input: str, is_correct: bool, db_path=DB_PATH) -> int:
    """
    Record a user's answer to a specific question.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_answers (question_id, user_input, is_correct) VALUES (?, ?, ?)",
            (question_id, user_input, is_correct)
        )
        conn.commit()
        return cursor.lastrowid


def get_question(question_id: int, db_path=DB_PATH) -> dict:
    """Retrieve a single question by its ID."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_answers(user_id: int, db_path=DB_PATH) -> list:
    """
    Helper function for future progress tracking.
    Retrieves all answers given by a specific user across all quizzes.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT a.*, q.topic, q.difficulty, q.quiz_id 
            FROM user_answers a
            JOIN questions q ON a.question_id = q.id
            JOIN quizzes z ON q.quiz_id = z.id
            WHERE z.user_id = ?
            ''',
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
