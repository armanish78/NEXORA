import pytest
from app.generator import RAGGenerator
from app.llm import LLMProvider

class MockE2EProvider(LLMProvider):
    def __init__(self, raw_output):
        self.raw_output = raw_output
        
    def generate(self, prompt, temperature=0.0, max_tokens=512):
        return self.raw_output
        
    def health_check(self): return True

class MockE2ERetriever:
    def __init__(self, chunks):
        self._chunks = chunks
    def retrieve(self, query, top_k=5):
        if "moon" in query:
            return []
        for c in self._chunks:
            c["score"] = 0.99
        return self._chunks

def test_e2e_successful_generation():
    chunks = [{"chunk_id": 1, "filename": "doc1.pdf", "page": 1, "text": "A"}]
    prov = MockE2EProvider("The answer is A. [S1]")
    ret = MockE2ERetriever(chunks)
    gen = RAGGenerator(ret, prov)
    
    res = gen.generate("What is A?")
    assert "The answer is A. [doc1.pdf, Page 1]" in res["answer"]
    assert len(res["used_chunks"]) == 1

def test_e2e_retrieval_failure_graceful_handling():
    chunks = [{"chunk_id": 1, "filename": "doc1.pdf", "page": 1, "text": "A"}]
    prov = MockE2EProvider("Should not be called")
    ret = MockE2ERetriever(chunks)
    gen = RAGGenerator(ret, prov)
    
    res = gen.generate("What is the moon?")
    assert "do not contain sufficient information" in res["answer"]
    assert res["used_chunks"] == []

def test_e2e_invalid_citation_handling():
    chunks = [{"chunk_id": 1, "filename": "doc1.pdf", "page": 1, "text": "A"}]
    prov = MockE2EProvider("Fake fact [S99].")
    ret = MockE2ERetriever(chunks)
    gen = RAGGenerator(ret, prov)
    
    res = gen.generate("What is A?")
    assert "[S99]" in res["answer"] # Remained untouched because it's invalid
    assert res["used_chunks"] == []

def test_e2e_missing_citation():
    chunks = [{"chunk_id": 1, "filename": "doc1.pdf", "page": 1, "text": "A"}]
    prov = MockE2EProvider("I am not citing anything.")
    ret = MockE2ERetriever(chunks)
    gen = RAGGenerator(ret, prov)
    
    res = gen.generate("What is A?")
    assert "[" not in res["answer"]
    assert res["used_chunks"] == []
