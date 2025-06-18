import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

logger = logging.getLogger(__name__)

# Environment variable name for billing service
DB_ENV_VAR = "BILLING_DATABASE_URL"

# Use the env var if set, otherwise fall back to in‑memory SQLite (great for tests/dev)
SQLALCHEMY_DATABASE_URL = os.getenv(DB_ENV_VAR, "sqlite:///:memory:")
if DB_ENV_VAR not in os.environ:
    logger.info(f"{DB_ENV_VAR} not set—falling back to in‑memory SQLite.")

# Create engine and session factory
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

# Base class for declarative models
Base = declarative_base()

def get_db():
    """
    Dependency for FastAPI or Flask to get a session.
    Yields a SQLAlchemy session and then closes it.
    """
    db = db_session()
    try:
        yield db
    finally:
        db.close()

# Import your models here so Base.metadata knows about them
from .models_db import *  # Replace * with actual model names, e.g., BillingModel, InvoiceModel

def init_db():
    """
    Create all tables. Import your models so that they are registered on Base.metadata.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Billing database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing billing database: {e}", exc_info=True)
        raise
