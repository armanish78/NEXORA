import json
import logging
from typing import Dict, Any
from app.database import get_question, save_user_answer
from app.config import DB_PATH

logger = logging.getLogger(__name__)

class AnswerEvaluator:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def evaluate(self, question_id: int, user_answer: str) -> Dict[str, Any]:
        """
        Deterministically evaluates a user's answer against a stored question.
        Returns a dictionary containing feedback, or raises ValueError on invalid submissions.
        """
        # Validate empty answer
        if not user_answer or not str(user_answer).strip():
            raise ValueError("Submission is empty.")

        user_answer = str(user_answer).strip()
        
        # Load question
        question = get_question(question_id, db_path=self.db_path)
        if not question:
            raise ValueError(f"Question ID {question_id} does not exist.")
            
        # Validate question type
        if question.get("question_type") != "MCQ":
            raise ValueError(f"Unsupported question type: {question.get('question_type')}")
            
        # Parse and validate stored data
        try:
            options = json.loads(question["options"])
            if not isinstance(options, list) or len(options) != 4:
                raise ValueError("Malformed options in database.")
                
            source_metadata = json.loads(question["source_metadata"])
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise ValueError(f"Malformed question data in database: {e}")
            
        correct_answer = question.get("correct_answer")
        if not correct_answer or correct_answer not in options:
            raise ValueError("Stored correct answer is malformed or not in options.")
            
        # Check if user answer is one of the valid options
        if user_answer not in options:
            raise ValueError(f"Submitted answer '{user_answer}' is not a valid option.")
            
        # Deterministic check
        is_correct = (user_answer == correct_answer)
        
        # Store result
        save_user_answer(
            question_id=question_id,
            user_input=user_answer,
            is_correct=is_correct,
            db_path=self.db_path
        )
        
        # Construct feedback
        feedback = {
            "question_id": question_id,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question.get("explanation"),
            "topic": question.get("topic"),
            "difficulty": question.get("difficulty"),
            "source_metadata": source_metadata
        }
        
        return feedback
