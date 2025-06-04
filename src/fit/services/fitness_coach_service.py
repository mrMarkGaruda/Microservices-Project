from typing import List, Tuple
from src.fit.models_db import ExerciseModel, MuscleGroupModel, exercise_muscle_groups, UserExerciseHistoryModel
from src.fit.database import db_session
from datetime import datetime, timedelta
import random
from time import time

def heavy_computation(duration_seconds: int = 3):
    """
    Perform CPU-intensive calculations to simulate heavy processing.
    Uses matrix operations which are CPU-intensive.
    """
    start_time = time()
    i = 0
    while (time() - start_time) < duration_seconds:
        j = 0
        while j < 1000000:
            j += 1
        i += 1

def calculate_intensity(difficulty: int) -> float:
    """
    Calculate the intensity of an exercise based on its difficulty level (1-5).
    Returns a value between 0.0 and 1.0.
    """
    # Convert difficulty (1-5) to intensity (0.0-1.0)
    return (difficulty - 1) / 4.0

def get_recent_exercises(user_email: str, days_back: int = 3) -> List[int]:
    """
    Get exercise IDs that the user has performed in the last N days.
    """
    db = db_session()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        recent_exercises = db.query(UserExerciseHistoryModel.exercise_id).filter(
            UserExerciseHistoryModel.user_email == user_email,
            UserExerciseHistoryModel.performed_at >= cutoff_date
        ).distinct().all()
        
        return [ex[0] for ex in recent_exercises]
    finally:
        db.close()

def save_exercise_history(user_email: str, exercise_id: int, weight: float, reps: int):
    """
    Save the user's exercise to history.
    """
    db = db_session()
    try:
        history_entry = UserExerciseHistoryModel(
            user_email=user_email,
            exercise_id=exercise_id,
            suggested_weight=weight,
            suggested_reps=reps
        )
        
        db.add(history_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def request_wod(user_email: str) -> List[Tuple[ExerciseModel, List[Tuple[MuscleGroupModel, bool]]]]:
    """
    Request a workout of the day (WOD) for a specific user.
    Avoids exercises the user has done recently.
    Returns a list of tuples containing:
    - The exercise
    - A list of tuples containing:
      - The muscle group
      - Whether it's a primary muscle group
    """
    # Simulate heavy computation (AI model processing, complex calculations, etc.) for 1-5 seconds
    heavy_computation(random.randint(1, 5)) # DO NOT REMOVE THIS LINE
    
    db = db_session()
    try:
        # Get exercises the user has done recently
        recent_exercise_ids = get_recent_exercises(user_email)
        
        # Get all exercises, excluding recent ones
        query = db.query(ExerciseModel)
        if recent_exercise_ids:
            query = query.filter(~ExerciseModel.id.in_(recent_exercise_ids))
        
        available_exercises = query.all()
        
        # If we don't have enough available exercises, fall back to all exercises
        if len(available_exercises) < 6:
            available_exercises = db.query(ExerciseModel).all()
        
        # Select 6 random exercises
        selected_exercises = random.sample(available_exercises, 6) if len(available_exercises) >= 6 else available_exercises
        
        # For each exercise, get its muscle groups and whether they are primary
        result = []
        for exercise in selected_exercises:
            # Get the junction table information for this exercise
            stmt = db.query(
                MuscleGroupModel,
                exercise_muscle_groups.c.is_primary
            ).join(
                exercise_muscle_groups,
                MuscleGroupModel.id == exercise_muscle_groups.c.muscle_group_id
            ).filter(
                exercise_muscle_groups.c.exercise_id == exercise.id
            )
            
            muscle_groups = [(mg, is_primary) for mg, is_primary in stmt.all()]
            result.append((exercise, muscle_groups))
            
            # Save to history (with random weight and reps for tracking)
            weight = random.uniform(5.0, 50.0)
            reps = random.randint(8, 15)
            save_exercise_history(user_email, exercise.id, weight, reps)
            
        return result
    finally:
        db.close()