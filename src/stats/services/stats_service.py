import logging
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from ..database import db_session
from models_db import WorkoutStatModel
from models_dto import WorkoutStatResponseItemSchema, UserWorkoutStatsResponseSchema
from queue_messages import WorkoutPerformedMessage

logger = logging.getLogger(__name__)

def store_workout_stat(message: WorkoutPerformedMessage) -> None:
    session = db_session()
    try:
        logger.info(f"Processing WorkoutPerformedMessage for user: {message.user_email}, workout_id: {message.workout_id}, performed_at: {message.performed_at}")
        logger.debug(f"Full message details: {message.model_dump_json(indent=2)}")
        if not message.exercises:
            logger.warning(f"No exercises found in WorkoutPerformedMessage for workout_id: {message.workout_id}. Nothing to store.")
            return
        for exercise_info in message.exercises:
            stat_entry = WorkoutStatModel(
                user_email=message.user_email,
                exercise_id=exercise_info.exercise_id,
                workout_id=message.workout_id,
                performed_timestamp=message.performed_at
            )
            session.add(stat_entry)
            logger.debug(f"Added WorkoutStatModel entry for exercise_id: {exercise_info.exercise_id}, workout_id: {message.workout_id}")
        session.commit()
        logger.info(f"Successfully stored {len(message.exercises)} workout stat(s) for user {message.user_email}, workout_id {message.workout_id}")
    except SQLAlchemyError as e:
        logger.error(f"Database error storing workout stat for workout_id {message.workout_id}: {e}", exc_info=True)
        session.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error storing workout stat for workout_id {message.workout_id}: {e}", exc_info=True)
        session.rollback()
        raise
    finally:
        session.close()
        logger.debug("Database session closed after store_workout_stat.")

def get_user_workout_stats(user_email: str) -> Optional[UserWorkoutStatsResponseSchema]:
    db = db_session()
    try:
        stats_query = db.query(WorkoutStatModel).filter(WorkoutStatModel.user_email == user_email).order_by(WorkoutStatModel.performed_timestamp.desc()).all()
        if not stats_query:
            logger.info(f"No workout stats found for user: {user_email}")
            return None
        stats_list = [WorkoutStatResponseItemSchema.from_orm(stat) for stat in stats_query]
        logger.info(f"Retrieved {len(stats_list)} workout stat(s) for user: {user_email}")
        return UserWorkoutStatsResponseSchema(user_email=user_email, stats=stats_list)
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving workout stats for user {user_email}: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving workout stats for user {user_email}: {e}", exc_info=True)
        raise
    finally:
        db.close()
        logger.debug("Database session closed after get_user_workout_stats.")