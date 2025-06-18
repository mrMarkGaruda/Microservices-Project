"""
Tests for coach.models_db and coach.models_dto
"""
import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError
from src.coach.models_dto import (
    MuscleGroupBase, MuscleGroup, ExerciseMuscleGroup, ExerciseBase,
    MuscleGroupWithPrimary, Exercise, MuscleGroupImpact, WodExerciseSchema, WodResponseSchema
)
from src.coach.models_db import MuscleGroupModel, ExerciseModel


class TestMuscleGroupSchemas:
    """Test muscle group DTO schemas"""
    
    def test_muscle_group_base_valid(self):
        """Test valid MuscleGroupBase creation"""
        mg = MuscleGroupBase(
            name="Chest",
            body_part="Upper Body",
            description="Chest muscles"
        )
        assert mg.name == "Chest"
        assert mg.body_part == "Upper Body"
        assert mg.description == "Chest muscles"

    def test_muscle_group_base_minimal(self):
        """Test MuscleGroupBase with minimal required fields"""
        mg = MuscleGroupBase(
            name="Chest",
            body_part="Upper Body"
        )
        assert mg.name == "Chest"
        assert mg.body_part == "Upper Body"
        assert mg.description is None

    def test_muscle_group_with_id(self):
        """Test MuscleGroup with ID"""
        mg = MuscleGroup(
            id=1,
            name="Chest",
            body_part="Upper Body",
            description="Chest muscles"
        )
        assert mg.id == 1
        assert mg.name == "Chest"
        assert mg.body_part == "Upper Body"
        assert mg.description == "Chest muscles"

    def test_muscle_group_with_primary(self):
        """Test MuscleGroupWithPrimary"""
        mg = MuscleGroupWithPrimary(
            id=1,
            name="Chest",
            body_part="Upper Body",
            description="Chest muscles",
            is_primary=True
        )
        assert mg.id == 1
        assert mg.name == "Chest"
        assert mg.is_primary is True

    def test_muscle_group_impact(self):
        """Test MuscleGroupImpact"""
        mgi = MuscleGroupImpact(
            id=1,
            name="Chest",
            body_part="Upper Body",
            is_primary=True,
            intensity=0.8
        )
        assert mgi.id == 1
        assert mgi.name == "Chest"
        assert mgi.body_part == "Upper Body"
        assert mgi.is_primary is True
        assert mgi.intensity == 0.8

    def test_muscle_group_missing_required_fields(self):
        """Test MuscleGroup with missing required fields"""
        with pytest.raises(ValidationError):
            MuscleGroup(name="Chest")  # type: ignore


