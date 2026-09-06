import pytest
from app.retrieve import Retriever

@pytest.fixture(scope="module")
def retriever():
    """Load the retriever once for all tests in this module to save time."""
    return Retriever()

def test_retriever_initialization(retriever):
    assert retriever.index is not None
    assert retriever.model is not None
    assert retriever.total_chunks > 0

def test_valid_query(retriever):
    results = retriever.retrieve("What is Naive Bayes?", top_k=3)
    assert len(results) == 3
    # Check provenance
    for r in results:
        assert "score" in r
        assert "rank" in r
        assert "text" in r
        assert "chunk_id" in r
        assert "filename" in r

def test_empty_query(retriever):
    with pytest.raises(ValueError, match="Query cannot be empty"):
        retriever.retrieve("", top_k=5)
        
    with pytest.raises(ValueError, match="Query cannot be empty"):
        retriever.retrieve("   \n  ", top_k=5)

def test_invalid_top_k(retriever):
    with pytest.raises(ValueError, match="positive integer"):
        retriever.retrieve("Test", top_k=0)
        
    with pytest.raises(ValueError, match="positive integer"):
        retriever.retrieve("Test", top_k=-5)

def test_top_k_exceeds_index(retriever):
    # Should cap at total_chunks (or slightly less if FAISS drops empty chunks)
    large_k = retriever.total_chunks + 100
    results = retriever.retrieve("Test", top_k=large_k)
    # Since chunks are merged into regions of up to 3 chunks, the number of results can be total_chunks / 3.
    assert len(results) >= retriever.total_chunks * 0.3

def test_missing_index():
    with pytest.raises(FileNotFoundError):
        Retriever(index_path="fake/path.index", metadata_path="fake/path.pkl")
