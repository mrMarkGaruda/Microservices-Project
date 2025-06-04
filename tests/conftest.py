import pytest
import os
import tempfile
from src.fit.app import app
from src.fit.database import init_db, db_session
from src.fit.models_db import Base

@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    # Use SQLite for tests to avoid affecting production DB
    db_fd, db_path = tempfile.mkstemp()
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db_path}')
    yield
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

@pytest.fixture
def db():
    init_db()
    db = db_session()
    yield db
    db.close()
    Base.metadata.drop_all(bind=db.get_bind())