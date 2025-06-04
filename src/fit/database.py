import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

def get_engine_and_session():
    db_url = os.getenv(
        'DATABASE_URL', 
        'postgresql://fitness_user:fitness_password@localhost:5432/fitness_db'
    )
    if 'sqlite' in db_url:
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, scoped_session(SessionLocal)

# Default engine/session for app usage
engine, db_session = get_engine_and_session()
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

# For testing: allow re-initialization of engine/session after env change
def reload_engine_and_session():
    global engine, db_session
    engine, db_session = get_engine_and_session()

def get_db_session():
    _, session = get_engine_and_session()
    return session