import pytest
from app.llm import LLMProvider, get_provider, OpenAIProvider
from app.generator import RAGGenerator

class MockProvider(LLMProvider):
    def generate(self, prompt, temperature=0.0, max_tokens=512):
        if "moon" in prompt:
            return "The provided documents do not contain sufficient information."
        return "Naive Bayes uses Bayes theorem. [S1] It assumes independence. [S2] Fake cite [S99]."
    def health_check(self): return True

class MockRetriever:
    def retrieve(self, query, top_k=5, filename=None):
        if "moon" in query: return []
        return [
            {"chunk_id": 1, "filename": "doc1.pdf", "page": 1, "text": "Bayes theorem.", "score": 0.99},
            {"chunk_id": 2, "filename": "doc2.pdf", "page": 5, "text": "Independence.", "score": 0.99}
        ]

@pytest.fixture
def generator():
    return RAGGenerator(MockRetriever(), MockProvider())

def test_prompt_generation(generator):
    chunks = [{"text": "A"}, {"text": "B"}]
    prompt = generator.generate_prompt("Q?", chunks)
    assert "[S1]\nContent: A" in prompt
    assert "[S2]\nContent: B" in prompt
    assert "=== QUESTION ===\nQ?" in prompt

def test_strict_grounding_prompt_enforcement(generator):
    """
    Regression test from Phase 29:
    Ensures that the strict refusal instruction remains in the prompt.
    Removing this instruction causes Qwen3B to hallucinate from outside knowledge
    when retrieved chunks are insufficient.
    """
    prompt = generator.generate_prompt("Test?", [])
    assert "If the answer is not contained in the context, explicitly state: 'The provided documents do not contain sufficient information.'" in prompt
    assert "Do not use outside knowledge. Do not invent facts." in prompt

def test_citation_parsing(generator):
    chunks = [
        {"filename": "a.pdf", "page": 1},
        {"filename": "b.pdf", "page": 2}
    ]
    raw = "Fact 1 [S1]. Fact 2 [S2]. Fact 3 [S3]. [S0]."
    final, used = generator.parse_citations(raw, chunks)
    assert final == "Fact 1 [a.pdf, Page 1]. Fact 2 [b.pdf, Page 2]. Fact 3 [S3]. [S0]."
    assert len(used) == 2

def test_generate_answer(generator):
    res = generator.generate("How does it work?")
    assert "[doc1.pdf, Page 1]" in res["answer"]
    assert "[doc2.pdf, Page 5]" in res["answer"]
    assert "[S99]" in res["answer"] # Invalid citation untouched
    assert len(res["used_chunks"]) == 2
    
def test_insufficient_context(generator):
    res = generator.generate("moon")
    assert res["answer"] == "The provided documents do not contain sufficient information."
    assert res["used_chunks"] == []

def test_get_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "test")
    p = get_provider()
    assert isinstance(p, OpenAIProvider)
    assert p.api_key == "test"
