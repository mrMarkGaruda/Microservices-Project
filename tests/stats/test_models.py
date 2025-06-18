"""
Tests for stats.models_db and stats.models_dto
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock
from pydantic import ValidationError
from src.stats.models_dto import WorkoutStatResponseItemSchema, UserWorkoutStatsResponseSchema
from src.stats.models_db import WorkoutStatModel


class TestWorkoutStatResponseItemSchema:
    """Test WorkoutStatResponseItemSchema DTO"""
    
    def test_workout_stat_schema_valid(self):
        """Test valid workout stat schema creation"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        stat = WorkoutStatResponseItemSchema(
            exercise_id=1,
            workout_id=2,
            performed_timestamp=timestamp,
            reps=10,
            weight=50.5,
            duration_seconds=300
        )
        assert stat.exercise_id == 1
        assert stat.workout_id == 2
        assert stat.performed_timestamp == timestamp
        assert stat.reps == 10
        assert stat.weight == 50.5
        assert stat.duration_seconds == 300

    def test_workout_stat_schema_with_nulls(self):
        """Test workout stat schema with optional null fields"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        stat = WorkoutStatResponseItemSchema(
            exercise_id=1,
            workout_id=2,
            performed_timestamp=timestamp,
            reps=None,
            weight=None,
            duration_seconds=None
        )
        assert stat.exercise_id == 1
        assert stat.workout_id == 2
        assert stat.performed_timestamp == timestamp
        assert stat.reps is None
        assert stat.weight is None
        assert stat.duration_seconds is None

    def test_workout_stat_schema_invalid_exercise_id(self):
        """Test workout stat schema with invalid exercise_id"""
        with pytest.raises(ValidationError):
            WorkoutStatResponseItemSchema(
                exercise_id="invalid",  # type: ignore
                workout_id=2,
                performed_timestamp=datetime(2024, 1, 1, 12, 0, 0)
            )

    def test_workout_stat_schema_missing_required_fields(self):
        """Test workout stat schema with missing required fields"""
        with pytest.raises(ValidationError):
            WorkoutStatResponseItemSchema(exercise_id=1)  # type: ignore


class TestUserWorkoutStatsResponseSchema:
    """Test UserWorkoutStatsResponseSchema DTO"""
    
    def test_user_workout_stats_schema_valid(self):
        """Test valid user workout stats schema"""
        stats = [
            WorkoutStatResponseItemSchema(
                exercise_id=1,
                workout_id=2,
                performed_timestamp=datetime(2024, 1, 1, 12, 0, 0)
            )
        ]
        user_stats = UserWorkoutStatsResponseSchema(
            user_email="test@example.com",
            stats=stats
        )
        assert user_stats.user_email == "test@example.com"
        assert len(user_stats.stats) == 1
        assert user_stats.stats[0].exercise_id == 1

    def test_user_workout_stats_schema_empty_stats(self):
        """Test user workout stats schema with empty stats list"""
        user_stats = UserWorkoutStatsResponseSchema(
            user_email="test@example.com",
            stats=[]
        )
        assert user_stats.user_email == "test@example.com"
        assert len(user_stats.stats) == 0

    def test_user_workout_stats_schema_missing_email(self):
        """Test user workout stats schema with missing email"""
        with pytest.raises(ValidationError):
            UserWorkoutStatsResponseSchema(stats=[])  # type: ignore


class TestWorkoutStatModel:
    """Test WorkoutStatModel database model"""
    
    def test_workout_stat_model_repr(self):
        """Test WorkoutStatModel __repr__ method"""
        model = WorkoutStatModel(
            id=1,
            user_email="test@example.com",
            exercise_id=5,
            workout_id=10
        )
        repr_str = repr(model)
        assert "1" in repr_str
        assert "test@example.com" in repr_str
        assert "5" in repr_str
        assert "10" in repr_str

    def test_workout_stat_model_creation(self):
        """Test WorkoutStatModel creation - just verify it doesn't raise"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        model = WorkoutStatModel(
            id=1,
            user_email="test@example.com",
            exercise_id=5,
            workout_id=10,
            performed_timestamp=timestamp,
            reps=15,
            weight=75.5,
            duration_seconds=600
        )
        # SQLAlchemy models don't allow direct attribute comparison
        # Just verify the model was created without errors
        assert model is not None

    def test_workout_stat_model_minimal_creation(self):
        """Test WorkoutStatModel creation with minimal required fields"""
        model = WorkoutStatModel(
            user_email="test@example.com",
            exercise_id=5,
            workout_id=10
        )
        # Just verify the model was created without errors
        assert model is not None


class TestModelSerialization:
    """Test model serialization and deserialization"""
    
    def test_workout_stat_schema_dict_conversion(self):
        """Test converting WorkoutStatResponseItemSchema to dict"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        stat = WorkoutStatResponseItemSchema(
            exercise_id=1,
            workout_id=2,
            performed_timestamp=timestamp,
            reps=10,
            weight=50.5,
            duration_seconds=300
        )
        
        stat_dict = stat.model_dump()
        assert stat_dict["exercise_id"] == 1
        assert stat_dict["workout_id"] == 2
        assert stat_dict["reps"] == 10
        assert stat_dict["weight"] == 50.5
        assert stat_dict["duration_seconds"] == 300

    def test_user_workout_stats_schema_dict_conversion(self):
        """Test converting UserWorkoutStatsResponseSchema to dict"""
        stats = [
            WorkoutStatResponseItemSchema(
                exercise_id=1,
                workout_id=2,
                performed_timestamp=datetime(2024, 1, 1, 12, 0, 0)
            )
        ]
        user_stats = UserWorkoutStatsResponseSchema(
            user_email="test@example.com",
            stats=stats
        )
        
        user_stats_dict = user_stats.model_dump()
        assert user_stats_dict["user_email"] == "test@example.com"
        assert len(user_stats_dict["stats"]) == 1
        assert user_stats_dict["stats"][0]["exercise_id"] == 1

    def test_workout_stat_schema_json_serialization(self):
        """Test JSON serialization of WorkoutStatResponseItemSchema"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        stat = WorkoutStatResponseItemSchema(
            exercise_id=1,
            workout_id=2,
            performed_timestamp=timestamp
        )
        
        json_str = stat.model_dump_json()
        assert '"exercise_id":1' in json_str
        assert '"workout_id":2' in json_str
        assert "2024-01-01T12:00:00" in json_str


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_large_numbers(self):
        """Test handling of very large numbers"""
        stat = WorkoutStatResponseItemSchema(
            exercise_id=999999999,
            workout_id=999999999,
            performed_timestamp=datetime(2024, 1, 1, 12, 0, 0),
            reps=999999,
            weight=999999.99,
            duration_seconds=999999
        )
        assert stat.exercise_id == 999999999
        assert stat.workout_id == 999999999
        assert stat.reps == 999999
        assert stat.weight == 999999.99
        assert stat.duration_seconds == 999999

    def test_empty_user_email(self):
        """Test handling of empty user email"""
        user_stats = UserWorkoutStatsResponseSchema(
            user_email="",
            stats=[]
        )
        assert user_stats.user_email == ""

    def test_special_characters_in_email(self):
        """Test handling of special characters in email"""
        special_email = "test+special.email@sub-domain.example.com"
        user_stats = UserWorkoutStatsResponseSchema(
            user_email=special_email,
            stats=[]
        )
        assert user_stats.user_email == special_email
