from src.fit.database import db_session
from src.fit.models_db import MuscleGroupModel, ExerciseModel, exercise_muscle_groups
from src.fit.models_dto import MuscleGroup, Exercise, MuscleGroupWithPrimary
from sqlalchemy import select, join

def get_all_muscle_groups():
    """
    Get all muscle groups from the database
    """
    db = db_session()
    try:
        muscle_groups = db.query(MuscleGroupModel).all()
        return [MuscleGroup.model_validate(
            {
                "id": mg.id,
                "name": mg.name,
                "body_part": mg.body_part,
                "description": mg.description
            }
        ) for mg in muscle_groups]
    finally:
        db.close()

def get_muscle_group_by_id(muscle_group_id: int):
    """
    Get a specific muscle group by ID
    """
    db = db_session()
    try:
        muscle_group = db.query(MuscleGroupModel).filter(MuscleGroupModel.id == muscle_group_id).first()
        if not muscle_group:
            return None
        
        return MuscleGroup.model_validate(
            {
                "id": muscle_group.id,
                "name": muscle_group.name,
                "body_part": muscle_group.body_part,
                "description": muscle_group.description
            }
        )
    finally:
        db.close()

def get_all_exercises():
    """
    Get all exercises with their associated muscle groups
    """
    db = db_session()
    try:
        exercises = db.query(ExerciseModel).all()
        
        result = []
        for exercise in exercises:
            # Get muscle groups with primary information for this exercise
            muscle_groups_data = db.query(
                MuscleGroupModel, 
                exercise_muscle_groups.c.is_primary
            ).join(
                exercise_muscle_groups, 
                MuscleGroupModel.id == exercise_muscle_groups.c.muscle_group_id
            ).filter(
                exercise_muscle_groups.c.exercise_id == exercise.id
            ).all()
            
            # Convert to DTO format
            muscle_groups = [
                MuscleGroupWithPrimary.model_validate(
                    {
                        "id": mg[0].id,
                        "name": mg[0].name,
                        "body_part": mg[0].body_part,
                        "description": mg[0].description,
                        "is_primary": mg[1]
                    }
                ) for mg in muscle_groups_data
            ]
            
            # Create exercise DTO
            exercise_dto = Exercise.model_validate(
                {
                    "id": exercise.id,
                    "name": exercise.name,
                    "description": exercise.description,
                    "difficulty": exercise.difficulty,
                    "equipment": exercise.equipment,
                    "instructions": exercise.instructions,
                    "muscle_groups": muscle_groups
                }
            )
            
            result.append(exercise_dto)
            
        return result
    finally:
        db.close()

def get_exercise_by_id(exercise_id: int):
    """
    Get a specific exercise by ID with its associated muscle groups
    """
    db = db_session()
    try:
        exercise = db.query(ExerciseModel).filter(ExerciseModel.id == exercise_id).first()
        if not exercise:
            return None
        
        # Get muscle groups with primary information for this exercise
        muscle_groups_data = db.query(
            MuscleGroupModel, 
            exercise_muscle_groups.c.is_primary
        ).join(
            exercise_muscle_groups, 
            MuscleGroupModel.id == exercise_muscle_groups.c.muscle_group_id
        ).filter(
            exercise_muscle_groups.c.exercise_id == exercise.id
        ).all()
        
        # Convert to DTO format
        muscle_groups = [
            MuscleGroupWithPrimary.model_validate(
                {
                    "id": mg[0].id,
                    "name": mg[0].name,
                    "body_part": mg[0].body_part,
                    "description": mg[0].description,
                    "is_primary": mg[1]
                }
            ) for mg in muscle_groups_data
        ]
        
        # Create exercise DTO
        return Exercise.model_validate(
            {
                "id": exercise.id,
                "name": exercise.name,
                "description": exercise.description,
                "difficulty": exercise.difficulty,
                "equipment": exercise.equipment,
                "instructions": exercise.instructions,
                "muscle_groups": muscle_groups
            }
        )
    finally:
        db.close()

def get_exercises_by_muscle_group(muscle_group_id: int):
    """
    Get all exercises that target a specific muscle group
    """
    db = db_session()
    try:
        exercises = db.query(ExerciseModel).join(
            exercise_muscle_groups,
            ExerciseModel.id == exercise_muscle_groups.c.exercise_id
        ).filter(
            exercise_muscle_groups.c.muscle_group_id == muscle_group_id
        ).all()
        
        result = []
        for exercise in exercises:
            # Get all muscle groups for this exercise
            muscle_groups_data = db.query(
                MuscleGroupModel, 
                exercise_muscle_groups.c.is_primary
            ).join(
                exercise_muscle_groups, 
                MuscleGroupModel.id == exercise_muscle_groups.c.muscle_group_id
            ).filter(
                exercise_muscle_groups.c.exercise_id == exercise.id
            ).all()
            
            # Convert to DTO format
            muscle_groups = [
                MuscleGroupWithPrimary.model_validate(
                    {
                        "id": mg[0].id,
                        "name": mg[0].name,
                        "body_part": mg[0].body_part,
                        "description": mg[0].description,
                        "is_primary": mg[1]
                    }
                ) for mg in muscle_groups_data
            ]
            
            # Create exercise DTO
            exercise_dto = Exercise.model_validate(
                {
                    "id": exercise.id,
                    "name": exercise.name,
                    "description": exercise.description,
                    "difficulty": exercise.difficulty,
                    "equipment": exercise.equipment,
                    "instructions": exercise.instructions,
                    "muscle_groups": muscle_groups
                }
            )
            
            result.append(exercise_dto)
            
        return result
    finally:
        db.close()