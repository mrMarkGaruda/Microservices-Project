"""
Comprehensive tests for coach Flask app endpoints and integration.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.coach.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "UP"

@patch("src.coach.app.get_all_exercises")
def test_get_exercises_success(mock_get_all_exercises, client):
    mock_get_all_exercises.return_value = [
        {"id": 1, "name": "Pushup"},
        {"id": 2, "name": "Squat"}
    ]
    response = client.get("/exercises")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert response.json[0]["name"] == "Pushup"

@patch("src.coach.app.get_all_exercises", side_effect=Exception("DB error"))
def test_get_exercises_error(mock_get_all_exercises, client):
    response = client.get("/exercises")
    assert response.status_code == 500
    assert "error" in response.json

# Add similar tests for /exercises/<id>, /createWod, and all other endpoints, including error and edge cases.
