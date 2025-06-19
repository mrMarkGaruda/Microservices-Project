# Import BaseModel from pydantic for data validation
from pydantic import BaseModel
# Import List and Optional for type hinting
from typing import List, Optional
# Import datetime for date/time fields
from datetime import datetime

# Define the schema for a single workout stat response item
class WorkoutStatResponseItemSchema(BaseModel):
    exercise_id: int  # ID of the exercise
    workout_id: int  # ID of the workout
    performed_timestamp: datetime  # Timestamp when the exercise was performed
    reps: Optional[int] = None  # Number of repetitions (optional)
    weight: Optional[float] = None  # Weight used (optional)
    duration_seconds: Optional[int] = None  # Duration in seconds (optional)

    class Config:
        orm_mode = True # Enable ORM mode for Pydantic V1
        # from_attributes = True # Pydantic V2 (commented out)

# Define the schema for a user's workout stats response
class UserWorkoutStatsResponseSchema(BaseModel):
    user_email: str  # Email of the user
    stats: List[WorkoutStatResponseItemSchema]  # List of workout stat items