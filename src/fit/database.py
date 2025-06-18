import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

logger = logging.getLogger(__name__)

# Env var name (shared by both monolith & coach)
DB_ENV_VAR = "DATABASE_URL"

# Use DATABASE_URL if present, otherwise default to in‑memory SQLite
SQLALCHEMY_DATABASE_URL = os.getenv(DB_ENV_VAR, "sqlite:///:memory:")
if DB_ENV_VAR not in os.environ:
    logger.info(f"{DB_ENV_VAR} not set—falling back to in‑memory SQLite.")

# Create engine & session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

# Base declarative class
Base = declarative_base()

def get_db():
    """
    Dependency-injection helper:
    yields a session, then closes it.
    """
    db = db_session()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Imports all models so they register on Base.metadata,
    then creates tables.
    """
    from .models_db import UserExerciseHistory, UserModel  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Monolith database tables created.")
