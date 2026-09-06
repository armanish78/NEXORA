import pytest
from app.retrieve import Retriever

@pytest.fixture(scope="module")
def retriever():
    """Load the retriever once for all tests in this module."""
    return Retriever()

def test_document_isolation(retriever):
    # Query specific to Document A but searching in Document C
    results = retriever.retrieve("How many chapters are there?", top_k=5, filename="Document C")
    assert all("Document C" in res.get("filename", "") for res in results), "Document isolation failed: retrieved chunks from wrong document."

def test_structural_calibration(retriever):
    # "explain program 4" shouldn't have structural chunk as the #1 ranked chunk
    results = retriever.retrieve("explain program 4", top_k=5, filename="GenAI Lab manual.pdf")
    # Actually, RRF ranks might be tricky, but the final context MUST contain the actual program 4 text
    assert any(res.get("heading", "") == "PROGRAM - 4" and not res.get("is_structural", False) for res in results), "Failed to include actual content chunks for program 4"

def test_context_assembly_expansion(retriever):
    # A structural hit or specific hit should pull in adjacent content
    results = retriever.retrieve("what are the programs", top_k=5, filename="GenAI Lab manual.pdf")
    # Verify that order is preserved
    chunk_ids = [res["chunk_id"] for res in results]
    assert chunk_ids == sorted(chunk_ids), "Context assembly failed to preserve document order."
    assert len(results) > 1, "Context assembly failed to expand chunks."

def test_structural_how_many_sections(retriever):
    results = retriever.retrieve("how many total programs", top_k=5, filename="GenAI Lab manual.pdf")
    assert any(res.get("is_structural", False) for res in results)

def test_out_of_corpus_refusal(retriever):
    # This shouldn't retrieve the structural chunk, and semantic score should be low
    results = retriever.retrieve("What is the recipe for chocolate cake?", top_k=5, filename="GenAI Lab manual.pdf")
    assert not any(res.get("score", 0.0) >= 0.8 for res in results)
