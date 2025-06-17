import logging
import os
from datetime import datetime, timezone
from typing import List, Optional

import requests
from sqlalchemy.orm import joinedload

from ..database import db_session
from ..models_db import UserExerciseHistory, WorkoutModel
from ..models_dto import (
    ExerciseId,
    WodExerciseSchema,
    WorkoutExercisesList,
    WorkoutResponseSchema,
    RegisterWorkoutExerciseSchema,
    ExerciseResponseSchema
)
from ..services.rabbitmq_service import rabbitmq_service
from ..queue_messages import WorkoutPerformedMessage, WorkoutPerformedExerciseSchema

logger = logging.getLogger(__name__)


def register_workout(user_email: str, exercises: List[RegisterWorkoutExerciseSchema]) -> None:
    db = db_session()
    try:
        workout = WorkoutModel(
            user_email=user_email,
            created_at=datetime.utcnow(),
            performed_at=None
        )
        db.add(workout)
        db.flush()  # To get the ID

        for ex in exercises:
            exercise_entry = UserExerciseHistory(
                workout_id=workout.id,
                exercise_id=ex.exercise_id
            )
            db.add(exercise_entry)

        db.commit()
    finally:
        db.close()


def get_exercises_metadata(exercise_ids: List[int]) -> List[ExerciseResponseSchema]:
    coach_url = os.getenv("COACH_URL")
    history_response = requests.get(f"{coach_url}/exercises")
    history_response.raise_for_status()
    history_exercises = history_response.json()

    return [ExerciseResponseSchema(**exercise) for exercise in history_exercises if exercise['id'] in exercise_ids]


def get_most_recent_workout_exercises(user_email: str, performed: Optional[bool] = None) -> Optional[WorkoutResponseSchema]:
    db = db_session()
    try:
        query = db.query(WorkoutModel).filter(WorkoutModel.user_email == user_email)

        if performed is True:
            query = query.filter(WorkoutModel.performed_at.isnot(None)).order_by(WorkoutModel.performed_at.desc())
        elif performed is False:
            query = query.filter(WorkoutModel.performed_at.is_(None)).order_by(WorkoutModel.created_at.desc())
        else:
            query = query.order_by(WorkoutModel.created_at.desc())

        workout = query.first()

        if not workout:
            return None

        exercises = db.query(UserExerciseHistory).filter(UserExerciseHistory.workout_id == workout.id).all()
        exercise_ids = [e.exercise_id for e in exercises]
        exercise_metadata = get_exercises_metadata(exercise_ids)

        return WorkoutResponseSchema(
            id=workout.id,
            exercises=exercise_metadata
        )
    finally:
        db.close()


def get_user_next_workout(user_email: str) -> Optional[WorkoutResponseSchema]:
    return get_most_recent_workout_exercises(user_email, performed=False)


def perform_workout(workout_id: int, user_email: str) -> None:
    db = db_session()
    try:
        workout = db.query(WorkoutModel).options(
            joinedload(WorkoutModel.exercises)
        ).filter(
            WorkoutModel.id == workout_id,
            WorkoutModel.user_email == user_email
        ).first()

        if not workout:
            logger.warning(f"Workout not found or does not belong to user. Workout ID: {workout_id}, User: {user_email}")
            raise ValueError("Workout not found or does not belong to the user")

        if workout.performed:
            logger.warning(f"Workout already marked as performed. Workout ID: {workout_id}, User: {user_email}")
            raise ValueError("Workout already marked as performed")

        workout.performed = True
        workout.performed_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Workout {workout_id} marked as performed for user {user_email} at {workout.performed_at}")

        try:
            exercise_schemas = []
            if workout.exercises:
                for wo_exercise in workout.exercises:
                    exercise_schemas.append(WorkoutPerformedExerciseSchema(exercise_id=wo_exercise.exercise_id))

            event_message = WorkoutPerformedMessage(
                user_email=user_email,
                workout_id=workout_id,
                performed_at=workout.performed_at,
                exercises=exercise_schemas
            )

            if rabbitmq_service.publish_workout_performed_event(event_message):
                logger.info(f"Successfully published WorkoutPerformedEvent for workout {workout_id}, user {user_email}")
            else:
                logger.error(f"Failed to publish WorkoutPerformedEvent for workout {workout_id}, user {user_email}")
        except Exception as e:
            logger.error(
                f"Exception during WorkoutPerformedEvent publishing for workout {workout_id}, user {user_email}: {e}",
                exc_info=True
            )

    except ValueError as ve:
        db.rollback()
        logger.error(f"ValueError performing workout {workout_id} for user {user_email}: {ve}", exc_info=True)
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Generic error performing workout {workout_id} for user {user_email}: {e}", exc_info=True)
        raise
    finally:
        db.close()
