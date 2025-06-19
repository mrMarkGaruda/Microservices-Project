# Import os for environment variable access
import os
# Import SQLAlchemy engine and ORM components
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
# Import logging for logging messages
import logging

# Create a logger for this module
logger = logging.getLogger(__name__)

# Get the database URL from the environment variable
SQLALCHEMY_DATABASE_URL = os.getenv("STATS_DATABASE_URL")
# If the environment variable is not set, log an error and raise an exception
if not SQLALCHEMY_DATABASE_URL:
    logger.error("STATS_DATABASE_URL environment variable not set.")
    raise ValueError("STATS_DATABASE_URL environment variable not set.")

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# Create a session factory for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Create a scoped session for thread-safe sessions
db_session = scoped_session(SessionLocal)

# Create a base class for declarative models
Base = declarative_base()

# Function to get a database session (for dependency injection)
def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()

# Function to initialize the database (create tables)
def init_db():
    import models_db
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Stats database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing stats database: {e}", exc_info=True)
        raise