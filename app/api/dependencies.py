import logging
from app.config import LLM_MODEL_DEFAULT
from app.llm import LocalHuggingFaceProvider
from app.retrieve import Retriever
from app.generator import RAGGenerator
from app.quiz_generator import QuizGenerator
from app.personalization import PersonalizationEngine
from app.answer_evaluator import AnswerEvaluator

logger = logging.getLogger(__name__)

# Global singletons
_provider = None
_retriever = None
_rag_generator = None
_quiz_generator = None
_personalization_engine = None
_answer_evaluator = None

def init_core_brain():
    global _provider, _retriever, _rag_generator, _quiz_generator, _personalization_engine, _answer_evaluator
    logger.info("Initializing Core Brain...")
    
    _provider = LocalHuggingFaceProvider(LLM_MODEL_DEFAULT)
    _retriever = Retriever()
    _rag_generator = RAGGenerator(_retriever, _provider)
    _quiz_generator = QuizGenerator(_retriever, _provider)
    _personalization_engine = PersonalizationEngine(_quiz_generator)
    _answer_evaluator = AnswerEvaluator()
    
    logger.info("Core Brain initialized successfully.")

def get_rag_generator() -> RAGGenerator:
    return _rag_generator

def get_quiz_generator() -> QuizGenerator:
    return _quiz_generator

def get_personalization_engine() -> PersonalizationEngine:
    return _personalization_engine

def get_answer_evaluator() -> AnswerEvaluator:
    return _answer_evaluator

def get_model_name() -> str:
    return LLM_MODEL_DEFAULT
