import logging
import os
from typing import List, Tuple

import requests
from .models_db import ExerciseModel, MuscleGroupModel, exercise_muscle_groups
from .database import db_session
import random
from time import time

logger = logging.getLogger(__name__)


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


def get_last_workout_exercises(user_email: str) -> List[int]:
    """
    Get the last workout exercises for a user from the monolith.
    """
    monolith_url = os.getenv("MONOLITH_URL")
    headers = {"X-API-Key": os.getenv("FIT_API_KEY")}
    history_response = requests.post(
        f"{monolith_url}/workouts/last", headers=headers, json={"email": user_email}
    )
    history_response.raise_for_status()
    return history_response.json()


def save_workout_exercises(user_email: str, exercise_ids: List[int]):
    """
    Save the workout exercises for a user to the monolith.
    """
    monolith_url = os.getenv("MONOLITH_URL")
    headers = {"X-API-Key": os.getenv("FIT_API_KEY")}
    requests.post(
        f"{monolith_url}/workouts/",
        headers=headers,
        json={"email": user_email, "exercises": exercise_ids},
    )


def is_user_premium(user_email: str) -> bool:
    billing_url = os.getenv("BILLING_URL", "http://billing:5003")
    try:
        resp = requests.get(
            f"{billing_url}/billing/subscriptions/users/{user_email}", timeout=3
        )
        if resp.status_code == 200:
            data = resp.json()
            return (
                data.get("is_active", False) and data.get("plan_id_name", "") != "free"
            )
        return False
    except Exception:
        return False


def create_wod_for_user(user_email: str):
    db = db_session()
    try:
        last_exercise_ids = get_last_workout_exercises(user_email)
        available_exercises = (
            db.query(ExerciseModel)
            .filter(~ExerciseModel.id.in_(last_exercise_ids))
            .all()
        )
        if len(available_exercises) < 9:
            available_exercises = db.query(ExerciseModel).all()
        premium = is_user_premium(user_email)
        num_exercises = 9 if premium else 3
        selected_exercises = (
            random.sample(available_exercises, num_exercises)
            if len(available_exercises) >= num_exercises
            else available_exercises
        )
        save_workout_exercises(
            user_email, [exercise.id for exercise in selected_exercises] # type: ignore
        )
        result = []
        for exercise in selected_exercises:
            stmt = (
                db.query(MuscleGroupModel, exercise_muscle_groups.c.is_primary)
                .join(
                    exercise_muscle_groups,
                    MuscleGroupModel.id == exercise_muscle_groups.c.muscle_group_id,
                )
                .filter(exercise_muscle_groups.c.exercise_id == exercise.id)
            )
            muscle_groups = [(mg, is_primary) for mg, is_primary in stmt.all()]
            result.append((exercise, muscle_groups))
        return result
    finally:
        db.close()