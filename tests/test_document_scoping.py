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
