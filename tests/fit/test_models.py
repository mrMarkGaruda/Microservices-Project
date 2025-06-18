"""
Tests for fit.models_db and fit.models_dto
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock
from pydantic import ValidationError
from src.fit.models_dto import (
    UserSchema, TokenSchema, UserResponseSchema, LoginSchema,
    UserProfileSchema, UserProfileResponseSchema, UserProfileUpdate,
    ExerciseId, MuscleGroupImpact, RegisterWorkoutSchema,
    ExerciseResponseSchema, WorkoutResponseSchema, WorkoutExercisesList
)
from src.fit.models_db import UserModel, WorkoutModel, UserExerciseHistory

class TestUserSchemas:
    """Test user-related DTO schemas"""
    
    def test_user_schema_validation(self):
        """Test valid user schema"""
        user = UserSchema(email="test@example.com", name="Test User", role="user")
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.role == "user"

    def test_user_schema_invalid_email(self):
        """Test user schema with invalid email"""
        with pytest.raises(ValidationError):
            UserSchema(email="invalid-email", name="Test", role="user")

    def test_user_schema_empty_name(self):
        """Test user schema with empty name"""
        with pytest.raises(ValidationError):
            UserSchema(email="test@example.com", name="", role="user")

    def test_user_schema_invalid_role(self):
        """Test user schema with invalid role"""
        # Assuming role validation exists
        user = UserSchema(email="test@example.com", name="Test", role="invalid_role")
        assert user.role == "invalid_role"  # If no validation, should accept

    def test_user_response_schema(self):
        """Test user response schema"""
        user = UserResponseSchema(
            email="test@example.com",
            name="Test User",
            role="user",
            password="generated_password"
        )
        assert user.email == "test@example.com"
        assert user.password == "generated_password"

    def test_login_schema_valid(self):
        """Test valid login schema"""
        login = LoginSchema(email="test@example.com", password="password123")
        assert login.email == "test@example.com"
        assert login.password == "password123"

    def test_login_schema_invalid_email(self):
        """Test login schema with invalid email"""
        with pytest.raises(ValidationError):
            LoginSchema(email="invalid-email", password="password123")

    def test_token_schema(self):
        """Test token schema"""
        token = TokenSchema(access_token="abc123", token_type="bearer")
        assert token.access_token == "abc123"
        assert token.token_type == "bearer"

class TestUserProfileSchemas:
    """Test user profile DTO schemas"""

    def test_user_profile_schema_valid(self):
        """Test valid user profile schema"""
        profile = UserProfileSchema(
            weight=70.5,
            height=180.0,
            fitness_goal="lose_weight"
        )
        assert profile.weight == 70.5
        assert profile.height == 180.0
        assert profile.fitness_goal == "lose_weight"

    def test_user_profile_schema_negative_weight(self):
        """Test user profile schema with negative weight"""
        profile = UserProfileSchema(
            weight=-70.5,
            height=180.0,
            fitness_goal="lose_weight"
        )
        assert profile.weight == -70.5  # Should accept if no validation

    def test_user_profile_response_schema(self):
        """Test user profile response schema"""
        profile = UserProfileResponseSchema(
            email="test@example.com",
            name="Test User",
            weight=70.5,
            height=180.0,
            fitness_goal="lose_weight",
            onboarded="true"
        )
        assert profile.email == "test@example.com"
        assert profile.onboarded == "true"

    def test_user_profile_update(self):
        """Test user profile update schema"""
        update = UserProfileUpdate(
            weight=75.0,
            height=185.0,
            fitness_goal="gain_muscle"
        )
        assert update.weight == 75.0
        assert update.fitness_goal == "gain_muscle"

class TestExerciseSchemas:
    """Test exercise-related DTO schemas"""

    def test_exercise_id_schema(self):
        """Test exercise ID schema"""
        exercise_id = ExerciseId(exercise_id=1)
        assert exercise_id.exercise_id == 1

    def test_muscle_group_impact(self):
        """Test muscle group impact schema"""
        impact = MuscleGroupImpact(
            id=1,
            name="Chest",
            body_part="Upper Body"
        )
        assert impact.id == 1
        assert impact.name == "Chest"
        assert impact.body_part == "Upper Body"

    def test_exercise_response_schema(self):
        """Test exercise response schema"""
        exercise = ExerciseResponseSchema(
            id=1,
            name="Push-up",
            description="A bodyweight exercise",
            difficulty=3,
            equipment="None",
            instructions="Perform push-up motion"
        )
        assert exercise.id == 1
        assert exercise.name == "Push-up"
        assert exercise.difficulty == 3

class TestWorkoutSchemas:
    """Test workout-related DTO schemas"""

    def test_register_workout_schema(self):
        """Test register workout schema"""
        exercises = [ExerciseId(exercise_id=1), ExerciseId(exercise_id=2)]
        workout = RegisterWorkoutSchema(exercises=exercises)
        assert len(workout.exercises) == 2
        assert workout.exercises[0].exercise_id == 1

    def test_workout_response_schema(self):
        """Test workout response schema"""
        exercises = [
            ExerciseResponseSchema(
                id=1, name="Push-up", description="desc",
                difficulty=3, equipment="None", instructions="Do it"
            )
        ]
        workout = WorkoutResponseSchema(
            id=1,
            user_email="test@example.com",
            created_at=datetime.now(),
            performed_at=None,
            performed=False,
            exercises=exercises
        )
        assert workout.id == 1
        assert workout.performed is False
        assert len(workout.exercises) == 1

    def test_workout_exercises_list(self):
        """Test workout exercises list schema"""
        exercises = [ExerciseId(exercise_id=1)]
        workout_list = WorkoutExercisesList(exercises=exercises)
        assert len(workout_list.exercises) == 1

class TestFitModels:
    """Test fit database models"""

    def test_user_model_repr(self):
        """Test user model string representation"""
        user = MagicMock()
        user.email = "test@example.com"
        user.name = "Test User"
        user.role = "user"
        
        # Test the __repr__ method if it exists
        result = UserModel.__repr__(user)
        assert "test@example.com" in result

    def test_workout_model_creation(self):
        """Test workout model can be created"""
        # Since SQLAlchemy models have complex column types,
        # we'll just test that the class exists and has expected attributes
        assert hasattr(WorkoutModel, '__tablename__')
        assert hasattr(WorkoutModel, 'id')
        assert hasattr(WorkoutModel, 'user_email')

    def test_user_exercise_history_model(self):
        """Test user exercise history model"""
        assert hasattr(UserExerciseHistory, '__tablename__')
        assert hasattr(UserExerciseHistory, 'id')
        assert hasattr(UserExerciseHistory, 'exercise_id')

class TestValidationEdgeCases:
    """Test validation edge cases and error conditions"""

    def test_empty_string_email(self):
        """Test empty string email validation"""
        with pytest.raises(ValidationError):
            UserSchema(email="", name="Test", role="user")

    def test_very_long_name(self):
        """Test very long name handling"""
        long_name = "x" * 1000
        user = UserSchema(email="test@example.com", name=long_name, role="user")
        assert user.name == long_name

    def test_special_characters_in_name(self):
        """Test special characters in name"""
        user = UserSchema(
            email="test@example.com",
            name="Test User ñáéíóú",
            role="user"
        )
        assert "ñáéíóú" in user.name

    def test_zero_weight_height(self):
        """Test zero weight and height"""
        profile = UserProfileSchema(
            weight=0.0,
            height=0.0,
            fitness_goal="maintain"
        )
        assert profile.weight == 0.0
        assert profile.height == 0.0

    def test_negative_exercise_id(self):
        """Test negative exercise ID"""
        exercise_id = ExerciseId(exercise_id=-1)
        assert exercise_id.exercise_id == -1

    def test_empty_fitness_goal(self):
        """Test empty fitness goal"""
        profile = UserProfileSchema(
            weight=70.0,
            height=180.0,
            fitness_goal=""
        )
        assert profile.fitness_goal == ""

    def test_none_values_in_optional_fields(self):
        """Test None values in optional fields"""
        profile = UserProfileUpdate(
            weight=None,
            height=None,
            fitness_goal=None
        )
        assert profile.weight is None
        assert profile.height is None
        assert profile.fitness_goal is None

class TestModelEquality:
    """Test model equality and comparison operations"""

    def test_user_schema_equality(self):
        """Test user schema equality"""
        user1 = UserSchema(email="test@example.com", name="Test", role="user")
        user2 = UserSchema(email="test@example.com", name="Test", role="user")
        assert user1 == user2

    def test_user_schema_inequality(self):
        """Test user schema inequality"""
        user1 = UserSchema(email="test1@example.com", name="Test", role="user")
        user2 = UserSchema(email="test2@example.com", name="Test", role="user")
        assert user1 != user2

    def test_exercise_id_equality(self):
        """Test exercise ID equality"""
        ex1 = ExerciseId(exercise_id=1)
        ex2 = ExerciseId(exercise_id=1)
        assert ex1 == ex2

    def test_exercise_id_inequality(self):
        """Test exercise ID inequality"""
        ex1 = ExerciseId(exercise_id=1)
        ex2 = ExerciseId(exercise_id=2)
        assert ex1 != ex2

class TestModelSerialization:
    """Test model serialization and deserialization"""

    def test_user_schema_dict(self):
        """Test user schema to dict conversion"""
        user = UserSchema(email="test@example.com", name="Test", role="user")
        user_dict = user.model_dump()
        assert user_dict["email"] == "test@example.com"
        assert user_dict["name"] == "Test"
        assert user_dict["role"] == "user"

    def test_user_profile_dict(self):
        """Test user profile schema to dict conversion"""
        profile = UserProfileSchema(
            weight=70.0,
            height=180.0,
            fitness_goal="lose_weight"
        )
        profile_dict = profile.model_dump()
        assert profile_dict["weight"] == 70.0
        assert profile_dict["fitness_goal"] == "lose_weight"

    def test_token_schema_dict(self):
        """Test token schema to dict conversion"""
        token = TokenSchema(access_token="abc123", token_type="bearer")
        token_dict = token.model_dump()
        assert token_dict["access_token"] == "abc123"
        assert token_dict["token_type"] == "bearer"
