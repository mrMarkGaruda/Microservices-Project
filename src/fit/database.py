import os  # Import the os module to access environment variables
from sqlalchemy import create_engine  # Import create_engine to create a new SQLAlchemy engine instance
from sqlalchemy.ext.declarative import declarative_base  # Import declarative_base to create a base class for declarative models
from sqlalchemy.orm import sessionmaker, scoped_session  # Import sessionmaker and scoped_session to create and manage database sessions

# Database connection settings from docker-compose.yml
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")  # Get the database URL from the environment variable

engine = create_engine(SQLALCHEMY_DATABASE_URL)  # Create a new SQLAlchemy engine instance
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Create a session factory bound to the engine
db_session = scoped_session(SessionLocal)  # Create a scoped session that provides a registry for sessions

Base = declarative_base()  # Create a base class for declarative models

# Dependency to get db session
def get_db():
    db = db_session()  # Create a new session
    try:
        yield db  # Yield the session to the caller
    finally:
        db.close()  # Close the session when done

def init_db():
    # Import all models here so they are registered with the metadata
    from .models_db import UserExerciseHistory, UserModel  # Import the models to register them with the metadata
    
    Base.metadata.create_all(bind=engine)  # Create all tables in the database that are defined by the models