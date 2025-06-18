"""
Unit tests for stats.services.stats_service
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.stats.services import stats_service
from src.stats.models_dto import WorkoutStatResponseItemSchema, UserWorkoutStatsResponseSchema
from src.stats.queue_messages import WorkoutPerformedMessage, WorkoutPerformedExerciseSchema


class TestStoreWorkoutStat:
    """Test storing workout statistics"""

    @patch("src.stats.services.stats_service.db_session")
    @patch("src.stats.services.stats_service.WorkoutStatModel")
    def test_store_workout_stat_success(self, mock_stat_model, mock_db_session):
        """Test successful workout stat storage"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        exercise = WorkoutPerformedExerciseSchema(exercise_id=1)
        
        message = WorkoutPerformedMessage(
            user_email="test@example.com",
            workout_id=1,
            performed_at=datetime(2024, 1, 1, 10, 0, 0),
            exercises=[exercise]
        )
        
        stats_service.store_workout_stat(message)
        
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
        mock_db.close.assert_called()

    @patch("src.stats.services.stats_service.db_session")
    @patch("src.stats.services.stats_service.WorkoutStatModel")
    def test_store_workout_stat_database_error(self, mock_stat_model, mock_db_session):
        """Test storing workout stat with database error"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.commit.side_effect = Exception("Database error")
        
        exercise = WorkoutPerformedExerciseSchema(exercise_id=1)
        
        message = WorkoutPerformedMessage(
            user_email="test@example.com",
            workout_id=1,
            performed_at=datetime(2024, 1, 1, 10, 0, 0),
            exercises=[exercise]
        )
        
        with pytest.raises(Exception):
            stats_service.store_workout_stat(message)
        
        mock_db.rollback.assert_called()
        mock_db.close.assert_called()

    @patch("src.stats.services.stats_service.db_session")
    @patch("src.stats.services.stats_service.WorkoutStatModel")
    def test_store_workout_stat_empty_exercises(self, mock_stat_model, mock_db_session):
        """Test storing workout stat with empty exercises list"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        message = WorkoutPerformedMessage(
            user_email="test@example.com",
            workout_id=1,
            performed_at=datetime(2024, 1, 1, 10, 0, 0),
            exercises=[]
        )
        
        stats_service.store_workout_stat(message)
        
        # Should not add any stats but still complete successfully
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()
        mock_db.close.assert_called()

    @patch("src.stats.services.stats_service.db_session")
    @patch("src.stats.services.stats_service.WorkoutStatModel")
    def test_store_workout_stat_multiple_exercises(self, mock_stat_model, mock_db_session):
        """Test storing workout stat with multiple exercises"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        exercises = [
            WorkoutPerformedExerciseSchema(exercise_id=1),
            WorkoutPerformedExerciseSchema(exercise_id=2),
            WorkoutPerformedExerciseSchema(exercise_id=3)
        ]
        
        message = WorkoutPerformedMessage(
            user_email="test@example.com",
            workout_id=1,
            performed_at=datetime(2024, 1, 1, 10, 0, 0),
            exercises=exercises
        )
        
        stats_service.store_workout_stat(message)
        
        assert mock_db.add.call_count == 3
        mock_db.commit.assert_called()
        mock_db.close.assert_called()


class TestGetUserWorkoutStats:
    """Test getting user workout statistics"""

    @patch("src.stats.services.stats_service.db_session")
    @patch("src.stats.services.stats_service.WorkoutStatModel")
    def test_get_user_workout_stats_success(self, mock_stat_model, mock_db_session):
        """Test successful retrieval of user workout stats"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        mock_stat = MagicMock()
        mock_stat.exercise_id = 1
        mock_stat.workout_id = 1
        mock_stat.performed_timestamp = datetime(2024, 1, 1, 10, 0, 0)
        mock_stat.reps = None
        mock_stat.weight = None
        mock_stat.duration_seconds = None
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_stat]
        
        with patch("src.stats.services.stats_service.WorkoutStatResponseItemSchema.from_orm") as mock_from_orm:
            mock_response_item = WorkoutStatResponseItemSchema(
                exercise_id=1,
                workout_id=1,
                performed_timestamp=datetime(2024, 1, 1, 10, 0, 0)
            )
            mock_from_orm.return_value = mock_response_item
            
            result = stats_service.get_user_workout_stats("test@example.com")
            
            assert isinstance(result, UserWorkoutStatsResponseSchema)
            assert result.user_email == "test@example.com"
            assert len(result.stats) == 1
            mock_db.close.assert_called()

    @patch("src.stats.services.stats_service.db_session")
    @patch("src.stats.services.stats_service.WorkoutStatModel")
    def test_get_user_workout_stats_empty(self, mock_stat_model, mock_db_session):
        """Test getting workout stats for user with no stats"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        result = stats_service.get_user_workout_stats("test@example.com")
        
        assert result is None
        mock_db.close.assert_called()

    @patch("src.stats.services.stats_service.db_session")
    @patch("src.stats.services.stats_service.WorkoutStatModel")
    def test_get_user_workout_stats_database_error(self, mock_stat_model, mock_db_session):
        """Test getting workout stats with database error"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            stats_service.get_user_workout_stats("test@example.com")
        
        mock_db.close.assert_called()

    @patch("src.stats.services.stats_service.db_session")
    @patch("src.stats.services.stats_service.WorkoutStatModel")
    def test_get_user_workout_stats_multiple_stats(self, mock_stat_model, mock_db_session):
        """Test getting multiple workout stats"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        mock_stats = []
        for i in range(3):
            mock_stat = MagicMock()
            mock_stat.exercise_id = i + 1
            mock_stat.workout_id = i + 1
            mock_stat.performed_timestamp = datetime(2024, 1, i + 1, 10, 0, 0)
            mock_stat.reps = None
            mock_stat.weight = None
            mock_stat.duration_seconds = None
            mock_stats.append(mock_stat)
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_stats
        
        with patch("src.stats.services.stats_service.WorkoutStatResponseItemSchema.from_orm") as mock_from_orm:
            mock_response_items = [
                WorkoutStatResponseItemSchema(
                    exercise_id=i + 1,
                    workout_id=i + 1,
                    performed_timestamp=datetime(2024, 1, i + 1, 10, 0, 0)
                ) for i in range(3)
            ]
            mock_from_orm.side_effect = mock_response_items
            
            result = stats_service.get_user_workout_stats("test@example.com")
            
            assert isinstance(result, UserWorkoutStatsResponseSchema)
            assert result.user_email == "test@example.com"
            assert len(result.stats) == 3
            mock_db.close.assert_called()


class TestEdgeCases:
    """Test edge cases and error conditions"""

    @patch("src.stats.services.stats_service.db_session")
    def test_empty_user_email(self, mock_db_session):
        """Test handling of empty email"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        result = stats_service.get_user_workout_stats("")
        
        assert result is None
        mock_db.close.assert_called()

    @patch("src.stats.services.stats_service.db_session")
    def test_invalid_message_format(self, mock_db_session):
        """Test handling of None message"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        # This will fail at runtime due to AttributeError when trying to access message attributes
        with pytest.raises(AttributeError):
            # Suppress type checker warning for intentional None test
            stats_service.store_workout_stat(None)  # type: ignore
        
        mock_db.close.assert_called()

    def test_message_validation(self):
        """Test WorkoutPerformedMessage validation"""
        # Test valid message
        exercise = WorkoutPerformedExerciseSchema(exercise_id=1)
        message = WorkoutPerformedMessage(
            user_email="test@example.com",
            workout_id=1,
            performed_at=datetime(2024, 1, 1, 10, 0, 0),
            exercises=[exercise]
        )
        assert message.user_email == "test@example.com"
        assert len(message.exercises) == 1
        
        # Test invalid exercise_id - pydantic will raise ValidationError
        with pytest.raises(ValueError):
            # Suppress type checker warning for intentional invalid test
            WorkoutPerformedExerciseSchema(exercise_id="invalid")  # type: ignore
        
        # Test invalid workout_id - pydantic will raise ValidationError  
        with pytest.raises(ValueError):
            # Suppress type checker warning for intentional invalid test
            WorkoutPerformedMessage(
                user_email="test@example.com",
                workout_id="invalid",  # type: ignore
                performed_at=datetime(2024, 1, 1, 10, 0, 0),
                exercises=[exercise]
            )
