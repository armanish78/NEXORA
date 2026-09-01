from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QAQuery(BaseModel):
    query: str = Field(..., description="The question to ask based on the ingested documents")
    top_k: int = Field(5, description="Number of chunks to retrieve")

class QAResponse(BaseModel):
    success: bool
    answer: Optional[str] = None
    citations: Optional[List[Dict[str, Any]]] = None
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None
    reason: Optional[str] = None

class QuizRequest(BaseModel):
    user_id: int
    topic: str
    difficulty: str = Field("medium", pattern="^(easy|medium|hard)$")
    num_questions: int = Field(1, ge=1, le=5)

class PersonalizedQuizRequest(BaseModel):
    user_id: int
    difficulty: str = Field("medium", pattern="^(easy|medium|hard)$")
    num_questions: int = Field(1, ge=1, le=5)

class QuizResponse(BaseModel):
    success: bool
    quiz_id: Optional[int] = None
    questions: Optional[List[Dict[str, Any]]] = None
    reason: Optional[str] = None

class AnswerSubmission(BaseModel):
    question_id: int
    user_answer: str

class AnswerResponse(BaseModel):
    is_correct: bool
    explanation: str

class HealthResponse(BaseModel):
    status: str
    model: str
