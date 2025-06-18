"""
Unit tests for coach.fitness_service
"""
import pytest
from unittest.mock import patch, MagicMock
from src.coach import fitness_service

def test_get_all_muscle_groups(monkeypatch):
    with patch("src.coach.fitness_service.db_session") as mock_db_session:
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_mg = MagicMock(id=1, name="Chest", body_part="Upper", description="desc")
        mock_db.query.return_value.all.return_value = [mock_mg]
        result = fitness_service.get_all_muscle_groups()
        assert result[0].name == "Chest"
        mock_db.close.assert_called()

@patch("src.coach.fitness_service.db_session")
@patch("src.coach.fitness_service.MuscleGroupModel")
def test_get_muscle_group_by_id(mock_mg_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_mg = MagicMock(id=1, name="Chest", body_part="Upper", description="desc")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_mg
    result = fitness_service.get_muscle_group_by_id(1)
    # ...assertions as appropriate...
    mock_db.close.assert_called()

# Add more tests for get_exercise_by_id, get_all_exercises, and all other functions, including error and edge cases.
