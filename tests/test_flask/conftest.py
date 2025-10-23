import pytest
from FLASK_APP.app import create_app  
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app(testing=True)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_jwt(monkeypatch):
    """Mocka get_jwt_identity per evitare problemi con JWT reali."""
    from flask_jwt_extended import get_jwt_identity
    monkeypatch.setattr("flask_jwt_extended.get_jwt_identity", lambda: 1)
    return lambda: 1

@pytest.fixture
def auth_headers():
    """Restituisce header con un token JWT valido (finto)."""
    return {
        "Authorization": f"Bearer fake-jwt-token"
    }