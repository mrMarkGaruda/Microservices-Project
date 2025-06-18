"""
Unit tests for stats.services.stats_service
"""
import pytest
from unittest.mock import patch, MagicMock
from src.stats.services import stats_service

def test_store_workout_stat(monkeypatch):
    with patch("src.stats.services.stats_service.db_session") as mock_db_session:
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        message = MagicMock(user_email="a@b.com", workout_id=1, performed_at="2024-01-01T00:00:00Z", exercises=[MagicMock(exercise_id=1)])
        stats_service.store_workout_stat(message)
        mock_db.commit.assert_called()
        mock_db.close.assert_called()

# Add more tests for get_user_workout_stats, and all other functions, including error and edge cases.
