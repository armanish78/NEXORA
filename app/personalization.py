from typing import Dict, Any, List
from app.progress import get_weak_topics
from app.quiz_generator import QuizGenerator
import logging

logger = logging.getLogger(__name__)

class PersonalizationEngine:
    def __init__(self, quiz_generator: QuizGenerator):
        self.quiz_generator = quiz_generator

    def generate_personalized_quiz(self, user_id: int, difficulty: str = "medium", num_questions: int = 1) -> Dict[str, Any]:
        """
        Orchestrates the generation of a personalized quiz targeted at the user's weak topics.
        """
        # Validate difficulty (QuizGenerator also validates, but good practice here too)
        if difficulty not in ["easy", "medium", "hard"]:
            raise ValueError(f"Invalid difficulty: {difficulty}")

        # Determine weak topics
        weak_topics = get_weak_topics(user_id, limit=3)
        
        # Behavior when no history is present (or no weak topics meet the threshold)
        if not weak_topics:
            raise ValueError("Insufficient history to generate a personalized quiz. Please take a general quiz first.")

        # Determine target topic
        # For simplicity, if they want multiple questions, we will focus entirely on their #1 weakest topic 
        # in this phase, as requested by 'Do not introduce complicated repetition logic'.
        target_topic_data = weak_topics[0]
        target_topic = target_topic_data["topic"]
        
        explanation = (
            f"Based on your previous answers, {target_topic} is currently one of your weakest topics "
            f"({target_topic_data['accuracy']}% accuracy across {target_topic_data['attempts']} attempts)."
        )

        # Delegate to QuizGenerator
        result = self.quiz_generator.generate_quiz(
            user_id=user_id,
            topic=target_topic,
            difficulty=difficulty,
            num_questions=num_questions
        )
        
        if not result.get("success"):
            return result

        # Build clean return structure
        return {
            "personalized": True,
            "target_topics": weak_topics,
            "selected_topic": target_topic,
            "difficulty": difficulty,
            "quiz_id": result["quiz_id"],
            "explanation": explanation
        }
