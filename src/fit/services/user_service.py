# Import user-related schemas from the parent models_dto module
from ..models_dto import UserSchema, UserResponseSchema, UserProfileSchema, UserProfileResponseSchema
# Import the UserModel from the parent models_db module
from ..models_db import UserModel
# Import the database session from the parent database module
from ..database import db_session
# Import List and Optional for type hinting
from typing import List, Optional
# Import random for generating random passwords
import random
# Import string for character sets
import string
# Import hashlib for password hashing
import hashlib

# Function to generate a random password of specified length
def generate_random_password(length=10):
    """Generate a random password of specified length"""
    # Define the set of characters to use
    chars = string.ascii_letters + string.digits + string.punctuation
    # Randomly select characters and join them into a string
    return ''.join(random.choice(chars) for _ in range(length))

# Function to hash a password using SHA-256
def hash_password(password):
    """Hash a password using SHA-256"""
    # Encode the password and hash it
    return hashlib.sha256(password.encode()).hexdigest()

# Function to create a new user and persist it to the database
def create_user(user: UserSchema) -> UserResponseSchema:
    """
    Create a new user with a random password and persist it to the database
    """
    # Generate a random password
    random_password = generate_random_password()
    # Hash the generated password
    hashed_password = hash_password(random_password)
    
    # Convert Pydantic model to SQLAlchemy model
    db_user = UserModel(
        email=user.email,
        name=user.name,
        role=user.role,
        password_hash=hashed_password
    )
    
    # Add and commit to database
    db = db_session()
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    
    # Return response including the clear-text password (one-time reveal)
    response = UserResponseSchema(
        email=user.email,
        name=user.name,
        role=user.role,
        password=random_password
    )
    
    return response

# Function to retrieve all users from the database
def get_all_users() -> List[UserSchema]:
    """
    Retrieve all users from the database
    """
    db = db_session()
    try:
        # Query all users from the database
        db_users = db.query(UserModel).all()
        
        # Convert SQLAlchemy models to Pydantic models
        return [
            UserSchema(
                email=db_user.email,
                name=db_user.name,
                role=db_user.role
            )
            for db_user in db_users
        ]
    finally:
        db.close()

# Function to update a user's profile
def update_user_profile(email: str, profile: UserProfileSchema) -> Optional[UserProfileResponseSchema]:
    """
    Update user profile with weight, height, and fitness goal
    """
    db = db_session()
    try:
        # Find the user
        user = db.query(UserModel).filter(UserModel.email == email).first()
        # If the user does not exist, return None
        if not user:
            return None

        # Update the user's profile fields
        user.weight = profile.weight
        user.height = profile.height
        user.fitness_goal = profile.fitness_goal
        user.onboarded = "true"
        
        # Commit the changes and refresh the user
        db.commit()
        db.refresh(user)
        
        # Return the updated user profile
        return UserProfileResponseSchema(
            email=user.email,
            name=user.name,
            weight=user.weight,
            height=user.height,
            fitness_goal=user.fitness_goal,
            onboarded=user.onboarded
        )
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Function to get a user's profile information
def get_user_profile(email: str) -> Optional[UserProfileResponseSchema]:
    """
    Get user profile information
    """
    db = db_session()
    try:
        # Query the user by email
        user = db.query(UserModel).filter(UserModel.email == email).first()
        # If the user does not exist, return None
        if not user:
            return None
            
        # Return the user's profile as a response schema
        return UserProfileResponseSchema(
            email=user.email,
            name=user.name,
            weight=user.weight,
            height=user.height,
            fitness_goal=user.fitness_goal,
            onboarded=user.onboarded
        )
    finally:
        db.close()
