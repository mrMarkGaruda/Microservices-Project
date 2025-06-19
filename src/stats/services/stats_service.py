# Import logging for logging messages
import logging
# Import SQLAlchemyError for database error handling
from sqlalchemy.exc import SQLAlchemyError
# Import List and Optional for type hinting
from typing import List, Optional
# Import the database session from the database module
from database import db_session
# Import the WorkoutStatModel from models_db
from models_db import WorkoutStatModel
# Import response schemas from models_dto
from models_dto import WorkoutStatResponseItemSchema, UserWorkoutStatsResponseSchema
# Import the message schema for workout performed events
from queue_messages import WorkoutPerformedMessage

# Create a logger for this module
logger = logging.getLogger(__name__)

# Function to store a workout stat in the database
def store_workout_stat(message: WorkoutPerformedMessage) -> None:
    # Create a new database session
    session = db_session()
    try:
        # Log the message being processed
        logger.info(f"Processing WorkoutPerformedMessage for user: {message.user_email}, workout_id: {message.workout_id}, performed_at: {message.performed_at}")
        logger.debug(f"Full message details: {message.model_dump_json(indent=2)}")
        # If there are no exercises in the message, log a warning and return
        if not message.exercises:
            logger.warning(f"No exercises found in WorkoutPerformedMessage for workout_id: {message.workout_id}. Nothing to store.")
            return
        # Iterate over each exercise in the message
        for exercise_info in message.exercises:
            # Create a new WorkoutStatModel entry
            stat_entry = WorkoutStatModel(
                user_email=message.user_email,
                exercise_id=exercise_info.exercise_id,
                workout_id=message.workout_id,
                performed_timestamp=message.performed_at
            )
            # Add the stat entry to the session
            session.add(stat_entry)
            logger.debug(f"Added WorkoutStatModel entry for exercise_id: {exercise_info.exercise_id}, workout_id: {message.workout_id}")
        # Commit the session to save all entries
        session.commit()
        logger.info(f"Successfully stored {len(message.exercises)} workout stat(s) for user {message.user_email}, workout_id {message.workout_id}")
    except SQLAlchemyError as e:
        # Log database errors, roll back, and re-raise
        logger.error(f"Database error storing workout stat for workout_id {message.workout_id}: {e}", exc_info=True)
        session.rollback()
        raise
    except Exception as e:
        # Log any other errors, roll back, and re-raise
        logger.error(f"Unexpected error storing workout stat for workout_id {message.workout_id}: {e}", exc_info=True)
        session.rollback()
        raise
    finally:
        # Close the session
        session.close()
        logger.debug("Database session closed after store_workout_stat.")

# Function to get all workout stats for a user
def get_user_workout_stats(user_email: str) -> Optional[UserWorkoutStatsResponseSchema]:
    # Create a new database session
    db = db_session()
    try:
        # Query all workout stats for the user, ordered by timestamp descending
        stats_query = db.query(WorkoutStatModel).filter(WorkoutStatModel.user_email == user_email).order_by(WorkoutStatModel.performed_timestamp.desc()).all()
        # If no stats are found, log and return None
        if not stats_query:
            logger.info(f"No workout stats found for user: {user_email}")
            return None
        # Convert each stat to a response schema
        stats_list = [WorkoutStatResponseItemSchema.from_orm(stat) for stat in stats_query]
        logger.info(f"Retrieved {len(stats_list)} workout stat(s) for user: {user_email}")
        # Return the user's stats as a response schema
        return UserWorkoutStatsResponseSchema(user_email=user_email, stats=stats_list)
    except SQLAlchemyError as e:
        # Log database errors and re-raise
        logger.error(f"Database error retrieving workout stats for user {user_email}: {e}", exc_info=True)
        raise
    except Exception as e:
        # Log any other errors and re-raise
        logger.error(f"Unexpected error retrieving workout stats for user {user_email}: {e}", exc_info=True)
        raise
    finally:
        # Close the session
        db.close()
        logger.debug("Database session closed after get_user_workout_stats.")