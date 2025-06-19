from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey
from database import Base
import datetime

# Define the WorkoutStatModel class, which represents the "workout_stats" table in the database
class WorkoutStatModel(Base):
    __tablename__ = "workout_stats"  # Specify the table name

    # Define the columns in the table
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Primary key, auto-incrementing ID
    user_email = Column(String, nullable=False, index=True)  # User's email, cannot be null, indexed for performance
    exercise_id = Column(Integer, nullable=False)  # Exercise ID, cannot be null
    workout_id = Column(Integer, nullable=False, index=True)  # Workout ID, cannot be null, indexed for performance
    performed_timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)  # Timestamp of when the workout was performed, cannot be null, defaults to current UTC time
    # Optional fields, can be extended if message includes them
    reps = Column(Integer, nullable=True)  # Number of reps, can be null
    weight = Column(Float, nullable=True)  # Weight used, can be null
    duration_seconds = Column(Integer, nullable=True)  # Duration in seconds, can be null

    # String representation of the object, useful for debugging
    def __repr__(self):
        return f"<WorkoutStatModel(id={self.id}, user_email='{self.user_email}', exercise_id={self.exercise_id}, workout_id={self.workout_id})>"