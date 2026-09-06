import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from app.retrieve import Retriever
from app.llm import LLMProvider
from app.database import create_quiz, add_question
from app.config import INITIAL_GROUNDING_THRESHOLD

logger = logging.getLogger(__name__)

class DifficultyStrategy(ABC):
    @abstractmethod
    def get_num_chunks(self) -> int:
        pass

    @abstractmethod
    def get_prompt_instructions(self) -> str:
        pass

    @abstractmethod
    def validate_question(self, data: dict) -> None:
        pass

class EasyStrategy(DifficultyStrategy):
    def get_num_chunks(self) -> int:
        return 1

    def get_prompt_instructions(self) -> str:
        return (
            "Generate a direct factual/definition question testing one-concept understanding. "
            "Do not require unnecessary reasoning or multi-chunk synthesis. Exactly one correct answer."
        )

    def validate_question(self, data: dict) -> None:
        if len(data.get("source_chunk_ids", [])) > 1:
            raise ValueError("Easy questions should not claim multi-chunk evidence")

class MediumStrategy(DifficultyStrategy):
    def get_num_chunks(self) -> int:
        return 2

    def get_prompt_instructions(self) -> str:
        return (
            "Generate an application, comparison, cause/effect, or interpretation question. "
            "The answer must require understanding rather than simple copying. "
            "Combine information from the provided text where appropriate."
        )

    def validate_question(self, data: dict) -> None:
        pass

class HardStrategy(DifficultyStrategy):
    def get_num_chunks(self) -> int:
        return 4

    def get_prompt_instructions(self) -> str:
        return (
            "Generate a synthesis, multi-step reasoning, or comparison question across evidence. "
            "Apply concepts to an unfamiliar scenario and integrate multiple concepts. "
            "The answer must remain completely grounded in the retrieved material."
        )

    def validate_question(self, data: dict) -> None:
        pass

def get_difficulty_strategy(difficulty: str) -> DifficultyStrategy:
    difficulty = difficulty.lower()
    if difficulty == "easy":
        return EasyStrategy()
    elif difficulty == "medium":
        return MediumStrategy()
    elif difficulty == "hard":
        return HardStrategy()
    else:
        raise ValueError(f"Invalid difficulty: {difficulty}")

