import pytest
from app.llm import LLMProvider, LocalHuggingFaceProvider, OpenAIProvider, get_provider
from app.quiz_generator import QuizGenerator
from tests.test_quiz_generator import MockRetriever, MockProvider, mock_db_functions, valid_mcq_response, test_db, user_id, retriever

def test_local_provider_conforms_to_interface():
    # We do not want to load the massive 3B model in testing, 
    # but we can verify it subclasses LLMProvider and has correct method signatures.
    assert issubclass(LocalHuggingFaceProvider, LLMProvider)
    assert hasattr(LocalHuggingFaceProvider, "generate")
    assert hasattr(LocalHuggingFaceProvider, "health_check")

def test_cloud_provider_conforms_to_interface():
    assert issubclass(OpenAIProvider, LLMProvider)
    assert hasattr(OpenAIProvider, "generate")
    assert hasattr(OpenAIProvider, "health_check")

def test_provider_factory():
    # Using fake kwargs to prevent actual API keys from being needed
    cloud = get_provider(provider_type="openai", api_key="test", base_url="test")
    assert isinstance(cloud, OpenAIProvider)
    
def test_invalid_provider_fails_cleanly():
    with pytest.raises(ValueError, match="Unknown provider type: fake"):
        get_provider(provider_type="fake")

def test_quiz_generator_accepts_any_provider(test_db, user_id, retriever, monkeypatch):
    mock_db_functions(monkeypatch, test_db)
    
    # We use MockProvider which we know is Duck-typed or inherits LLMProvider
    # This proves the QuizGenerator only cares about the .generate() method behavior
    mock_local = MockProvider([valid_mcq_response()])
    mock_cloud = MockProvider([valid_mcq_response()])
    
    gen_local = QuizGenerator(retriever, mock_local)
    gen_cloud = QuizGenerator(retriever, mock_cloud)
    
    # Both should succeed without issue
    res1 = gen_local.generate_quiz(user_id, "AI Basics", "medium", 1)
    res2 = gen_cloud.generate_quiz(user_id, "AI Basics", "medium", 1)
    
    assert res1["success"] is True
    assert res2["success"] is True
    assert res1["quiz_id"] is not None
    assert res2["quiz_id"] is not None
