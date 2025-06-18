"""
Unit tests for fit.services.workout_service
"""
import pytest
from unittest.mock import patch, MagicMock
from src.fit.services import workout_service
from src.fit.models_dto import RegisterWorkoutExerciseSchema, ExerciseResponseSchema

@patch("src.fit.services.workout_service.db_session")
@patch("src.fit.services.workout_service.WorkoutModel")
@patch("src.fit.services.workout_service.UserExerciseHistory")
def test_register_workout(mock_user_exercise_history, mock_workout_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_workout = MagicMock(id=1)
    mock_workout_model.return_value = mock_workout
    exercises = [RegisterWorkoutExerciseSchema(exercise_id=1)]
    mock_user_exercise_history.return_value = MagicMock()
    workout_service.register_workout("user@b.com", exercises)
    mock_db.add.assert_called()
    mock_db.commit.assert_called()
    mock_db.close.assert_called()

@patch("src.fit.services.workout_service.requests.get")
def test_get_exercises_metadata(mock_get):
    mock_get.return_value.json.return_value = [
        {"id": 1, "name": "Pushup", "description": "desc"},
        {"id": 2, "name": "Squat", "description": "desc"}
    ]
    mock_get.return_value.raise_for_status.return_value = None
    exercises = workout_service.get_exercises_metadata([1])
    assert len(exercises) == 1
    assert exercises[0].name == "Pushup"

@patch("src.fit.services.workout_service.db_session")
@patch("src.fit.services.workout_service.WorkoutModel")
@patch("src.fit.services.workout_service.UserExerciseHistory")
@patch("src.fit.services.workout_service.get_exercises_metadata")
def test_get_most_recent_workout_exercises(mock_get_exercises_metadata, mock_user_exercise_history, mock_workout_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_workout = MagicMock(id=1, performed_at=None, created_at=None)
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_workout
    mock_user_exercise_history_instance = MagicMock(exercise_id=1)
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_user_exercise_history_instance]
    mock_get_exercises_metadata.return_value = [ExerciseResponseSchema(id=1, name="Pushup", description="desc")]
    resp = workout_service.get_most_recent_workout_exercises("user@b.com")
    assert resp.id == 1
    assert resp.exercises[0].name == "Pushup"
    mock_db.close.assert_called()

@patch("src.fit.services.workout_service.get_most_recent_workout_exercises")
def test_get_user_next_workout(mock_get_most_recent):
    mock_get_most_recent.return_value = MagicMock()
    resp = workout_service.get_user_next_workout("user@b.com")
    assert resp == mock_get_most_recent.return_value

@patch("src.fit.services.workout_service.db_session")
@patch("src.fit.services.workout_service.WorkoutModel")
@patch("src.fit.services.workout_service.rabbitmq_service")
def test_perform_workout_success(mock_rabbitmq_service, mock_workout_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_workout = MagicMock(id=1, user_email="user@b.com", performed=False, exercises=[MagicMock(exercise_id=1)])
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_workout
    mock_rabbitmq_service.publish_workout_performed_event.return_value = True
    workout_service.perform_workout(1, "user@b.com")
    mock_db.commit.assert_called()
    mock_db.close.assert_called()
    mock_rabbitmq_service.publish_workout_performed_event.assert_called()

@patch("src.fit.services.workout_service.db_session")
@patch("src.fit.services.workout_service.WorkoutModel")
def test_perform_workout_not_found(mock_workout_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = None
    with pytest.raises(ValueError):
        workout_service.perform_workout(1, "user@b.com")
    mock_db.rollback.assert_called()
    mock_db.close.assert_called()

@patch("src.fit.services.workout_service.db_session")
@patch("src.fit.services.workout_service.WorkoutModel")
def test_perform_workout_already_performed(mock_workout_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_workout = MagicMock(id=1, user_email="user@b.com", performed=True, exercises=[])
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_workout
    with pytest.raises(ValueError):
        workout_service.perform_workout(1, "user@b.com")
    mock_db.rollback.assert_called()
    mock_db.close.assert_called()
