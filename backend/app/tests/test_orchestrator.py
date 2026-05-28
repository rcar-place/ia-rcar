"""
Testes do orquestrador de mensagens.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.messaging.schedule_checker import is_business_hours, should_ai_respond


def test_business_hours_inside():
    """Testa que 10h em dia útil é horário comercial."""
    with patch("app.services.messaging.schedule_checker.get_current_time_local") as mock_time:
        dt = MagicMock()
        dt.hour = 10
        dt.weekday.return_value = 1  # Terça-feira
        mock_time.return_value = dt
        assert is_business_hours(8, 18) is True


def test_business_hours_outside_night():
    """Testa que 22h é fora do horário comercial."""
    with patch("app.services.messaging.schedule_checker.get_current_time_local") as mock_time:
        dt = MagicMock()
        dt.hour = 22
        dt.weekday.return_value = 1
        mock_time.return_value = dt
        assert is_business_hours(8, 18) is False


def test_business_hours_weekend():
    """Testa que sábado/domingo é fora do horário comercial."""
    with patch("app.services.messaging.schedule_checker.get_current_time_local") as mock_time:
        dt = MagicMock()
        dt.hour = 10
        dt.weekday.return_value = 5  # Sábado
        mock_time.return_value = dt
        assert is_business_hours(8, 18) is False


def test_should_ai_respond_outside_hours():
    """IA deve responder fora do horário comercial."""
    with patch("app.services.messaging.schedule_checker.get_current_time_local") as mock_time:
        dt = MagicMock()
        dt.hour = 20
        dt.weekday.return_value = 1
        mock_time.return_value = dt
        assert should_ai_respond(8, 18) is True


def test_should_ai_not_respond_inside_hours():
    """IA NÃO deve responder dentro do horário comercial."""
    with patch("app.services.messaging.schedule_checker.get_current_time_local") as mock_time:
        dt = MagicMock()
        dt.hour = 9
        dt.weekday.return_value = 2  # Quarta
        mock_time.return_value = dt
        assert should_ai_respond(8, 18) is False