class QuizGenerator:
    def __init__(self, retriever: Retriever, llm: LLMProvider):
        self.retriever = retriever
        self.llm = llm

    def generate_quiz(self, user_id: int, topic: str, difficulty: str = "medium", num_questions: int = 1, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates a quiz with multiple questions for a given topic and difficulty.
        Returns a dictionary containing success status, quiz_id if successful, or refusal reason.
        """
        strategy = get_difficulty_strategy(difficulty)
        
        # Retrieve chunks based on difficulty strategy
        top_k = strategy.get_num_chunks()
        
        chunks = []
        is_all_topics = (topic == "All Topics")

        # Document-topic-specific retrieval strategy for structural topics
        if filename:
            from app.vector_store import load_index
            try:
                # Load the index containing recently uploaded documents
                _, v1_chunks, _ = load_index()
                doc_chunks = [c for c in v1_chunks if c.get("filename") == filename]
                
                if doc_chunks:
                    if is_all_topics:
                        doc_chunks.sort(key=lambda x: x["chunk_id"])
                        chunks = doc_chunks[:top_k * 2]
                        for c in chunks:
                            c["score"] = 1.0  # bypass grounding gate for valid doc
                    else:
                        # Exact structural heading match
                        exact_chunks = [c for c in doc_chunks if c.get("heading") == topic]
                        if exact_chunks:
                            exact_chunks.sort(key=lambda x: x["chunk_id"])
                            chunks = exact_chunks[:top_k * 2]
                            for c in chunks:
                                c["score"] = 1.0  # bypass grounding gate for structural match
            except Exception as e:
                logger.warning(f"Document-topic-specific retrieval failed: {e}")

        # Fallback to Core Brain retrieval if not found via specific strategy
        if not chunks:
            chunks = self.retriever.retrieve(topic, top_k=top_k, filename=filename)

        # Grounding Gate
        if not chunks:
            return {
                "success": False,
                "reason": "INSUFFICIENT_SOURCE_CONTEXT",
                "message": "I couldn't find enough information about this topic in your uploaded material."
            }

        if not is_all_topics and chunks[0].get("score", 0) < INITIAL_GROUNDING_THRESHOLD:
            return {
                "success": False,
                "reason": "INSUFFICIENT_SOURCE_CONTEXT",
                "message": "I couldn't find enough information about this topic in your uploaded material."
            }
            
        quiz_id = create_quiz(user_id, difficulty)
            
        generated_questions = []
        
        for _ in range(num_questions):
            question = self._generate_single_question(topic, difficulty, strategy, chunks, generated_questions)
            if not question:
                raise RuntimeError("Failed to generate a valid question after maximum retries.")
                
            add_question(
                quiz_id=quiz_id,
                question_text=question["question"],
                question_type=question["question_type"],
                difficulty=question["difficulty"],
                correct_answer=question["correct_answer"],
                options=question["options"],
                explanation=question["explanation"],
                topic=question["topic"],
                source_metadata=question["source_metadata"]
            )
            generated_questions.append(question["question"])
                
        return {
            "success": True,
            "quiz_id": quiz_id,
            "message": "Quiz generated successfully."
        }
        
    def _generate_single_question(
        self, 
        topic: str, 
        difficulty: str, 
        strategy: DifficultyStrategy,
        chunks: List[Dict[str, Any]], 
        previous_questions: List[str]
    ) -> Optional[Dict[str, Any]]:
        valid_chunk_ids = {c["chunk_id"] for c in chunks if "chunk_id" in c}
        
        context_text = "\n\n".join([f"Chunk ID: {c.get('chunk_id')}\nText: {c.get('text')}" for c in chunks])
        
        prev_q_prompt = ""
        if previous_questions:
            prev_q_prompt = "DO NOT generate questions similar to these previously generated ones:\n"
            for q in previous_questions:
                prev_q_prompt += f"- {q}\n"
        
        prompt = f"""You are an educational quiz generator.
Generate a multiple choice question based ONLY on the provided context.
Topic: {topic}
Difficulty: {difficulty}

{strategy.get_prompt_instructions()}

{prev_q_prompt}

Context:
{context_text}

Output MUST be a valid JSON object with the following fields exactly:
- "question" (string)
- "question_type" (must be exactly "MCQ")
- "difficulty" (string: {difficulty})
- "options" (array of exactly 4 unique strings)
- "correct_answer" (string, must be character-for-character identical to exactly one string in the "options" array)
- "explanation" (string)
- "topic" (string, max 3 words)
- "source_chunk_ids" (array of integer Chunk IDs used to create this question. MUST be chosen ONLY from these valid IDs: {list(valid_chunk_ids)})

Do not include markdown blocks or any other text outside the JSON. Return only the JSON object.
"""
        
        for attempt in range(3):
            try:
                response = self.llm.generate(prompt, temperature=0.7)
                
                # Cleanup markdown
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                elif response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                response = response.strip()
                
                data = json.loads(response)
                
                if not isinstance(data, dict):
                    raise ValueError("JSON must be an object")
                
                required_fields = ["question", "question_type", "difficulty", "options", "correct_answer", "explanation", "topic", "source_chunk_ids"]
                for f in required_fields:
                    if f not in data:
                        raise ValueError(f"Missing field: {f}")
                        
                if data["question_type"] != "MCQ":
                    raise ValueError("question_type must be MCQ")
                    
                if not isinstance(data["options"], list) or len(data["options"]) != 4:
                    raise ValueError("options must be a list of exactly 4 items")
                    
                if len(set(data["options"])) != 4:
                    raise ValueError("options must not contain duplicates")
                    
                if data["correct_answer"] not in data["options"]:
                    raise ValueError("correct_answer must be exactly one of the options")
                    
                topic_words = data["topic"].split()
                if len(topic_words) > 3 or len(topic_words) == 0:
                    raise ValueError("topic must be between 1 and 3 words")
                    
                if not isinstance(data["source_chunk_ids"], list) or not data["source_chunk_ids"]:
                    raise ValueError("source_chunk_ids must be a non-empty list")
                    
                for cid in data["source_chunk_ids"]:
                    if cid not in valid_chunk_ids:
                        raise ValueError(f"hallucinated source_chunk_id: {cid}")
                
                if data["difficulty"] != difficulty:
                    raise ValueError(f"Generated difficulty '{data['difficulty']}' does not match requested '{difficulty}'")
                    
                strategy.validate_question(data)
                
                # Provenance mapping
                source_metadata = [c for c in chunks if c.get("chunk_id") in data["source_chunk_ids"]]
                data["source_metadata"] = source_metadata
                
                return data
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
                
        return None
