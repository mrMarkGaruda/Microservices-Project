from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WorkoutStatResponseItemSchema(BaseModel):
    exercise_id: int
    workout_id: int
    performed_timestamp: datetime
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration_seconds: Optional[int] = None

    class Config:
        orm_mode = True # Pydantic V1
        # from_attributes = True # Pydantic V2

class UserWorkoutStatsResponseSchema(BaseModel):
    user_email: str
    stats: List[WorkoutStatResponseItemSchema]