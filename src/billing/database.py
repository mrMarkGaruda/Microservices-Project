import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import logging

logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = os.getenv("BILLING_DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    logger.error("BILLING_DATABASE_URL environment variable not set.")
    raise ValueError("BILLING_DATABASE_URL environment variable not set.")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

Base = declarative_base()

def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from . import models_db
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Billing database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing billing database: {e}", exc_info=True)
        raise
