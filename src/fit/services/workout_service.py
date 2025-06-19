import logging  # Importing the logging module to enable logging throughout the application
import os  # Importing the os module to access environment variables
from datetime import datetime, timezone  # Importing datetime and timezone classes to handle date and time
from typing import List, Optional  # Importing List and Optional for type hinting

import requests  # Importing requests module to make HTTP requests
from sqlalchemy.orm import joinedload  # Importing joinedload to optimize database queries

from ..database import db_session  # Importing the database session manager
from ..models_db import UserExerciseHistory, WorkoutModel  # Importing database models
from ..models_dto import (
    ExerciseId,
    WodExerciseSchema,
    WorkoutExercisesList,
    WorkoutResponseSchema,
    RegisterWorkoutExerciseSchema,
    ExerciseResponseSchema
)  # Importing Data Transfer Object (DTO) models
from ..services.rabbitmq_service import rabbitmq_service  # Importing RabbitMQ service for messaging
from ..queue_messages import WorkoutPerformedMessage, WorkoutPerformedExerciseSchema  # Importing message schemas

logger = logging.getLogger(__name__)  # Setting up a logger for this module


def register_workout(user_email: str, exercises: List[RegisterWorkoutExerciseSchema]) -> None:
    db = db_session()  # Creating a new database session
    try:
        # Creating a new workout instance
        workout = WorkoutModel(
            user_email=user_email,
            created_at=datetime.utcnow(),
            performed_at=None
        )
        db.add(workout)  # Adding the workout to the session
        db.flush()  # Flushing the session to get the workout ID

        # Adding each exercise to the workout
        for ex in exercises:
            exercise_entry = UserExerciseHistory(
                workout_id=workout.id,
                exercise_id=ex.exercise_id
            )
            db.add(exercise_entry)  # Adding exercise entry to the session

        db.commit()  # Committing the session to save changes to the database
    finally:
        db.close()  # Closing the database session


def get_exercises_metadata(exercise_ids: List[int]) -> List[ExerciseResponseSchema]:
    coach_url = os.getenv("COACH_URL")  # Getting the coach URL from environment variables
    history_response = requests.get(f"{coach_url}/exercises")  # Making a GET request to fetch exercises
    history_response.raise_for_status()  # Raising an error for bad responses
    history_exercises = history_response.json()  # Parsing the JSON response

    # Returning the exercise metadata for the given exercise IDs
    return [ExerciseResponseSchema(**exercise) for exercise in history_exercises if exercise['id'] in exercise_ids]


def get_most_recent_workout_exercises(user_email: str, performed: Optional[bool] = None) -> Optional[WorkoutResponseSchema]:
    db = db_session()  # Creating a new database session
    try:
        query = db.query(WorkoutModel).filter(WorkoutModel.user_email == user_email)  # Querying workouts for the user

        # Filtering and ordering workouts based on their performed status
        if performed is True:
            query = query.filter(WorkoutModel.performed_at.isnot(None)).order_by(WorkoutModel.performed_at.desc())
        elif performed is False:
            query = query.filter(WorkoutModel.performed_at.is_(None)).order_by(WorkoutModel.created_at.desc())
        else:
            query = query.order_by(WorkoutModel.created_at.desc())

        workout = query.first()  # Fetching the most recent workout

        if not workout:
            return None  # Returning None if no workout is found

        exercises = db.query(UserExerciseHistory).filter(UserExerciseHistory.workout_id == workout.id).all()  # Fetching exercises for the workout
        exercise_ids = [e.exercise_id for e in exercises]  # Extracting exercise IDs
        exercise_metadata = get_exercises_metadata(exercise_ids)  # Fetching exercise metadata

        # Returning the workout response schema
        return WorkoutResponseSchema(
            id=workout.id,
            exercises=exercise_metadata
        )
    finally:
        db.close()  # Closing the database session


def get_user_next_workout(user_email: str) -> Optional[WorkoutResponseSchema]:
    # Getting the next workout for the user (not yet performed)
    return get_most_recent_workout_exercises(user_email, performed=False)


def perform_workout(workout_id: int, user_email: str) -> None:
    db = db_session()  # Creating a new database session
    try:
        # Fetching the workout for the user with related exercises
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

        workout.performed = True  # Marking the workout as performed
        workout.performed_at = datetime.now(timezone.utc)  # Setting the performed at timestamp
        db.commit()  # Committing the session to save changes
        logger.info(f"Workout {workout_id} marked as performed for user {user_email} at {workout.performed_at}")

        try:
            exercise_schemas = []
            if workout.exercises:
                # Preparing the exercise schemas for the event message
                for wo_exercise in workout.exercises:
                    exercise_schemas.append(WorkoutPerformedExerciseSchema(exercise_id=wo_exercise.exercise_id))

            # Creating the event message for the performed workout
            event_message = WorkoutPerformedMessage(
                user_email=user_email,
                workout_id=workout_id,
                performed_at=workout.performed_at,
                exercises=exercise_schemas
            )

            # Publishing the event message to RabbitMQ
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
        db.rollback()  # Rolling back the session in case of a ValueError
        logger.error(f"ValueError performing workout {workout_id} for user {user_email}: {ve}", exc_info=True)
        raise
    except Exception as e:
        db.rollback()  # Rolling back the session in case of a generic exception
        logger.error(f"Generic error performing workout {workout_id} for user {user_email}: {e}", exc_info=True)
        raise
    finally:
        db.close()  # Closing the database session
