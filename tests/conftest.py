import pytest
import os
import tempfile
from src.fit.app import app
from src.fit.database import init_db, db_session
from src.fit.models_db import Base

@pytest.fixture
def client():
    # Create a temporary file to use as our database
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    
    # Teardown
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def db():
    # Set up the database
    init_db()
    db = db_session()
    yield db
    
    # Teardown
    db.close()
    Base.metadata.drop_all(bind=db.get_bind())