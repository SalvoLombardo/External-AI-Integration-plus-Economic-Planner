from fastapi.testclient import TestClient
from FASTAPI_APP.run import app

def test_ai_endpoint_success(mocker, client):
    mock_ai_response = {"result": "AI processed successfully"}
    mocker.patch("FASTAPI_APP.app.services.ai_service.send_to_ai", return_value=mock_ai_response)
    response = client.post("/ai/ai_process", json={"input": "test"})
    assert response.status_code == 200
    assert response.json() == mock_ai_response


def test_ai_endpoint_invalid_task(client):
    response = client.post("/ai/ai_process", json={"user_jwt_token": "token", "task": "invalid", "data": {}})
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid task"