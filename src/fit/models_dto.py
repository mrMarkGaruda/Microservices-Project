from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

# User-related DTOs
class UserSchema(BaseModel):
    email: str # User's email address
    name: str # User's name
    role: str # User's role (e.g., admin, user)

class TokenSchema(BaseModel):
    access_token: str # JWT access token
    token_type: str # Type of the token (e.g., Bearer)


class UserResponseSchema(UserSchema):
    password: str # User's password (for response, not recommended to expose)

class LoginSchema(BaseModel):
    email: str # User's email address
    password: str # User's password
 
class UserProfileSchema(BaseModel):
    weight: Optional[float] = None # User's weight in kg
    height: Optional[float] = None # User's height in cm
    fitness_goal: Optional[str] = None # User's fitness goal
    onboarded: Optional[str] = "false" # Onboarding status

class UserProfileResponseSchema(BaseModel):
    email: str # User's email address
    name: str # User's name
    weight: Optional[float] = None # User's weight in kg
    height: Optional[float] = None # User's height in cm
    fitness_goal: Optional[str] = None # User's fitness goal
    onboarded: Optional[str] = "false" # Onboarding status

class UserProfileUpdate(BaseModel):
    weight: Optional[float] = None # User's weight in kg
    height: Optional[float] = None # User's height in cm
    fitness_goal: Optional[str] = None # User's fitness goal
    onboarded: Optional[str] = None # Onboarding status

class User(UserSchema):
    weight: Optional[float] = None # User's weight in kg
    height: Optional[float] = None # User's height in cm
    fitness_goal: Optional[str] = None # User's fitness goal
    onboarded: str = "false" # Onboarding status

# Muscle Group DTOs
class MuscleGroupBase(BaseModel):
    name: str # Name of the muscle group
    body_part: str # Body part the muscle group is located
    description: Optional[str] = None # Description of the muscle group

class MuscleGroupUpdate(BaseModel):
    name: Optional[str] = None # Name of the muscle group
    body_part: Optional[str] = None # Body part the muscle group is located
    description: Optional[str] = None # Description of the muscle group

class MuscleGroup(MuscleGroupBase):
    id: int # Unique identifier for the muscle group

# Exercise DTOs
class ExerciseMuscleGroup(BaseModel):
    muscle_group_id: int # ID of the muscle group
    is_primary: bool = False # Whether this is the primary muscle group targeted

class ExerciseBase(BaseModel):
    name: str # Name of the exercise
    description: Optional[str] = None # Description of the exercise
    difficulty: int = Field(..., ge=1, le=5) # Difficulty rating of the exercise (1 to 5)
    equipment: Optional[str] = None # Equipment needed for the exercise
    instructions: Optional[str] = None # Instructions on how to perform the exercise

class ExerciseCreate(ExerciseBase):
    muscle_groups: List[ExerciseMuscleGroup] # List of muscle groups targeted by the exercise

class ExerciseUpdate(BaseModel):
    name: Optional[str] = None # Name of the exercise
    description: Optional[str] = None # Description of the exercise
    difficulty: Optional[int] = Field(None, ge=1, le=5) # Difficulty rating of the exercise (1 to 5)
    equipment: Optional[str] = None # Equipment needed for the exercise
    instructions: Optional[str] = None # Instructions on how to perform the exercise
    muscle_groups: Optional[List[ExerciseMuscleGroup]] = None # List of muscle groups targeted by the exercise

class MuscleGroupWithPrimary(MuscleGroup):
    is_primary: bool # Whether this muscle group is the primary one targeted

class ExerciseId(BaseModel):
    id: int # Unique identifier for the exercise

class MuscleGroupImpact(BaseModel):
    id: int # Unique identifier for the muscle group impact
    name: str # Name of the muscle group
    body_part: str # Body part the muscle group is located
    is_primary: bool # Whether this is the primary muscle group targeted
    intensity: float  # Calculated based on exercise difficulty (0.0 to 1.0)

class WodExerciseSchema(BaseModel):
    id: int # Unique identifier for the workout exercise
    name: str # Name of the workout exercise
    description: str # Description of the workout exercise
    difficulty: int # Difficulty level of the workout exercise

class WorkoutResponseSchema(BaseModel):
    id: int # Unique identifier for the workout
    exercises: List[WodExerciseSchema] # List of exercises in the workout

class RegisterWorkoutSchema(BaseModel):
    email: str # User's email address
    exercises: List[int] = Field(..., description="List of exercise IDs performed in the workout") # List of exercise IDs

class WorkoutExercisesList(BaseModel):
    workout_id: int # Unique identifier for the workout
    exercises: List[int] # List of exercise IDs in the workout

class RegisterWorkoutExerciseSchema(BaseModel):
    exercise_id: int # Unique identifier for the exercise
    reps: int = 0 # Number of repetitions
    weight: float = 0.0 # Weight used for the exercise
    duration_seconds: int = 0 # Duration of the exercise in seconds

class ExerciseResponseSchema(BaseModel):
    id: int # Unique identifier for the exercise
    name: str # Name of the exercise
    description: str = "" # Description of the exercise
    difficulty: int = 1 # Difficulty level of the exercise
    equipment: str = "" # Equipment needed for the exercise
    instructions: str = "" # Instructions on how to perform the exercise
