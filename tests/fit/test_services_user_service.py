"""
Unit tests for fit.services.user_service
"""
import pytest
from unittest.mock import patch, MagicMock
from src.fit.services import user_service
from src.fit.models_dto import UserSchema, UserProfileSchema

@pytest.fixture
def mock_db_session():
    with patch("src.fit.services.user_service.db_session") as mock:
        yield mock

def test_generate_random_password():
    pw = user_service.generate_random_password(12)
    assert len(pw) == 12
    assert any(c.isdigit() for c in pw)
    assert any(c.isalpha() for c in pw)
    assert any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for c in pw)

def test_hash_password():
    pw = "password123"
    hashed = user_service.hash_password(pw)
    assert isinstance(hashed, str)
    assert hashed != pw
    assert len(hashed) == 64

@patch("src.fit.services.user_service.db_session")
@patch("src.fit.services.user_service.UserModel")
def test_create_user(mock_user_model, mock_db_session):
    user = UserSchema(email="a@b.com", name="Test", role="user")
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    mock_db.close.return_value = None
    mock_user_model.return_value = MagicMock()
    resp = user_service.create_user(user)
    assert resp.email == user.email
    assert resp.name == user.name
    assert resp.role == user.role
    assert hasattr(resp, "password")
    mock_db.add.assert_called()
    mock_db.commit.assert_called()
    mock_db.refresh.assert_called()
    mock_db.close.assert_called()

@patch("src.fit.services.user_service.db_session")
@patch("src.fit.services.user_service.UserModel")
def test_get_all_users(mock_user_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_user = MagicMock(email="a@b.com", name="Test", role="user")
    mock_db.query.return_value.all.return_value = [mock_user]
    users = user_service.get_all_users()
    assert len(users) == 1
    assert users[0].email == "a@b.com"
    mock_db.close.assert_called()

@patch("src.fit.services.user_service.db_session")
@patch("src.fit.services.user_service.UserModel")
def test_update_user_profile_success(mock_user_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_user = MagicMock(email="a@b.com", name="Test", role="user", weight=None, height=None, fitness_goal=None, onboarded="false")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    profile = UserProfileSchema(weight=70, height=180, fitness_goal="Lose weight")
    resp = user_service.update_user_profile("a@b.com", profile)
    assert resp.weight == 70
    assert resp.height == 180
    assert resp.fitness_goal == "Lose weight"
    assert resp.onboarded == "true"
    mock_db.commit.assert_called()
    mock_db.refresh.assert_called()
    mock_db.close.assert_called()

@patch("src.fit.services.user_service.db_session")
@patch("src.fit.services.user_service.UserModel")
def test_update_user_profile_not_found(mock_user_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = None
    profile = UserProfileSchema(weight=70, height=180, fitness_goal="Lose weight")
    resp = user_service.update_user_profile("notfound@b.com", profile)
    assert resp is None
    mock_db.close.assert_called()

@patch("src.fit.services.user_service.db_session")
@patch("src.fit.services.user_service.UserModel")
def test_get_user_profile_success(mock_user_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_user = MagicMock(email="a@b.com", name="Test", weight=70, height=180, fitness_goal="Lose weight", onboarded="true")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    resp = user_service.get_user_profile("a@b.com")
    assert resp.email == "a@b.com"
    assert resp.weight == 70
    assert resp.height == 180
    assert resp.fitness_goal == "Lose weight"
    assert resp.onboarded == "true"
    mock_db.close.assert_called()

@patch("src.fit.services.user_service.db_session")
@patch("src.fit.services.user_service.UserModel")
def test_get_user_profile_not_found(mock_user_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = None
    resp = user_service.get_user_profile("notfound@b.com")
    assert resp is None
    mock_db.close.assert_called()
