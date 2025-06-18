import pytest
import os
import tempfile
import jwt
import datetime
from unittest.mock import MagicMock, patch
from decimal import Decimal

# Set test environment variables before importing apps
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('BILLING_DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('STATS_DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('FIT_API_KEY', 'test-api-key')
os.environ.setdefault('BOOTSTRAP_KEY', 'bootstrap-secret-key')
os.environ.setdefault('RABBITMQ_HOST', 'localhost')
os.environ.setdefault('RABBITMQ_PORT', '5672')
os.environ.setdefault('RABBITMQ_USER', 'guest')
os.environ.setdefault('RABBITMQ_PASS', 'guest')
os.environ.setdefault('LOG_LEVEL', 'ERROR')

# Import all apps for testing
from src.fit.app import app as fit_app
from src.coach.app import app as coach_app
from src.billing.app import app as billing_app
from src.stats.app import app as stats_app

# Import database modules
from src.fit.database import init_db as fit_init_db, db_session as fit_db_session
from src.fit.models_db import Base as FitBase
from src.coach.database import init_db as coach_init_db, db_session as coach_db_session
from src.coach.models_db import Base as CoachBase
from src.billing.database import init_db as billing_init_db, db_session as billing_db_session
from src.billing.models_db import Base as BillingBase
from src.stats.database import init_db as stats_init_db, db_session as stats_db_session
from src.stats.models_db import Base as StatsBase

# Common test data
TEST_USER_EMAIL = "test@example.com"
TEST_ADMIN_EMAIL = "admin@example.com"
TEST_PASSWORD = "testpassword123"
TEST_BOOTSTRAP_KEY = "bootstrap-secret-key"

@pytest.fixture
def fit_client():
    """Flask test client for fit service"""
    fit_app.config['TESTING'] = True
    fit_app.config['DATABASE_URL'] = "sqlite:///:memory:"
    
    with fit_app.test_client() as client:
        with fit_app.app_context():
            fit_init_db()
        yield client

@pytest.fixture
def coach_client():
    """Flask test client for coach service"""
    coach_app.config['TESTING'] = True
    coach_app.config['DATABASE_URL'] = "sqlite:///:memory:"
    
    with coach_app.test_client() as client:
        with coach_app.app_context():
            coach_init_db()
        yield client

@pytest.fixture
def billing_client():
    """Flask test client for billing service"""
    billing_app.config['TESTING'] = True
    billing_app.config['BILLING_DATABASE_URL'] = "sqlite:///:memory:"
    
    with billing_app.test_client() as client:
        with billing_app.app_context():
            billing_init_db()
        yield client

@pytest.fixture
def stats_client():
    """Flask test client for stats service"""
    stats_app.config['TESTING'] = True
    stats_app.config['STATS_DATABASE_URL'] = "sqlite:///:memory:"
    
    with stats_app.test_client() as client:
        with stats_app.app_context():
            stats_init_db()
        yield client

@pytest.fixture
def mock_db():
    """Mock database session"""
    return MagicMock()

@pytest.fixture
def valid_jwt_token():
    """Generate a valid JWT token for testing"""
    payload = {
        "sub": TEST_USER_EMAIL,
        "name": "Test User",
        "role": "user",
        "iss": "fit-api",
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, "fit-secret-key", algorithm="HS256")

@pytest.fixture
def valid_admin_token():
    """Generate a valid admin JWT token for testing"""
    payload = {
        "sub": TEST_ADMIN_EMAIL,
        "name": "Test Admin",
        "role": "admin",
        "iss": "fit-api",
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, "fit-secret-key", algorithm="HS256")

@pytest.fixture
def expired_jwt_token():
    """Generate an expired JWT token for testing"""
    payload = {
        "sub": TEST_USER_EMAIL,
        "name": "Test User",
        "role": "user",
        "iss": "fit-api",
        "iat": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2),
        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, "fit-secret-key", algorithm="HS256")

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": TEST_USER_EMAIL,
        "name": "Test User",
        "role": "user",
        "password": TEST_PASSWORD
    }

@pytest.fixture
def sample_admin_data():
    """Sample admin data for testing"""
    return {
        "email": TEST_ADMIN_EMAIL,
        "name": "Test Admin",
        "role": "admin",
        "password": TEST_PASSWORD
    }

@pytest.fixture
def sample_billing_plan():
    """Sample billing plan for testing"""
    return {
        "plan_id_name": "basic",
        "name": "Basic Plan",
        "price": Decimal("9.99"),
        "currency": "USD",
        "duration_days": 30,
        "features_description": "Basic features",
        "is_active": True
    }

@pytest.fixture
def sample_exercise_data():
    """Sample exercise data for testing"""
    return {
        "id": 1,
        "name": "Push-up",
        "description": "A basic push-up exercise",
        "difficulty": 3,
        "equipment": "None",
        "instructions": "Get into plank position and push up"
    }

@pytest.fixture
def sample_muscle_group_data():
    """Sample muscle group data for testing"""
    return {
        "id": 1,
        "name": "Chest",
        "body_part": "Upper Body",
        "description": "Chest muscles"
    }

@pytest.fixture
def sample_workout_data():
    """Sample workout data for testing"""
    return {
        "id": 1,
        "user_email": TEST_USER_EMAIL,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
        "performed_at": None,
        "performed": False
    }

@pytest.fixture
def mock_rabbitmq():
    """Mock RabbitMQ service"""
    with patch('src.fit.services.rabbitmq_service.rabbitmq_service') as mock:
        mock.publish_workout_performed_event.return_value = True
        mock.publish_create_wod_message.return_value = True
        yield mock

@pytest.fixture
def mock_requests():
    """Mock requests module"""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        yield {'get': mock_get, 'post': mock_post}

# Legacy fixtures for backward compatibility
@pytest.fixture
def client():
    """Legacy client fixture - points to fit_client for backward compatibility"""
    return fit_client()

@pytest.fixture
def db():
    """Legacy db fixture"""
    fit_init_db()
    db = fit_db_session()
    yield db
    db.close()
    FitBase.metadata.drop_all(bind=db.get_bind())