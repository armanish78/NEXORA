import pytest
import tempfile
import os
import json
from app.database import initialize_db, create_user, create_quiz, add_question, get_user_answers
from app.answer_evaluator import AnswerEvaluator

@pytest.fixture
def test_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    initialize_db(path)
    yield path
    os.unlink(path)

@pytest.fixture
def setup_data(test_db):
    user_id = create_user(test_db)
    quiz_id = create_quiz(user_id, "medium", test_db)
    
    question_id = add_question(
        quiz_id=quiz_id,
        question_text="What is the capital of France?",
        question_type="MCQ",
        difficulty="medium",
        correct_answer="Paris",
        options=["London", "Paris", "Berlin", "Rome"],
        explanation="Paris is the capital of France.",
        topic="Geography",
        source_metadata=[{"chunk_id": 1}],
        db_path=test_db
    )
    
    return {
        "user_id": user_id,
        "quiz_id": quiz_id,
        "question_id": question_id,
        "db_path": test_db
    }

def test_correct_answer(setup_data):
    evaluator = AnswerEvaluator(setup_data["db_path"])
    feedback = evaluator.evaluate(setup_data["question_id"], "Paris")
    
    assert feedback["is_correct"] is True
    assert feedback["user_answer"] == "Paris"
    assert feedback["correct_answer"] == "Paris"
    assert feedback["explanation"] == "Paris is the capital of France."
    assert feedback["topic"] == "Geography"
    assert feedback["difficulty"] == "medium"
    assert len(feedback["source_metadata"]) == 1
    
    # Check persistence
    answers = get_user_answers(setup_data["user_id"], setup_data["db_path"])
    assert len(answers) == 1
    assert answers[0]["is_correct"] == 1
    assert answers[0]["user_input"] == "Paris"

def test_incorrect_answer(setup_data):
    evaluator = AnswerEvaluator(setup_data["db_path"])
    feedback = evaluator.evaluate(setup_data["question_id"], "London")
    
    assert feedback["is_correct"] is False
    assert feedback["user_answer"] == "London"
    assert feedback["correct_answer"] == "Paris"
    
    # Check persistence
    answers = get_user_answers(setup_data["user_id"], setup_data["db_path"])
    assert len(answers) == 1
    assert answers[0]["is_correct"] == 0
    assert answers[0]["user_input"] == "London"

def test_empty_answer_rejected(setup_data):
    evaluator = AnswerEvaluator(setup_data["db_path"])
    with pytest.raises(ValueError, match="Submission is empty"):
        evaluator.evaluate(setup_data["question_id"], "")
    with pytest.raises(ValueError, match="Submission is empty"):
        evaluator.evaluate(setup_data["question_id"], "   ")

def test_answer_not_in_options(setup_data):
    evaluator = AnswerEvaluator(setup_data["db_path"])
    with pytest.raises(ValueError, match="is not a valid option"):
        evaluator.evaluate(setup_data["question_id"], "Madrid")

def test_invalid_question_id(setup_data):
    evaluator = AnswerEvaluator(setup_data["db_path"])
    with pytest.raises(ValueError, match="does not exist"):
        evaluator.evaluate(999, "Paris")

def test_malformed_question_data(setup_data):
    # Insert a malformed question (wrong type)
    q_id = add_question(
        quiz_id=setup_data["quiz_id"],
        question_text="Q?",
        question_type="TF",
        difficulty="easy",
        correct_answer="True",
        options=None,
        db_path=setup_data["db_path"]
    )
    
    evaluator = AnswerEvaluator(setup_data["db_path"])
    with pytest.raises(ValueError, match="Unsupported question type"):
        evaluator.evaluate(q_id, "True")

def test_multiple_evaluations(setup_data):
    q2_id = add_question(
        quiz_id=setup_data["quiz_id"],
        question_text="Q2?",
        question_type="MCQ",
        difficulty="easy",
        correct_answer="A",
        options=["A", "B", "C", "D"],
        explanation="Exp",
        topic="T",
        source_metadata=[],
        db_path=setup_data["db_path"]
    )
    
    evaluator = AnswerEvaluator(setup_data["db_path"])
    evaluator.evaluate(setup_data["question_id"], "Paris")
    evaluator.evaluate(q2_id, "B")
    
    answers = get_user_answers(setup_data["user_id"], setup_data["db_path"])
    assert len(answers) == 2
    assert answers[0]["is_correct"] == 1
    assert answers[1]["is_correct"] == 0

def test_integration_flow(setup_data):
    # This proves the sequence: Quiz -> Question -> Student answer -> Evaluation -> SQLite
    # Since we don't want real LLM, we use the fake setup_data which simulates QuizGenerator output
    
    db_path = setup_data["db_path"]
    user_id = setup_data["user_id"]
    
    # 1. User is created (done in setup)
    # 2. Quiz and Question are created (done in setup, representing QuizGenerator)
    q_id = setup_data["question_id"]
    
    # 3. Student answers the question
    student_answer = "Rome"
    
    # 4. Evaluation
    evaluator = AnswerEvaluator(db_path)
    feedback = evaluator.evaluate(q_id, student_answer)
    
    assert feedback["is_correct"] is False
    assert feedback["correct_answer"] == "Paris"
    
    # 5. SQLite state verification
    answers = get_user_answers(user_id, db_path)
    assert len(answers) == 1
    assert answers[0]["user_input"] == "Rome"
    assert answers[0]["question_id"] == q_id
