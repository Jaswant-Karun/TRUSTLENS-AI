import os
import pytest

os.environ["TESTING"] = "true"

@pytest.fixture(autouse=True, scope="session")
def setup_test_environment():
    os.environ["TESTING"] = "true"
    yield
