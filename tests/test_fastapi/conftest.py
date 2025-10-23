import pytest
from fastapi.testclient import TestClient
from FASTAPI_APP.run import app

@pytest.fixture
def client():
    return TestClient(app)