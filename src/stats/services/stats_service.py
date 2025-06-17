import logging
from typing import List, Optional
from ..database import db_session
from ..models_db import WorkoutStatModel
from ..models_dto import WorkoutStatResponseItemSchema, UserWorkoutStatsResponseSchema
from ..queue_messages import WorkoutPerformedMessage

logger = logging.getLogger(__name__)

def store_workout_stat(message: WorkoutPerformedMessage) -> None:
    db = None
    try:
        logger.info(f"Received workout stat to store (placeholder): User {message.user_email}, Workout ID {message.workout_id}, Performed at {message.performed_at}")
        logger.debug(f"Full message details: {message.model_dump_json(indent=2)}")
    except Exception as e:
        logger.error(f"Error in placeholder store_workout_stat: {e}", exc_info=True)
        raise

def get_user_workout_stats(user_email: str) -> Optional[UserWorkoutStatsResponseSchema]:
    db = db_session()
    try:
        stats_query = db.query(WorkoutStatModel).filter(WorkoutStatModel.user_email == user_email).order_by(WorkoutStatModel.performed_timestamp.desc()).all()
        if not stats_query:
            return None

        stats_list = [WorkoutStatResponseItemSchema.from_orm(stat) for stat in stats_query]
        
        return UserWorkoutStatsResponseSchema(user_email=user_email, stats=stats_list)
    except Exception as e:
        logger.error(f"Error retrieving workout stats for user {user_email}: {e}", exc_info=True)
        raise
    finally:
        db.close()