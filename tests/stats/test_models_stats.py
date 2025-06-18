"""
Tests for stats.models_db and stats.models_dto
"""
from src.stats.models_dto import WorkoutStatResponseItemSchema
from src.stats.models_db import WorkoutStatModel

def test_workout_stat_schema():
    stat = WorkoutStatResponseItemSchema(exercise_id=1, workout_id=2, performed_timestamp="2024-01-01T00:00:00Z")
    assert stat.exercise_id == 1
    assert stat.workout_id == 2
    assert stat.performed_timestamp == "2024-01-01T00:00:00Z"

def test_workout_stat_model_repr():
    wsm = WorkoutStatModel(id=1, user_email="a@b.com", exercise_id=1, workout_id=2)
    assert "a@b.com" in repr(wsm)

# Add more tests for all DTOs and models, including __repr__, __eq__, and edge cases.
