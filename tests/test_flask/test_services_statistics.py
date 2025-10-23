import pytest
from datetime import datetime, date, timedelta
from types import SimpleNamespace
from FLASK_APP.app.service.statistics_service import calculate_forecast
from FLASK_APP.app.schemas.statistics_schemas import GetOnlyDateSchema


def test_calculate_forecast_non_recurring_planned():
    trans = SimpleNamespace(
        planned_amount=100,
        planned_date_start=date(2025, 1, 1),
        recurring=False,
    )
    validated = GetOnlyDateSchema(end_prevision=date(2025, 12, 31))

    result = calculate_forecast(trans, validated, "planned", today=date(2025, 6, 1))

    assert result == 100  # perché la data è entro la fine periodo



def test_calculate_forecast_non_recurring_future():
    trans = SimpleNamespace(
        planned_amount=100,
        planned_date_start=date(2026, 1, 1),
        recurring=False,
    )
    validated = GetOnlyDateSchema(end_prevision=date(2025, 12, 31))

    result = calculate_forecast(trans, validated, "planned", today=date(2025, 6, 1))

    assert result == 0  # perché parte dopo la fine del periodo




def test_calculate_forecast_daily_recurring():
    trans = SimpleNamespace(
        planned_amount=10,
        planned_date_start=date(2025, 1, 1),
        recurring=True,
        frequency=SimpleNamespace(value="daily"),
    )
    validated = GetOnlyDateSchema(end_prevision=date(2025, 1, 10))

    result = calculate_forecast(trans, validated, "planned", today=date(2025, 1, 5))
    assert result > 0



def test_calculate_forecast_weekly_recurring():
    trans = SimpleNamespace(
        planned_amount=100,
        planned_date_start=date(2025, 1, 1),
        recurring=True,
        frequency=SimpleNamespace(value="weekly"),
    )
    validated = GetOnlyDateSchema(end_prevision=date(2025, 3, 1))

    result = calculate_forecast(trans, validated, "planned", today=date(2025, 1, 10))
    assert result >= 0




def test_calculate_forecast_monthly_recurring():
    trans = SimpleNamespace(
        planned_amount=200,
        planned_date_start=date(2025, 1, 1),
        recurring=True,
        frequency=SimpleNamespace(value="monthly"),
    )
    validated = GetOnlyDateSchema(end_prevision=date(2025, 6, 1))

    result = calculate_forecast(trans, validated, "planned", today=date(2025, 3, 1))
    assert result >= 0




def test_calculate_forecast_yearly_recurring():
    trans = SimpleNamespace(
        planned_amount=1000,
        planned_date_start=date(2020, 1, 1),
        recurring=True,
        frequency=SimpleNamespace(value="yearly"),
    )
    validated = GetOnlyDateSchema(end_prevision=date(2026, 1, 1))

    result = calculate_forecast(trans, validated, "planned", today=date(2025, 1, 1))
    assert result >= 0



import pytest

def test_calculate_forecast_invalid_type():
    trans = SimpleNamespace(
        planned_amount=100,
        planned_date_start=date(2025, 1, 1),
        recurring=False,
    )
    validated = GetOnlyDateSchema(end_prevision=date(2025, 12, 31))

    with pytest.raises(ValueError):
        calculate_forecast(trans, validated, "invalid")



def test_calculate_forecast_no_start_date():
    trans = SimpleNamespace(
        planned_amount=100,
        planned_date_start=None,
        recurring=False,
    )
    validated = GetOnlyDateSchema(end_prevision=date(2025, 12, 31))

    result = calculate_forecast(trans, validated, "planned")
    assert result == 0