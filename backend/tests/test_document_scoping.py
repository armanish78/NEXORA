import pytest
from app.retrieve import Retriever

class MockModel:
    def embed(self, texts):
        return [[0.1]*768 for _ in texts]
    def encode(self, text, convert_to_tensor=False, normalize_embeddings=False):
        return [0.1]*768

def setup_mock_retriever(monkeypatch):
    import faiss
    import numpy as np
    
    # Mock chunks from multiple documents
    chunks = [
        {"chunk_id": 0, "filename": "docA.pdf", "text": "Apple is a fruit.", "score": 0.0},
        {"chunk_id": 1, "filename": "docA.pdf", "text": "Apple pie is delicious.", "score": 0.0},
        {"chunk_id": 2, "filename": "docB.pdf", "text": "Banana is yellow.", "score": 0.0},
        {"chunk_id": 3, "filename": "docB.pdf", "text": "Banana bread is good.", "score": 0.0},
        {"chunk_id": 4, "filename": "docC.pdf", "text": "Cherry is red.", "score": 0.0},
    ]
    
    # Mock FAISS index
    index = faiss.IndexFlatIP(768)
    # Add dummy embeddings (all same so order is stable but we can test filtering)
    embeddings = np.ones((5, 768), dtype="float32")
    index.add(embeddings)
    
    monkeypatch.setattr("os.path.exists", lambda p: True)
    
    # Mock load_index
    def mock_load_index(i, m, b):
        return index, chunks, None
    monkeypatch.setattr("app.retrieve.load_index", mock_load_index)
    monkeypatch.setattr("app.retrieve.load_embedding_model", lambda: MockModel())
    
    retriever = Retriever("dummy", "dummy")
    return retriever

def test_document_scoping_doc_a(monkeypatch):
    retriever = setup_mock_retriever(monkeypatch)
    results = retriever.retrieve("query", top_k=5, filename="docA.pdf")
    assert len(results) == 2
    for r in results:
        assert r["filename"] == "docA.pdf"

def test_document_scoping_doc_b(monkeypatch):
    retriever = setup_mock_retriever(monkeypatch)
    results = retriever.retrieve("query", top_k=5, filename="docB.pdf")
    assert len(results) == 2
    for r in results:
        assert r["filename"] == "docB.pdf"

def test_document_scoping_non_existent(monkeypatch):
    retriever = setup_mock_retriever(monkeypatch)
    results = retriever.retrieve("query", top_k=5, filename="does_not_exist.pdf")
    assert len(results) == 0

def test_document_scoping_global(monkeypatch):
    retriever = setup_mock_retriever(monkeypatch)
    results = retriever.retrieve("query", top_k=5, filename=None)
    assert len(results) <= 5
    assert len(results) == 5
    
def test_document_scoping_broad_intent(monkeypatch):
    retriever = setup_mock_retriever(monkeypatch)
    results = retriever.retrieve("What are the important things in this document?", top_k=5, filename="docA.pdf")
    assert len(results) == 2
    for r in results:
        assert r["filename"] == "docA.pdf"

from app.quiz_generator import QuizGenerator
from app.personalization import PersonalizationEngine
from tests.test_quiz_generator import MockProvider, valid_mcq_response, test_db, mock_db_functions, user_id

def test_quiz_generation_scoping(monkeypatch, test_db, user_id):
    mock_db_functions(monkeypatch, test_db)
    retriever = setup_mock_retriever(monkeypatch)
    # The retriever mock will return chunks scoped to filename
    # Doc A has chunks 0, 1.
    llm = MockProvider([valid_mcq_response(difficulty="easy", source_chunks=[0])])
    generator = QuizGenerator(retriever, llm)
    
    # 1. Correct filename succeeds and uses chunks from docA
    result = generator.generate_quiz(user_id, "Apple", "easy", 1, filename="docA.pdf")
    assert result["success"] == True
    
    # 2. Wrong filename fails gracefully because retrieval yields 0 chunks
    llm = MockProvider([valid_mcq_response(difficulty="easy")])
    generator = QuizGenerator(retriever, llm)
    result = generator.generate_quiz(user_id, "Apple", "easy", 1, filename="wrong.pdf")
    assert result["success"] == False
    assert result["reason"] == "INSUFFICIENT_SOURCE_CONTEXT"
    
def test_personalized_quiz_scoping(monkeypatch, test_db, user_id):
    mock_db_functions(monkeypatch, test_db)
    retriever = setup_mock_retriever(monkeypatch)
    llm = MockProvider([valid_mcq_response(difficulty="easy", source_chunks=[0])])
    generator = QuizGenerator(retriever, llm)
    engine = PersonalizationEngine(generator)
    
    # Mock progress to return a weak topic
    monkeypatch.setattr("app.personalization.get_weak_topics", lambda uid, limit: [{"topic": "Apple", "attempts": 5, "accuracy": 20.0}])
    
    # 4. Personalized quiz respects filename scope
    result = engine.generate_personalized_quiz(user_id, "easy", 1, filename="docA.pdf")
    assert result["personalized"] == True
    assert result["selected_topic"] == "Apple"

# =====================================================================
# REQUESTED TESTS
# =====================================================================

