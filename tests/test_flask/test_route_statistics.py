#-------------------------
# TEST STATISTICS / PREVISION
#-------------------------
def test_get_planned_prevision_success(mocker, client, auth_headers):
    mock_result = {
        "total_forecast": 500,
        "current_balance": 100,
        "planned_income": 600,
        "planned_outcome": 200
    }

    mocker.patch(
        "FLASK_APP.app.routes.statistics.calculate_planned_user_forecast",
        return_value=mock_result
    )

    response = client.post(
        "/get_planned_prevision",
        headers=auth_headers,
        json={"end_prevision": "2025-12-31"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["Total prevision"] == 500
    assert data["Details"]["Planned income"] == 600


def test_get_planned_prevision_invalid_data(client, auth_headers):
    response = client.post(
        "/get_planned_prevision",
        headers=auth_headers,
        json={}  # mancano campi richiesti
    )
    assert response.status_code == 400


def test_save_money_with_prevision(mocker, client, auth_headers):
    mock_trans = mocker.MagicMock()
    mock_trans.priority_score.value = 3
    mock_trans.transaction_type.value = "outcome"
    mock_trans.is_completed = False

    mocker.patch("FLASK_APP.app.routes.statistics.get_all_plann_trans", return_value=[mock_trans])
    mocker.patch("FLASK_APP.app.routes.statistics.get_all_actual_trans", return_value=[mock_trans])
    mocker.patch("FLASK_APP.app.routes.statistics.calculate_forecast", return_value=50)
    mocker.patch(
        "FLASK_APP.app.routes.statistics.calculate_planned_user_forecast",
        return_value={"total_forecast": 100}
    )

    response = client.post(
        "/save_money_with_prevision",
        headers=auth_headers,
        json={"end_prevision": "2025-12-31"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "can_save_if_deferrable" in data
    assert data["can_save_if_deferrable"] == 100 + 100  # totale mock


def test_low_priority_outcome(mocker, client, auth_headers):
    mock_trans = mocker.MagicMock()
    mock_trans.priority_score.value = 3
    mock_trans.transaction_type.value = "outcome"
    mock_trans.planned_amount = 150

    mocker.patch("FLASK_APP.app.routes.statistics.get_all_plann_trans", return_value=[mock_trans])

    response = client.post("/low_priority_outcome", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json() == {"You can save": 150}


def test_periodic_report(mocker, client, auth_headers):
    mock_trans = mocker.MagicMock()
    mock_trans.is_completed = False
    mock_trans.transaction_type.value = "income"

    mocker.patch("FLASK_APP.app.routes.statistics.get_all_plann_trans", return_value=[mock_trans])
    mocker.patch("FLASK_APP.app.routes.statistics.get_all_actual_trans", return_value=[mock_trans])
    mocker.patch("FLASK_APP.app.routes.statistics.calculate_occurrences", return_value=10)

    response = client.post(
        "/statistic/periodic_report",
        headers=auth_headers,
        json={"end_prevision": "2025-12-31", "days": 30}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "planned_income" in data
    assert data["planned_income"] == [10]


def test_get_actual_prevision_success(mocker, client, auth_headers):
    mock_result = {
        "total_forecast": 800,
        "current_balance": 300,
        "actual_income": 1000,
        "actual_outcome": 200
    }

    mocker.patch(
        "FLASK_APP.app.routes.statistics.calculate__actual_user_forecast",
        return_value=mock_result
    )

    response = client.post(
        "/get_actual_prevision",
        headers=auth_headers,
        json={"end_prevision": "2025-12-31"}
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["Total prevision"] == 800
    assert data["Details"]["Current balance"] == 300
    assert data["Details"]["Actual income"] == 1000
    assert data["Details"]["Actual outcome"] == 200


def test_get_actual_prevision_invalid_data(client, auth_headers):
    response = client.post(
        "/get_actual_prevision",
        headers=auth_headers,
        json={}  # mancano i campi richiesti dal Pydantic schema
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data or "Errors" 