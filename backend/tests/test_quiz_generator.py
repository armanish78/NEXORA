import pytest
import tempfile
import os
import json
from app.quiz_generator import QuizGenerator, get_difficulty_strategy
from app.database import initialize_db, create_user, get_db_connection

class MockRetriever:
    def __init__(self):
        self.last_top_k = None
        
    def retrieve(self, query, top_k=5, filename=None):
        self.last_top_k = top_k
        if query == "empty_topic":
            return []
        
        # return exactly top_k chunks so we can test the strategy retrieved the right amount
        chunks = [
            {"chunk_id": 101, "text": "Chunk 1", "filename": "doc1.pdf", "page": 1, "score": 0.5},
            {"chunk_id": 102, "text": "Chunk 2", "filename": "doc1.pdf", "page": 1, "score": 0.5},
            {"chunk_id": 103, "text": "Chunk 3", "filename": "doc1.pdf", "page": 1, "score": 0.5},
            {"chunk_id": 104, "text": "Chunk 4", "filename": "doc1.pdf", "page": 1, "score": 0.5},
        ]
        return chunks[:top_k]

class MockProvider:
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0
        self.last_prompt = None
        
    def generate(self, prompt, temperature=0.0, max_tokens=512):
        self.last_prompt = prompt
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
            self.call_count += 1
            return resp
        return self.responses[-1]
        
    def health_check(self):
        return True

@pytest.fixture
def test_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    initialize_db(path)
    yield path
    os.unlink(path)

@pytest.fixture
def user_id(test_db):
    return create_user(test_db)

@pytest.fixture
def retriever():
    return MockRetriever()

def mock_db_functions(monkeypatch, test_db):
    def mock_create_quiz(*args, **kwargs):
        kwargs['db_path'] = test_db
        return __import__("app.database", fromlist=["create_quiz"]).create_quiz(*args, **kwargs)
        
    def mock_add_question(*args, **kwargs):
        kwargs['db_path'] = test_db
        return __import__("app.database", fromlist=["add_question"]).add_question(*args, **kwargs)

    monkeypatch.setattr("app.quiz_generator.create_quiz", mock_create_quiz)
    monkeypatch.setattr("app.quiz_generator.add_question", mock_add_question)

def valid_mcq_response(difficulty="medium", source_chunks=[101]):
    return json.dumps({
        "question": "What is AI?",
        "question_type": "MCQ",
        "difficulty": difficulty,
        "options": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "Because.",
        "topic": "AI Basics",
        "source_chunk_ids": source_chunks
    })