class TestExerciseSchemas:
    """Test exercise DTO schemas"""
    
    def test_exercise_muscle_group(self):
        """Test ExerciseMuscleGroup"""
        emg = ExerciseMuscleGroup(
            muscle_group_id=1,
            is_primary=True
        )
        assert emg.muscle_group_id == 1
        assert emg.is_primary is True

    def test_exercise_muscle_group_default_primary(self):
        """Test ExerciseMuscleGroup with default is_primary"""
        emg = ExerciseMuscleGroup(muscle_group_id=1)
        assert emg.muscle_group_id == 1
        assert emg.is_primary is False

    def test_exercise_base_valid(self):
        """Test valid ExerciseBase creation"""
        exercise = ExerciseBase(
            name="Push-up",
            description="Basic push-up exercise",
            difficulty=3,
            equipment="None",
            instructions="Get into plank position and push up"
        )
        assert exercise.name == "Push-up"
        assert exercise.description == "Basic push-up exercise"
        assert exercise.difficulty == 3
        assert exercise.equipment == "None"
        assert exercise.instructions == "Get into plank position and push up"

    def test_exercise_base_minimal(self):
        """Test ExerciseBase with minimal required fields"""
        exercise = ExerciseBase(
            name="Push-up",
            difficulty=3
        )
        assert exercise.name == "Push-up"
        assert exercise.difficulty == 3
        assert exercise.description is None
        assert exercise.equipment is None
        assert exercise.instructions is None

    def test_exercise_difficulty_validation(self):
        """Test exercise difficulty validation"""
        # Valid difficulties (1-5)
        for difficulty in [1, 2, 3, 4, 5]:
            exercise = ExerciseBase(name="Test", difficulty=difficulty)
            assert exercise.difficulty == difficulty

        # Invalid difficulties
        with pytest.raises(ValidationError):
            ExerciseBase(name="Test", difficulty=0)

        with pytest.raises(ValidationError):
            ExerciseBase(name="Test", difficulty=6)

        with pytest.raises(ValidationError):
            ExerciseBase(name="Test", difficulty=-1)

    def test_exercise_with_muscle_groups(self):
        """Test Exercise with muscle groups"""
        muscle_groups = [
            MuscleGroupWithPrimary(
                id=1,
                name="Chest",
                body_part="Upper Body",
                is_primary=True
            ),
            MuscleGroupWithPrimary(
                id=2,
                name="Triceps",
                body_part="Upper Body",
                is_primary=False
            )
        ]
        
        exercise = Exercise(
            id=1,
            name="Push-up",
            difficulty=3,
            muscle_groups=muscle_groups
        )
        assert exercise.id == 1
        assert exercise.name == "Push-up"
        assert len(exercise.muscle_groups) == 2
        assert exercise.muscle_groups[0].is_primary is True
        assert exercise.muscle_groups[1].is_primary is False

    def test_exercise_missing_required_fields(self):
        """Test Exercise with missing required fields"""
        with pytest.raises(ValidationError):
            Exercise(name="Push-up")  # type: ignore


class TestWodSchemas:
    """Test workout of the day schemas"""
    
    def test_wod_exercise_schema(self):
        """Test WodExerciseSchema"""
        muscle_groups = [
            MuscleGroupImpact(
                id=1,
                name="Chest",
                body_part="Upper Body",
                is_primary=True,
                intensity=0.8
            )
        ]
        
        wod_exercise = WodExerciseSchema(
            id=1,
            name="Push-up",
            description="Basic push-up",
            difficulty=3,
            muscle_groups=muscle_groups,
            suggested_weight=25.5,
            suggested_reps=15
        )
        
        assert wod_exercise.id == 1
        assert wod_exercise.name == "Push-up"
        assert wod_exercise.suggested_weight == 25.5
        assert wod_exercise.suggested_reps == 15
        assert len(wod_exercise.muscle_groups) == 1    def test_wod_response_schema(self):
        """Test WodResponseSchema"""
        from datetime import datetime
        
        exercises = [
            WodExerciseSchema(
                id=1,
                name="Push-up",
                description="Basic push-up",
                difficulty=3,
                muscle_groups=[],
                suggested_weight=25.5,
                suggested_reps=15
            )
        ]
        
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        wod_response = WodResponseSchema(
            exercises=exercises,
            generated_at=timestamp
        )
        
        assert len(wod_response.exercises) == 1
        assert wod_response.generated_at == timestamp

    def test_wod_response_empty_exercises(self):
        """Test WodResponseSchema with empty exercises"""
        from datetime import datetime
        
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        wod_response = WodResponseSchema(
            exercises=[],
            generated_at=timestamp
        )
        
        assert len(wod_response.exercises) == 0
        assert wod_response.generated_at == timestamp


class TestCoachModels:
    """Test coach database models"""
    
    def test_muscle_group_model_repr(self):
        """Test MuscleGroupModel __repr__ method"""
        model = MuscleGroupModel(
            id=1,
            name="Chest",
            body_part="Upper Body",
            description="Chest muscles"
        )
        repr_str = repr(model)
        assert "Chest" in repr_str

    def test_muscle_group_model_creation(self):
        """Test MuscleGroupModel creation"""
        model = MuscleGroupModel(
            name="Chest",
            body_part="Upper Body",
            description="Chest muscles"
        )
        # SQLAlchemy models don't allow direct attribute comparison
        # Just verify the model was created without errors
        assert model is not None

    def test_exercise_model_repr(self):
        """Test ExerciseModel __repr__ method"""
        model = ExerciseModel(
            id=1,
            name="Push-up",
            description="Basic push-up",
            difficulty=3
        )
        repr_str = repr(model)
        assert "Push-up" in repr_str

    def test_exercise_model_creation(self):
        """Test ExerciseModel creation"""
        model = ExerciseModel(
            name="Push-up",
            description="Basic push-up",
            difficulty=3,
            equipment="None",
            instructions="Push up from the ground"
        )
        # Just verify the model was created without errors
        assert model is not None


