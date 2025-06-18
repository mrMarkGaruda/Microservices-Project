"""
Comprehensive tests for fit Flask app endpoints and integration.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.fit.app import app, BOOTSTRAP_KEY

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "UP"

def test_bootstrap_admin_invalid_key(client):
    response = client.post("/bootstrap/admin", headers={"X-Bootstrap-Key": "wrong-key"}, json={})
    assert response.status_code == 401
    assert "Invalid bootstrap key" in response.json["error"]

@patch("src.fit.app.db_session")
@patch("src.fit.app.UserModel")
def test_bootstrap_admin_already_exists(mock_user_model, mock_db_session, client):
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = True
    mock_db_session.return_value = mock_db
    response = client.post("/bootstrap/admin", headers={"X-Bootstrap-Key": BOOTSTRAP_KEY}, json={"username": "admin", "email": "admin@example.com", "password": "pass"})
    assert response.status_code == 409
    assert "Admin user already exists" in response.json["error"]
    mock_db.close.assert_called_once()

@patch("src.fit.app.create_user_service")
@patch("src.fit.app.UserSchema")
@patch("src.fit.app.db_session")
@patch("src.fit.app.UserModel")
def test_bootstrap_admin_success(mock_user_model, mock_db_session, mock_user_schema, mock_create_user_service, client):
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = False
    mock_db_session.return_value = mock_db
    mock_user_schema.model_validate.return_value = MagicMock()
    mock_created_admin = MagicMock()
    mock_created_admin.model_dump.return_value = {"id": 1, "username": "admin", "role": "admin"}
    mock_create_user_service.return_value = mock_created_admin
    response = client.post("/bootstrap/admin", headers={"X-Bootstrap-Key": BOOTSTRAP_KEY}, json={"username": "admin", "email": "admin@example.com", "password": "pass"})
    assert response.status_code == 201
    assert response.json["username"] == "admin"
    assert response.json["role"] == "admin"
    mock_db.close.assert_called_once()

@patch("src.fit.app.db_session")
@patch("src.fit.app.UserModel")
def test_bootstrap_admin_validation_error(mock_user_model, mock_db_session, client):
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = False
    mock_db_session.return_value = mock_db
    with patch("src.fit.app.UserSchema.model_validate", side_effect=Exception("Validation error")):
        response = client.post("/bootstrap/admin", headers={"X-Bootstrap-Key": BOOTSTRAP_KEY}, json={"username": "admin"})
        assert response.status_code == 500 or response.status_code == 400
        assert "error" in response.json
    mock_db.close.assert_called_once()

@patch("src.fit.app.db_session")
@patch("src.fit.app.UserModel")
def test_bootstrap_admin_unexpected_exception(mock_user_model, mock_db_session, client):
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = False
    mock_db_session.return_value = mock_db
    with patch("src.fit.app.UserSchema.model_validate", side_effect=Exception("Some error")):
        response = client.post("/bootstrap/admin", headers={"X-Bootstrap-Key": BOOTSTRAP_KEY}, json={"username": "admin"})
        assert response.status_code == 500 or response.status_code == 400
        assert "error" in response.json
    mock_db.close.assert_called_once()

# Note: Blueprint endpoints (user, auth, workout) should be tested in their respective test files for full coverage.