# Phase 21 Tests
def test_easy_strategy_retrieval(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    llm = MockProvider([valid_mcq_response(difficulty="easy", source_chunks=[101])])
    generator = QuizGenerator(retriever, llm)
    result = generator.generate_quiz(user_id, "AI Basics", "easy", 1)
    
    # Prove it retrieves 1 chunk
    assert retriever.last_top_k == 1
    # Prove the correct prompt instruction is passed
    assert "direct factual/definition question" in llm.last_prompt

def test_medium_strategy_retrieval(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    llm = MockProvider([valid_mcq_response(difficulty="medium", source_chunks=[101, 102])])
    generator = QuizGenerator(retriever, llm)
    result = generator.generate_quiz(user_id, "AI Basics", "medium", 1)
    quiz_id = result["quiz_id"]
    
    assert retriever.last_top_k == 2
    assert "application, comparison, cause/effect" in llm.last_prompt

def test_hard_strategy_retrieval(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    llm = MockProvider([valid_mcq_response(difficulty="hard", source_chunks=[101, 102, 103, 104])])
    generator = QuizGenerator(retriever, llm)
    result = generator.generate_quiz(user_id, "AI Basics", "hard", 1)
    
    assert retriever.last_top_k == 4
    assert "synthesis, multi-step reasoning, or comparison" in llm.last_prompt

def test_easy_validation_rejects_multiple_chunks(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    # The llm returns 2 chunks for an easy question
    llm = MockProvider([valid_mcq_response(difficulty="easy", source_chunks=[101, 102])] * 3)
    generator = QuizGenerator(retriever, llm)
    with pytest.raises(RuntimeError):
        result = generator.generate_quiz(user_id, "AI Basics", "easy", 1)

def test_generated_difficulty_must_match(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    # The llm returns 'medium' but we requested 'easy'
    llm = MockProvider([valid_mcq_response(difficulty="medium", source_chunks=[101])] * 3)
    generator = QuizGenerator(retriever, llm)
    with pytest.raises(RuntimeError):
        result = generator.generate_quiz(user_id, "AI Basics", "easy", 1)

# Phase 20 Existing Validation Tests (Ensuring regression safety)

def test_valid_mcq_generation(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    llm = MockProvider([valid_mcq_response()])
    generator = QuizGenerator(retriever, llm)
    
    result = generator.generate_quiz(user_id, "AI Basics", "medium", 1)
    quiz_id = result["quiz_id"]
    
    with get_db_connection(test_db) as conn:
        q = conn.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,)).fetchone()
        assert q is not None
        assert q["question_text"] == "What is AI?"
        assert q["difficulty"] == "medium"
        assert q["question_type"] == "MCQ"
        options = json.loads(q["options"])
        assert len(options) == 4
        assert "A" in options
        meta = json.loads(q["source_metadata"])
        assert len(meta) == 1
        assert meta[0]["chunk_id"] == 101
        
        # Verify no user answers
        answers = conn.execute("SELECT * FROM user_answers").fetchall()
        assert len(answers) == 0

def test_invalid_difficulty(retriever):
    llm = MockProvider([])
    generator = QuizGenerator(retriever, llm)
    with pytest.raises(ValueError, match="Invalid difficulty: super_hard"):
        result = generator.generate_quiz(1, "Topic", "super_hard", 1)

def test_retry_exhaustion_on_malformed_json(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    llm = MockProvider(["{ malformed json"] * 3)
    generator = QuizGenerator(retriever, llm)
    
    with pytest.raises(RuntimeError, match="Failed to generate a valid question"):
        result = generator.generate_quiz(user_id, "Topic", "medium", 1)
    
def test_retry_success_after_failure(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    llm = MockProvider(["{ malformed", valid_mcq_response()])
    generator = QuizGenerator(retriever, llm)
    
    result = generator.generate_quiz(user_id, "Topic", "medium", 1)
    quiz_id = result["quiz_id"]
    
    with get_db_connection(test_db) as conn:
        q = conn.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,)).fetchall()
        assert len(q) == 1

def test_not_exactly_4_options(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    bad_resp = json.loads(valid_mcq_response())
    bad_resp["options"] = ["A", "B", "C"] # 3 options
    llm = MockProvider([json.dumps(bad_resp)] * 3)
    generator = QuizGenerator(retriever, llm)
    with pytest.raises(RuntimeError):
        result = generator.generate_quiz(user_id, "Topic", "medium", 1)
    
def test_duplicate_options(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    bad_resp = json.loads(valid_mcq_response())
    bad_resp["options"] = ["A", "A", "C", "D"] # Duplicate
    llm = MockProvider([json.dumps(bad_resp)] * 3)
    generator = QuizGenerator(retriever, llm)
    with pytest.raises(RuntimeError):
        result = generator.generate_quiz(user_id, "Topic", "medium", 1)
    
def test_invalid_correct_answer(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    bad_resp = json.loads(valid_mcq_response())
    bad_resp["correct_answer"] = "E" # Not in options
    llm = MockProvider([json.dumps(bad_resp)] * 3)
    generator = QuizGenerator(retriever, llm)
    with pytest.raises(RuntimeError):
        result = generator.generate_quiz(user_id, "Topic", "medium", 1)
    
def test_missing_required_fields(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    bad_resp = json.loads(valid_mcq_response())
    del bad_resp["difficulty"] # Missing field
    llm = MockProvider([json.dumps(bad_resp)] * 3)
    generator = QuizGenerator(retriever, llm)
    with pytest.raises(RuntimeError):
        result = generator.generate_quiz(user_id, "Topic", "medium", 1)
    
def test_invalid_question_type(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    bad_resp = json.loads(valid_mcq_response())
    bad_resp["question_type"] = "TF" 
    llm = MockProvider([json.dumps(bad_resp)] * 3)
    generator = QuizGenerator(retriever, llm)
    with pytest.raises(RuntimeError):
        result = generator.generate_quiz(user_id, "Topic", "medium", 1)
    
def test_invalid_topic(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    bad_resp = json.loads(valid_mcq_response())
    bad_resp["topic"] = "This is a very long topic exceeding limit"
    llm = MockProvider([json.dumps(bad_resp)] * 3)
    generator = QuizGenerator(retriever, llm)
    with pytest.raises(RuntimeError):
        result = generator.generate_quiz(user_id, "Topic", "medium", 1)
    
def test_hallucinated_source_chunk_id(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    bad_resp = json.loads(valid_mcq_response())
    bad_resp["source_chunk_ids"] = [999] # Hallucinated
    llm = MockProvider([json.dumps(bad_resp)] * 3)
    generator = QuizGenerator(retriever, llm)
    with pytest.raises(RuntimeError):
        result = generator.generate_quiz(user_id, "Topic", "medium", 1)
    
def test_multiple_questions(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    resp1 = json.loads(valid_mcq_response(source_chunks=[101]))
    resp2 = json.loads(valid_mcq_response(source_chunks=[102]))
    resp2["question"] = "What is ML?"
    
    llm = MockProvider([json.dumps(resp1), json.dumps(resp2)])
    generator = QuizGenerator(retriever, llm)
    
    result = generator.generate_quiz(user_id, "Topic", "medium", 2)
    quiz_id = result["quiz_id"]
    
    with get_db_connection(test_db) as conn:
        q = conn.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,)).fetchall()
        assert len(q) == 2
        assert q[0]["question_text"] == "What is AI?"
        assert q[1]["question_text"] == "What is ML?"

def test_empty_retrieval(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    llm = MockProvider([valid_mcq_response()])
    generator = QuizGenerator(retriever, llm)
    result = generator.generate_quiz(user_id, "empty_topic", "medium", 1)
    assert not result["success"]
    assert result["reason"] == "INSUFFICIENT_SOURCE_CONTEXT"

def test_prompt_contains_valid_chunk_ids_and_exact_match(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    llm = MockProvider([valid_mcq_response(source_chunks=[101, 102])])
    generator = QuizGenerator(retriever, llm)
    generator.generate_quiz(user_id, "AI Basics", "medium", 1)
    
    # Verify the hardened rules are present
    assert "MUST be chosen ONLY from these valid IDs: [101, 102]" in llm.last_prompt or "MUST be chosen ONLY from these valid IDs: [102, 101]" in llm.last_prompt
    assert "character-for-character identical to exactly one string in the \"options\" array" in llm.last_prompt
