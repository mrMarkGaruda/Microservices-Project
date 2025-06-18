"""
Comprehensive tests for fit blueprint endpoints
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.fit.app import app
from src.fit.models_dto import (
    UserSchema, UserProfileSchema, ExerciseResponseSchema, 
    WorkoutResponseSchema, RegisterWorkoutSchema
)


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_jwt_headers():
    """JWT headers for protected endpoints"""
    return {"Authorization": "Bearer valid-jwt-token"}


@pytest.fixture
def valid_api_key_headers():
    """API key headers for internal endpoints"""
    return {"X-API-Key": "test-api-key"}


@pytest.fixture
def admin_jwt_headers():
    """JWT headers for admin endpoints"""
    return {"Authorization": "Bearer admin-jwt-token"}


class TestUserBlueprint:
    """Test user blueprint endpoints"""
    
    @patch("src.fit.blueprints.user_blueprint.create_user_service")
    @patch("src.fit.blueprints.user_blueprint.admin_required", lambda f: f)
    def test_create_user_success(self, mock_create_user, client, admin_jwt_headers):
        """Test successful user creation"""
        mock_user = UserSchema(email="test@example.com", name="Test User", role="user")
        mock_create_user.return_value = mock_user
        
        payload = {
            "email": "test@example.com",
            "name": "Test User",
            "role": "user",
            "password": "password123"
        }
        
        response = client.post("/users", json=payload, headers=admin_jwt_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        
        mock_create_user.assert_called_once()

    @patch("src.fit.blueprints.user_blueprint.admin_required", lambda f: f)
    def test_create_user_validation_error(self, client, admin_jwt_headers):
        """Test user creation with validation error"""
        payload = {
            "email": "invalid-email",
            "name": "",
            "role": "user"
        }
        
        response = client.post("/users", json=payload, headers=admin_jwt_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    @patch("src.fit.blueprints.user_blueprint.create_user_service")
    @patch("src.fit.blueprints.user_blueprint.admin_required", lambda f: f)
    def test_create_user_service_error(self, mock_create_user, client, admin_jwt_headers):
        """Test user creation with service error"""
        mock_create_user.side_effect = Exception("Database error")
        
        payload = {
            "email": "test@example.com",
            "name": "Test User",
            "role": "user",
            "password": "password123"
        }
        
        response = client.post("/users", json=payload, headers=admin_jwt_headers)
        
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data

    @patch("src.fit.blueprints.user_blueprint.get_all_users_service")
    @patch("src.fit.blueprints.user_blueprint.admin_required", lambda f: f)
    def test_get_all_users_success(self, mock_get_all_users, client, admin_jwt_headers):
        """Test successful retrieval of all users"""
        mock_users = [
            UserSchema(email="user1@example.com", name="User 1", role="user"),
            UserSchema(email="user2@example.com", name="User 2", role="user")
        ]
        mock_get_all_users.return_value = mock_users
        
        response = client.get("/users", headers=admin_jwt_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]["email"] == "user1@example.com"
        assert data[1]["email"] == "user2@example.com"

    @patch("src.fit.blueprints.user_blueprint.get_all_users_service")
    @patch("src.fit.blueprints.user_blueprint.admin_required", lambda f: f)
    def test_get_all_users_service_error(self, mock_get_all_users, client, admin_jwt_headers):
        """Test get all users with service error"""
        mock_get_all_users.side_effect = Exception("Database error")
        
        response = client.get("/users", headers=admin_jwt_headers)
        
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data

    @patch("src.fit.blueprints.user_blueprint.get_user_profile")
    @patch("src.fit.blueprints.user_blueprint.jwt_required")
    def test_get_profile_success(self, mock_jwt_required, mock_get_profile, client, valid_jwt_headers):
        """Test successful profile retrieval"""
        # Mock JWT decorator
        def mock_decorator(f):
            def wrapper(*args, **kwargs):
                from flask import g
                g.user_email = "test@example.com"
                return f(*args, **kwargs)
            return wrapper
        mock_jwt_required.side_effect = mock_decorator
          mock_profile = UserProfileSchema(
            height=180, weight=75,
            fitness_goal="weight_loss"
        )
        mock_get_profile.return_value = mock_profile
        
        response = client.get("/profile", headers=valid_jwt_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["height"] == 180
        assert data["fitness_goal"] == "weight_loss"

    @patch("src.fit.blueprints.user_blueprint.get_user_profile")
    @patch("src.fit.blueprints.user_blueprint.jwt_required")
    def test_get_profile_not_found(self, mock_jwt_required, mock_get_profile, client, valid_jwt_headers):
        """Test profile retrieval for non-existent user"""
        # Mock JWT decorator
        def mock_decorator(f):
            def wrapper(*args, **kwargs):
                from flask import g
                g.user_email = "nonexistent@example.com"
                return f(*args, **kwargs)
            return wrapper
        mock_jwt_required.side_effect = mock_decorator
        
        mock_get_profile.return_value = None
        
        response = client.get("/profile", headers=valid_jwt_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data["error"].lower()

    @patch("src.fit.blueprints.user_blueprint.update_user_profile")
    @patch("src.fit.blueprints.user_blueprint.jwt_required")
    def test_onboard_user_success(self, mock_jwt_required, mock_update_profile, client, valid_jwt_headers):
        """Test successful user onboarding"""
        # Mock JWT decorator
        def mock_decorator(f):
            def wrapper(*args, **kwargs):
                from flask import g
                g.user_email = "test@example.com"
                return f(*args, **kwargs)
            return wrapper
        mock_jwt_required.side_effect = mock_decorator
        
        mock_profile = UserProfileSchema(
            age=25, gender="male", height=180, weight=75,
            fitness_level="intermediate", goals="weight_loss"
        )
        mock_update_profile.return_value = mock_profile
        
        payload = {
            "age": 25,
            "gender": "male",
            "height": 180,
            "weight": 75,
            "fitness_level": "intermediate",
            "goals": "weight_loss"
        }
        
        response = client.post("/profile/onboarding", json=payload, headers=valid_jwt_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["age"] == 25
        assert data["fitness_level"] == "intermediate"

    @patch("src.fit.blueprints.user_blueprint.rabbitmq_service")
    @patch("src.fit.blueprints.user_blueprint.get_all_users_service")
    @patch("src.fit.blueprints.user_blueprint.get_most_recent_workout_exercises")
    @patch("src.fit.blueprints.user_blueprint.admin_required", lambda f: f)
    def test_generate_wods_success(self, mock_get_workouts, mock_get_users, 
                                 mock_rabbitmq, client, admin_jwt_headers):
        """Test successful WOD generation"""
        # Mock users
        mock_users = [
            UserSchema(email="user1@example.com", name="User 1", role="user"),
            UserSchema(email="user2@example.com", name="User 2", role="user")
        ]
        mock_get_users.return_value = mock_users
        
        # Mock no unperformed workouts for both users
        mock_get_workouts.return_value = None
        
        # Mock RabbitMQ service
        mock_rabbitmq.publish_message.return_value = True
        
        response = client.post("/users/generateWods", headers=admin_jwt_headers)
        
        assert response.status_code == 202
        data = response.get_json()
        assert "Queued WOD generation for 2 users" in data["message"]
        assert data["total_users"] == 2
        assert data["users_needing_workout"] == 2
        
        # Verify RabbitMQ was called for each user
        assert mock_rabbitmq.publish_message.call_count == 2


class TestAuthBlueprint:
    """Test auth blueprint endpoints"""
    
    @patch("src.fit.blueprints.auth_blueprint.authenticate_user")
    @patch("src.fit.blueprints.auth_blueprint.create_access_token")
    def test_login_success(self, mock_create_token, mock_authenticate, client):
        """Test successful login"""
        mock_user = UserSchema(email="test@example.com", name="Test User", role="user")
        mock_authenticate.return_value = mock_user
        mock_create_token.return_value = "jwt-token-123"
        
        payload = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/oauth/token", json=payload)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["access_token"] == "jwt-token-123"
        assert data["token_type"] == "Bearer"
        assert data["user"]["email"] == "test@example.com"

    @patch("src.fit.blueprints.auth_blueprint.authenticate_user")
    def test_login_invalid_credentials(self, mock_authenticate, client):
        """Test login with invalid credentials"""
        mock_authenticate.return_value = None
        
        payload = {
            "email": "test@example.com",
            "password": "wrong-password"
        }
        
        response = client.post("/oauth/token", json=payload)
        
        assert response.status_code == 401
        data = response.get_json()
        assert "Invalid credentials" in data["error"]

    def test_login_validation_error(self, client):
        """Test login with validation error"""
        payload = {
            "email": "invalid-email",
            "password": ""
        }
        
        response = client.post("/oauth/token", json=payload)
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    @patch("src.fit.blueprints.auth_blueprint.authenticate_user")
    def test_login_service_error(self, mock_authenticate, client):
        """Test login with service error"""
        mock_authenticate.side_effect = Exception("Database error")
        
        payload = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/oauth/token", json=payload)
        
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data


class TestWorkoutBlueprint:
    """Test workout blueprint endpoints"""
    
    @patch("src.fit.blueprints.workout_blueprint.register_workout")
    @patch("src.fit.blueprints.workout_blueprint.api_key_required", lambda f: f)
    def test_create_workout_success(self, mock_register, client, valid_api_key_headers):
        """Test successful workout creation"""
        payload = {
            "email": "test@example.com",
            "exercises": [{"exercise_id": 1}, {"exercise_id": 2}]
        }
        
        response = client.post("/workouts", json=payload, headers=valid_api_key_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert "successfully" in data["message"].lower()
        
        mock_register.assert_called_once()

    @patch("src.fit.blueprints.workout_blueprint.api_key_required", lambda f: f)
    def test_create_workout_validation_error(self, client, valid_api_key_headers):
        """Test workout creation with validation error"""
        payload = {
            "email": "invalid-email",
            "exercises": []
        }
        
        response = client.post("/workouts", json=payload, headers=valid_api_key_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    @patch("src.fit.blueprints.workout_blueprint.register_workout")
    @patch("src.fit.blueprints.workout_blueprint.api_key_required", lambda f: f)
    def test_create_workout_service_error(self, mock_register, client, valid_api_key_headers):
        """Test workout creation with service error"""
        mock_register.side_effect = Exception("Database error")
        
        payload = {
            "email": "test@example.com",
            "exercises": [{"exercise_id": 1}]
        }
        
        response = client.post("/workouts", json=payload, headers=valid_api_key_headers)
        
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data

    @patch("src.fit.blueprints.workout_blueprint.perform_workout")
    @patch("src.fit.blueprints.workout_blueprint.jwt_required")
    def test_perform_workout_success(self, mock_jwt_required, mock_perform, client, valid_jwt_headers):
        """Test successful workout performance"""
        # Mock JWT decorator
        def mock_decorator(f):
            def wrapper(*args, **kwargs):
                from flask import g
                g.user_email = "test@example.com"
                return f(*args, **kwargs)
            return wrapper
        mock_jwt_required.side_effect = mock_decorator
        
        response = client.post("/workouts/1/perform", headers=valid_jwt_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert "performed" in data["message"].lower()
        
        mock_perform.assert_called_once_with(1, "test@example.com")

    @patch("src.fit.blueprints.workout_blueprint.perform_workout")
    @patch("src.fit.blueprints.workout_blueprint.jwt_required")
    def test_perform_workout_error(self, mock_jwt_required, mock_perform, client, valid_jwt_headers):
        """Test workout performance with error"""
        # Mock JWT decorator
        def mock_decorator(f):
            def wrapper(*args, **kwargs):
                from flask import g
                g.user_email = "test@example.com"
                return f(*args, **kwargs)
            return wrapper
        mock_jwt_required.side_effect = mock_decorator
        
        mock_perform.side_effect = ValueError("Workout not found")
        
        response = client.post("/workouts/999/perform", headers=valid_jwt_headers)
        
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data

    @patch("src.fit.blueprints.workout_blueprint.get_user_next_workout")
    @patch("src.fit.blueprints.workout_blueprint.jwt_required")
    def test_get_next_workout_success(self, mock_jwt_required, mock_get_next, client, valid_jwt_headers):
        """Test successful next workout retrieval"""
        # Mock JWT decorator
        def mock_decorator(f):
            def wrapper(*args, **kwargs):
                from flask import g
                g.user_email = "test@example.com"
                return f(*args, **kwargs)
            return wrapper
        mock_jwt_required.side_effect = mock_decorator
        
        mock_workout = WorkoutResponseSchema(
            id=1,
            user_email="test@example.com",
            created_at=datetime.now(),
            performed_at=None,
            performed=False,
            exercises=[
                ExerciseResponseSchema(
                    id=1, name="Push-up", description="desc",
                    difficulty=3, equipment="None", instructions="Do it"
                )
            ]
        )
        mock_get_next.return_value = mock_workout
        
        response = client.get("/workouts", headers=valid_jwt_headers)
        
        assert response.status_code == 200
        # Response should be JSON string from model_dump_json()
        assert response.content_type == "application/json"

    @patch("src.fit.blueprints.workout_blueprint.get_user_next_workout")
    @patch("src.fit.blueprints.workout_blueprint.jwt_required")
    def test_get_next_workout_none(self, mock_jwt_required, mock_get_next, client, valid_jwt_headers):
        """Test next workout retrieval when none available"""
        # Mock JWT decorator
        def mock_decorator(f):
            def wrapper(*args, **kwargs):
                from flask import g
                g.user_email = "test@example.com"
                return f(*args, **kwargs)
            return wrapper
        mock_jwt_required.side_effect = mock_decorator
        
        mock_get_next.return_value = None
        
        response = client.get("/workouts", headers=valid_jwt_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data == {}

    @patch("src.fit.blueprints.workout_blueprint.get_most_recent_workout_exercises")
    @patch("src.fit.blueprints.workout_blueprint.api_key_required", lambda f: f)
    def test_get_last_workout_success(self, mock_get_last, client, valid_api_key_headers):
        """Test successful last workout retrieval"""
        mock_exercises = [
            ExerciseResponseSchema(
                id=1, name="Push-up", description="desc",
                difficulty=3, equipment="None", instructions="Do it"
            )
        ]
        mock_workout = WorkoutResponseSchema(
            id=1,
            user_email="test@example.com",
            created_at=datetime.now(),
            performed_at=datetime.now(),
            performed=True,
            exercises=mock_exercises
        )
        mock_get_last.return_value = mock_workout
        
        payload = {"email": "test@example.com"}
        
        response = client.post("/workouts/last", json=payload, headers=valid_api_key_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1  # exercises list
        
        mock_get_last.assert_called_once_with("test@example.com", performed=True)

    @patch("src.fit.blueprints.workout_blueprint.get_most_recent_workout_exercises")
    @patch("src.fit.blueprints.workout_blueprint.api_key_required", lambda f: f)
    def test_get_last_workout_none(self, mock_get_last, client, valid_api_key_headers):
        """Test last workout retrieval when none found"""
        mock_get_last.return_value = None
        
        payload = {"email": "test@example.com"}
        
        response = client.post("/workouts/last", json=payload, headers=valid_api_key_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data == []

    @patch("src.fit.blueprints.workout_blueprint.api_key_required", lambda f: f)
    def test_get_last_workout_missing_email(self, client, valid_api_key_headers):
        """Test last workout retrieval with missing email"""
        payload = {}
        
        response = client.post("/workouts/last", json=payload, headers=valid_api_key_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert "required" in data["error"].lower()


class TestErrorHandling:
    """Test error handling across all blueprints"""
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post("/users", data="invalid-json", content_type="application/json")
        
        assert response.status_code == 400

    def test_missing_content_type(self, client):
        """Test handling of missing content type"""
        response = client.post("/users", data='{"test": "data"}')
        
        # Should handle gracefully
        assert response.status_code in [400, 415]

    def test_large_payload(self, client):
        """Test handling of very large payloads"""
        large_payload = {"data": "x" * 10000}
        
        response = client.post("/users", json=large_payload)
        
        # Should handle gracefully
        assert response.status_code in [400, 413, 500]
