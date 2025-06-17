from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class WorkoutPerformedExerciseSchema(BaseModel):
    exercise_id: int

class WorkoutPerformedMessage(BaseModel):
    user_email: str
    workout_id: int
    performed_at: datetime
    exercises: List[WorkoutPerformedExerciseSchema] = Field(..., description="List of exercises performed in the workout")
    event_type: str = "WorkoutPerformed"
    event_version: str = "1.0"