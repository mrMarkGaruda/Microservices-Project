"""
Unit tests for fit.services.auth_service
"""
import pytest
from unittest.mock import patch, MagicMock
from src.fit.services import auth_service
from src.fit.models_db import UserModel
import jwt
import os
import datetime
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

def test_create_access_token():
    token = auth_service.create_access_token({"sub": "test@example.com"})
    assert isinstance(token, str)
    decoded = jwt.decode(token, auth_service.SECRET_KEY, algorithms=["HS256"])
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded

def test_decode_token_valid():
    token = auth_service.create_access_token({"sub": "test@example.com"})
    payload = auth_service.decode_token(token)
    assert payload["sub"] == "test@example.com"

def test_decode_token_expired():
    expired_token = jwt.encode({"sub": "test@example.com", "exp": datetime.datetime.utcnow() - datetime.timedelta(seconds=1)}, auth_service.SECRET_KEY, algorithm="HS256")
    payload = auth_service.decode_token(expired_token)
    assert payload["error"] == "Token expired"

def test_decode_token_invalid():
    payload = auth_service.decode_token("invalid.token")
    assert payload["error"] == "Invalid token"

@patch("src.fit.services.auth_service.db_session")
@patch("src.fit.services.auth_service.UserModel")
def test_authenticate_user_success(mock_user_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_user = MagicMock(email="a@b.com", password_hash=auth_service.hash_password("pw"))
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    user = auth_service.authenticate_user("a@b.com", "pw")
    assert user == mock_user
    mock_db.close.assert_called()

@patch("src.fit.services.auth_service.db_session")
@patch("src.fit.services.auth_service.UserModel")
def test_authenticate_user_wrong_password(mock_user_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_user = MagicMock(email="a@b.com", password_hash=auth_service.hash_password("pw"))
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    user = auth_service.authenticate_user("a@b.com", "wrongpw")
    assert user is None
    mock_db.close.assert_called()

@patch("src.fit.services.auth_service.db_session")
@patch("src.fit.services.auth_service.UserModel")
def test_authenticate_user_not_found(mock_user_model, mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = None
    user = auth_service.authenticate_user("notfound@b.com", "pw")
    assert user is None
    mock_db.close.assert_called()

# Decorator tests
from flask import Flask, jsonify

def make_flask_request_context(headers=None):
    app = Flask(__name__)
    app.config['TESTING'] = True
    with app.test_request_context(headers=headers):
        yield

def test_admin_required_decorator_valid():
    token = auth_service.create_access_token({"sub": "admin@b.com", "role": "admin"})
    @auth_service.admin_required
    def endpoint():
        return "ok"
    with make_flask_request_context(headers={"Authorization": f"Bearer {token}"}):
        assert endpoint() == "ok"

def test_admin_required_decorator_no_header():
    @auth_service.admin_required
    def endpoint():
        return "ok"
    with make_flask_request_context():
        resp, code = endpoint()
        assert code == 401
        assert "Authorization header missing" in resp.json["error"]

def test_admin_required_decorator_invalid_role():
    token = auth_service.create_access_token({"sub": "user@b.com", "role": "user"})
    @auth_service.admin_required
    def endpoint():
        return "ok"
    with make_flask_request_context(headers={"Authorization": f"Bearer {token}"}):
        resp, code = endpoint()
        assert code == 403
        assert "Admin privileges required" in resp.json["error"]

def test_jwt_required_decorator_valid():
    token = auth_service.create_access_token({"sub": "user@b.com", "role": "user"})
    @auth_service.jwt_required
    def endpoint():
        return "ok"
    with make_flask_request_context(headers={"Authorization": f"Bearer {token}"}):
        assert endpoint() == "ok"

def test_jwt_required_decorator_no_header():
    @auth_service.jwt_required
    def endpoint():
        return "ok"
    with make_flask_request_context():
        resp, code = endpoint()
        assert code == 401
        assert "Authorization header missing" in resp.json["error"]

def test_api_key_required_decorator_valid():
    os.environ["FIT_API_KEY"] = "testkey"
    @auth_service.api_key_required
    def endpoint():
        return "ok"
    with make_flask_request_context(headers={"X-API-Key": "testkey"}):
        assert endpoint() == "ok"

def test_api_key_required_decorator_missing():
    @auth_service.api_key_required
    def endpoint():
        return "ok"
    with make_flask_request_context():
        resp, code = endpoint()
        assert code == 401
        assert "X-API-Key header missing" in resp.json["error"]

def test_api_key_required_decorator_invalid():
    os.environ["FIT_API_KEY"] = "testkey"
    @auth_service.api_key_required
    def endpoint():
        return "ok"
    with make_flask_request_context(headers={"X-API-Key": "wrongkey"}):
        resp, code = endpoint()
        assert code == 401
        assert "Invalid API key" in resp.json["error"]

def test_api_key_required_decorator_server_not_configured():
    if "FIT_API_KEY" in os.environ:
        del os.environ["FIT_API_KEY"]
    @auth_service.api_key_required
    def endpoint():
        return "ok"
    with make_flask_request_context(headers={"X-API-Key": "anykey"}):
        resp, code = endpoint()
        assert code == 500
        assert "API key not configured on server" in resp.json["error"]
