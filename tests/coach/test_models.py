"""
Tests for coach.models_db and coach.models_dto
"""
from src.coach.models_dto import MuscleGroup, Exercise
from src.coach.models_db import MuscleGroupModel, ExerciseModel

def test_muscle_group_schema():
    mg = MuscleGroup(id=1, name="Chest", body_part="Upper", description="desc")
    assert mg.name == "Chest"
    assert mg.body_part == "Upper"
    assert mg.description == "desc"

def test_exercise_model_repr():
    em = ExerciseModel(id=1, name="Pushup", description="desc")
    assert "Pushup" in repr(em)

# Add more tests for all DTOs and models, including __repr__, __eq__, and edge cases.
