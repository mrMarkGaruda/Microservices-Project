import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'postgresql://fitness_user:fitness_password@localhost:5432/fitness_db'
)

# Create engine with appropriate settings
if 'sqlite' in DATABASE_URL:
    # For SQLite (testing)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # For PostgreSQL (production)
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

Base = declarative_base()

# Dependency to get db session
def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import all models here so they are registered with the metadata
    from .models_db import UserModel, MuscleGroupModel, ExerciseModel, UserExerciseHistoryModel
    
    Base.metadata.create_all(bind=engine)