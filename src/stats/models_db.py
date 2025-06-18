from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey
from .database import Base
import datetime

class WorkoutStatModel(Base):
    __tablename__ = "workout_stats"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_email = Column(String, nullable=False, index=True)
    exercise_id = Column(Integer, nullable=False)
    workout_id = Column(Integer, nullable=False, index=True) # From the monolith's workout
    performed_timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    # Optional fields, can be extended if message includes them
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<WorkoutStatModel(id={self.id}, user_email='{self.user_email}', exercise_id={self.exercise_id}, workout_id={self.workout_id})>"