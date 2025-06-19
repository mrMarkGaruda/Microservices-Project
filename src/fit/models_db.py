from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, Table, Text, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .database import Base
import datetime

# Define the UserModel class, which represents the users table in the database
class UserModel(Base):
    __tablename__ = "users"  # Specify the name of the table

    # Define the columns in the users table
    email = Column(String, primary_key=True, index=True)  # User's email, primary key
    name = Column(String, nullable=False)  # User's name
    role = Column(String, nullable=False)  # User's role (e.g., admin, member)
    password_hash = Column(String, nullable=False)  # Hashed password for the user
    
    # Profile information (nullable as they'll be filled during onboarding)
    weight = Column(Float, nullable=True)  # User's weight
    height = Column(Float, nullable=True)  # User's height
    fitness_goal = Column(String, nullable=True)  # User's fitness goal
    onboarded = Column(String, default="false", nullable=False)  # Onboarding status

    # Relationships
    workouts = relationship("WorkoutModel", back_populates="user")  # Relationship to workouts table

    # String representation of the object for debugging
    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.name}', role='{self.role}')>"  # Return a string representation of the user

# Define the WorkoutModel class, which represents the workouts table in the database
class WorkoutModel(Base):
    __tablename__ = 'workouts'  # Specify the name of the table
    
    # Define the columns in the workouts table
    id = Column(Integer, primary_key=True)  # Workout ID, primary key
    user_email = Column(String, ForeignKey('users.email'), nullable=False)  # User's email, foreign key
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)  # Creation timestamp
    performed_at = Column(DateTime, nullable=True)  # Performance timestamp
    
    # Relationships
    user = relationship("UserModel", back_populates="workouts")  # Relationship to users table
    exercises = relationship("UserExerciseHistory", back_populates="workout")  # Relationship to exercise history

    # String representation of the object for debugging
    def __repr__(self):
        return f"<Workout(id={self.id}, user_email='{self.user_email}', created_at='{self.created_at}', performed_at='{self.performed_at}')>"  # Return a string representation of the workout

# Define the UserExerciseHistory class, which represents the user_exercise_history table in the database
class UserExerciseHistory(Base):
    __tablename__ = 'user_exercise_history'  # Specify the name of the table
    
    # Define the columns in the user_exercise_history table
    id = Column(Integer, primary_key=True)  # History ID, primary key
    workout_id = Column(Integer, ForeignKey('workouts.id'), nullable=False)  # Workout ID, foreign key
    exercise_id = Column(Integer, nullable=False)  # Exercise ID
    
    # Relationships
    workout = relationship("WorkoutModel", back_populates="exercises")  # Relationship to workouts table

    # String representation of the object for debugging
    def __repr__(self):
        return f"<UserExerciseHistory(id={self.id}, workout_id='{self.workout_id}', exercise_id='{self.exercise_id}')>"  # Return a string representation of the exercise history record