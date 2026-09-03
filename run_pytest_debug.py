import pytest
import sys
sys.argv = ["pytest", "tests/test_document_scoping.py", "-k", "test_structural_hit_resolves_to_actual_content", "-s"]
pytest.main()