def test_1_topics_are_document_scoped(monkeypatch):
    """TEST 1 - TOPICS ARE DOCUMENT SCOPED"""
    # Test GET /documents/{filename}/topics
    from app.api.routes import get_document_topics
    
    # Mock load_index for routes
    def mock_load_index():
        chunks = [
            {"chunk_id": 0, "filename": "document_a.pdf", "heading": "Doc A Heading"},
            {"chunk_id": 1, "filename": "document_b.pdf", "heading": "Doc B Heading"}
        ]
        return None, chunks, None
    monkeypatch.setattr("app.api.routes.load_index", mock_load_index)
    
    res = get_document_topics("document_a.pdf")
    assert res["filename"] == "document_a.pdf"
    assert "Doc A Heading" in res["topics"]
    assert "Doc B Heading" not in res["topics"]

def test_2_wrong_filename(monkeypatch):
    """TEST 2 - WRONG FILENAME"""
    from app.api.routes import get_document_topics
    def mock_load_index():
        chunks = [
            {"chunk_id": 0, "filename": "document_a.pdf", "heading": "Doc A Heading"},
        ]
        return None, chunks, None
    monkeypatch.setattr("app.api.routes.load_index", mock_load_index)
    
    res = get_document_topics("nonexistent.pdf")
    assert res["topics"] == []

def test_3_specific_topic_correct_document(monkeypatch, test_db, user_id):
    """TEST 3 - SPECIFIC TOPIC + CORRECT DOCUMENT"""
    mock_db_functions(monkeypatch, test_db)
    retriever = setup_mock_retriever(monkeypatch)
    # Give the chunk a high enough score to pass grounding
    retriever.chunks[0]["score"] = 0.9 
    
    llm = MockProvider([valid_mcq_response(difficulty="easy", source_chunks=[0])])
    generator = QuizGenerator(retriever, llm)
    
    # docA.pdf has chunks
    result = generator.generate_quiz(user_id, "Apple", "easy", 1, filename="docA.pdf")
    assert result["success"] == True

def test_4_specific_topic_wrong_document(monkeypatch, test_db, user_id):
    """TEST 4 - SPECIFIC TOPIC + WRONG DOCUMENT"""
    mock_db_functions(monkeypatch, test_db)
    retriever = setup_mock_retriever(monkeypatch)
    
    # Mock retrieve to simulate low scores when topics don't match the doc
    original_retrieve = retriever.retrieve
    def mock_retrieve(*args, **kwargs):
        chunks = original_retrieve(*args, **kwargs)
        for c in chunks:
            c["score"] = 0.0
        return chunks
    monkeypatch.setattr(retriever, "retrieve", mock_retrieve)
    
    llm = MockProvider([valid_mcq_response(difficulty="easy", source_chunks=[0])])
    generator = QuizGenerator(retriever, llm)
    
    # docC.pdf exists but doesn't have the topic "Apple" if we actually did semantic search, 
    # but since this is a mock, the mock retriever will return docC chunks. However, their score is 0.0.
    result = generator.generate_quiz(user_id, "Apple", "easy", 1, filename="docC.pdf")
    assert result["success"] == False
    assert result["reason"] == "INSUFFICIENT_SOURCE_CONTEXT"

def test_5_all_topics_correct_document(monkeypatch, test_db, user_id):
    """TEST 5 - ALL TOPICS"""
    mock_db_functions(monkeypatch, test_db)
    retriever = setup_mock_retriever(monkeypatch)
    llm = MockProvider([valid_mcq_response(difficulty="easy", source_chunks=[0])])
    generator = QuizGenerator(retriever, llm)
    
    # "All Topics" should pass grounding even if semantic score is 0.0
    result = generator.generate_quiz(user_id, "All Topics", "easy", 1, filename="docA.pdf")
    assert result["success"] == True

def test_6_all_topics_wrong_filename(monkeypatch, test_db, user_id):
    """TEST 6 - ALL TOPICS WRONG FILENAME"""
    mock_db_functions(monkeypatch, test_db)
    retriever = setup_mock_retriever(monkeypatch)
    llm = MockProvider([valid_mcq_response(difficulty="easy", source_chunks=[0])])
    generator = QuizGenerator(retriever, llm)
    
    result = generator.generate_quiz(user_id, "All Topics", "easy", 1, filename="nonexistent.pdf")
    assert result["success"] == False
    assert result["reason"] == "INSUFFICIENT_SOURCE_CONTEXT"

def test_7_no_cross_document_quiz(monkeypatch, test_db, user_id):
    """TEST 7 - NO CROSS-DOCUMENT QUIZ"""
    mock_db_functions(monkeypatch, test_db)
    retriever = setup_mock_retriever(monkeypatch)
    
    # Attempt to retrieve a topic that only exists in docB, but we are querying docA
    # Simulate low score for chunks in docA because they don't match the topic from docB
    original_retrieve = retriever.retrieve
    def mock_retrieve(*args, **kwargs):
        chunks = original_retrieve(*args, **kwargs)
        for c in chunks:
            c["score"] = 0.1
        return chunks
    monkeypatch.setattr(retriever, "retrieve", mock_retrieve)
    
    llm = MockProvider([valid_mcq_response(difficulty="easy", source_chunks=[0])])
    generator = QuizGenerator(retriever, llm)
    
    # Attempt to retrieve a topic that only exists in docB, but we are querying docA
    # The retriever mock will only return chunks from docA, which have score 0.0
    result = generator.generate_quiz(user_id, "Banana", "easy", 1, filename="docA.pdf")
    assert result["success"] == False
    assert result["reason"] == "INSUFFICIENT_SOURCE_CONTEXT"