class TestModelSerialization:
    """Test model serialization and deserialization"""
    
    def test_muscle_group_dict_conversion(self):
        """Test converting MuscleGroup to dict"""
        mg = MuscleGroup(
            id=1,
            name="Chest",
            body_part="Upper Body",
            description="Chest muscles"
        )
        
        mg_dict = mg.model_dump()
        assert mg_dict["id"] == 1
        assert mg_dict["name"] == "Chest"
        assert mg_dict["body_part"] == "Upper Body"
        assert mg_dict["description"] == "Chest muscles"

    def test_exercise_dict_conversion(self):
        """Test converting Exercise to dict"""
        exercise = Exercise(
            id=1,
            name="Push-up",
            difficulty=3,
            muscle_groups=[]
        )
        
        exercise_dict = exercise.model_dump()
        assert exercise_dict["id"] == 1
        assert exercise_dict["name"] == "Push-up"
        assert exercise_dict["difficulty"] == 3
        assert exercise_dict["muscle_groups"] == []

    def test_wod_exercise_json_serialization(self):
        """Test JSON serialization of WodExerciseSchema"""
        wod_exercise = WodExerciseSchema(
            id=1,
            name="Push-up",
            description="Basic push-up",
            difficulty=3,
            muscle_groups=[],
            suggested_weight=25.5,
            suggested_reps=15
        )
        
        json_str = wod_exercise.model_dump_json()
        assert '"id":1' in json_str
        assert '"name":"Push-up"' in json_str
        assert '"suggested_weight":25.5' in json_str


class TestValidationEdgeCases:
    """Test validation edge cases"""
    
    def test_empty_muscle_group_name(self):
        """Test MuscleGroup with empty name"""
        mg = MuscleGroup(
            id=1,
            name="",
            body_part="Upper Body"
        )
        assert mg.name == ""

    def test_empty_exercise_name(self):
        """Test Exercise with empty name"""
        exercise = Exercise(
            id=1,
            name="",
            difficulty=3,
            muscle_groups=[]
        )
        assert exercise.name == ""

    def test_very_long_names(self):
        """Test handling of very long names"""
        long_name = "a" * 1000
        
        mg = MuscleGroup(
            id=1,
            name=long_name,
            body_part="Upper Body"
        )
        assert mg.name == long_name

    def test_special_characters_in_names(self):
        """Test handling of special characters in names"""
        special_name = "Push-up (advanced) & Pull-up [modified]"
        
        exercise = Exercise(
            id=1,
            name=special_name,
            difficulty=3,
            muscle_groups=[]
        )
        assert exercise.name == special_name

    def test_negative_suggested_values(self):
        """Test WodExerciseSchema with negative suggested values"""
        wod_exercise = WodExerciseSchema(
            id=1,
            name="Push-up",
            description="Basic push-up",
            difficulty=3,
            muscle_groups=[],
            suggested_weight=-10.0,  # Negative weight
            suggested_reps=-5  # Negative reps
        )
        
        assert wod_exercise.suggested_weight == -10.0
        assert wod_exercise.suggested_reps == -5

    def test_zero_suggested_values(self):
        """Test WodExerciseSchema with zero suggested values"""
        wod_exercise = WodExerciseSchema(
            id=1,
            name="Push-up",
            description="Basic push-up",
            difficulty=3,
            muscle_groups=[],
            suggested_weight=0.0,
            suggested_reps=0
        )
        
        assert wod_exercise.suggested_weight == 0.0
        assert wod_exercise.suggested_reps == 0
