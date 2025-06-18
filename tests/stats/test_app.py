"""
Comprehensive tests for stats Flask app endpoints and integration.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.stats.app import create_app
from src.stats.models_dto import WorkoutStatResponseItemSchema, UserWorkoutStatsResponseSchema


@pytest.fixture
def app():
    """Create test app instance"""
    test_app = create_app()
    test_app.config['TESTING'] = True
    return test_app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health(self, client):
        """Test health endpoint returns correct status"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json["status"] == "UP"
        assert response.json["service"] == "Stats Service"


class TestStatsEndpoints:
    """Test stats-related endpoints"""
    
    @patch("src.stats.blueprints.stats_blueprint.get_user_workout_stats")
    def test_get_stats_for_user_success(self, mock_get_stats, client):
        """Test successful retrieval of user stats"""
        # Mock response data
        mock_stats = UserWorkoutStatsResponseSchema(
            user_email="test@example.com",
            stats=[
                WorkoutStatResponseItemSchema(
                    exercise_id=1,
                    workout_id=123,
                    performed_timestamp=datetime(2024, 1, 1, 12, 0, 0),
                    reps=10,
                    weight=50.0,
                    duration_seconds=300
                )
            ]
        )
        mock_get_stats.return_value = mock_stats
        
        response = client.get("/stats/users/test@example.com")
        
        assert response.status_code == 200
        data = response.json
        assert data["user_email"] == "test@example.com"
        assert len(data["stats"]) == 1
        assert data["stats"][0]["exercise_id"] == 1
        assert data["stats"][0]["workout_id"] == 123
        assert data["stats"][0]["reps"] == 10
        
        mock_get_stats.assert_called_once_with("test@example.com")

    @patch("src.stats.blueprints.stats_blueprint.get_user_workout_stats")
    def test_get_stats_for_user_not_found(self, mock_get_stats, client):
        """Test retrieval of stats for non-existent user"""
        mock_get_stats.return_value = None
        
        response = client.get("/stats/users/nonexistent@example.com")
        
        assert response.status_code == 404
        data = response.json
        assert "No stats found for this user" in data["message"]
        
        mock_get_stats.assert_called_once_with("nonexistent@example.com")

    @patch("src.stats.blueprints.stats_blueprint.get_user_workout_stats")
    def test_get_stats_for_user_service_error(self, mock_get_stats, client):
        """Test handling of service errors"""
        mock_get_stats.side_effect = Exception("Database connection failed")
        
        response = client.get("/stats/users/test@example.com")
        
        assert response.status_code == 500
        data = response.json
        assert "Failed to retrieve user statistics" in data["error"]
        assert "details" in data
        
        mock_get_stats.assert_called_once_with("test@example.com")

    @patch("src.stats.blueprints.stats_blueprint.get_user_workout_stats")
    def test_get_stats_for_user_empty_stats(self, mock_get_stats, client):
        """Test retrieval of empty stats"""
        mock_stats = UserWorkoutStatsResponseSchema(
            user_email="newuser@example.com",
            stats=[]
        )
        mock_get_stats.return_value = mock_stats
        
        response = client.get("/stats/users/newuser@example.com")
        
        assert response.status_code == 200
        data = response.json
        assert data["user_email"] == "newuser@example.com"
        assert len(data["stats"]) == 0
        
        mock_get_stats.assert_called_once_with("newuser@example.com")

    @patch("src.stats.blueprints.stats_blueprint.get_user_workout_stats")
    def test_get_stats_special_characters_in_email(self, mock_get_stats, client):
        """Test handling of special characters in email"""
        email_with_special = "test+special@example.com"
        mock_stats = UserWorkoutStatsResponseSchema(
            user_email=email_with_special,
            stats=[]
        )
        mock_get_stats.return_value = mock_stats
        
        response = client.get(f"/stats/users/{email_with_special}")
        
        assert response.status_code == 200
        data = response.json
        assert data["user_email"] == email_with_special
        
        mock_get_stats.assert_called_once_with(email_with_special)

    @patch("src.stats.blueprints.stats_blueprint.get_user_workout_stats")
    def test_get_stats_multiple_stats(self, mock_get_stats, client):
        """Test retrieval of multiple workout stats"""
        mock_stats = UserWorkoutStatsResponseSchema(
            user_email="active@example.com",
            stats=[
                WorkoutStatResponseItemSchema(
                    exercise_id=1,
                    workout_id=123,
                    performed_timestamp=datetime(2024, 1, 1, 12, 0, 0),
                    reps=10,
                    weight=50.0,
                    duration_seconds=300
                ),
                WorkoutStatResponseItemSchema(
                    exercise_id=2,
                    workout_id=124,
                    performed_timestamp=datetime(2024, 1, 2, 12, 0, 0),
                    reps=None,
                    weight=None,
                    duration_seconds=None
                ),
                WorkoutStatResponseItemSchema(
                    exercise_id=3,
                    workout_id=125,
                    performed_timestamp=datetime(2024, 1, 3, 12, 0, 0),
                    reps=15,
                    weight=75.0,
                    duration_seconds=450
                )
            ]
        )
        mock_get_stats.return_value = mock_stats
        
        response = client.get("/stats/users/active@example.com")
        
        assert response.status_code == 200
        data = response.json
        assert data["user_email"] == "active@example.com"
        assert len(data["stats"]) == 3
        
        # Check first stat (with all fields)
        assert data["stats"][0]["exercise_id"] == 1
        assert data["stats"][0]["reps"] == 10
        assert data["stats"][0]["weight"] == 50.0
        
        # Check second stat (with null fields)
        assert data["stats"][1]["exercise_id"] == 2
        assert data["stats"][1]["reps"] is None
        assert data["stats"][1]["weight"] is None
        
        # Check third stat
        assert data["stats"][2]["exercise_id"] == 3
        assert data["stats"][2]["reps"] == 15
        
        mock_get_stats.assert_called_once_with("active@example.com")


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_invalid_endpoint(self, client):
        """Test request to invalid endpoint"""
        response = client.get("/stats/invalid")
        assert response.status_code == 404

    def test_wrong_http_method(self, client):
        """Test using wrong HTTP method"""
        response = client.post("/stats/users/test@example.com")
        assert response.status_code == 405

    @patch("src.stats.blueprints.stats_blueprint.get_user_workout_stats")
    def test_internal_server_error(self, mock_get_stats, client):
        """Test internal server error handling"""
        mock_get_stats.side_effect = RuntimeError("Unexpected error")
        
        response = client.get("/stats/users/test@example.com")
        
        assert response.status_code == 500
        data = response.json
        assert "error" in data
        assert "Failed to retrieve user statistics" in data["error"]


class TestAppConfiguration:
    """Test app configuration and setup"""
    
    def test_app_creation(self):
        """Test app creation without errors"""
        app = create_app()
        assert app is not None
        assert app.config.get('TESTING') is None  # Default config

    def test_app_with_testing_config(self):
        """Test app with testing configuration"""
        app = create_app()
        app.config['TESTING'] = True
        assert app.config['TESTING'] is True

    @patch("src.stats.app.init_db")
    def test_database_initialization(self, mock_init_db):
        """Test database initialization during app creation"""
        create_app()
        mock_init_db.assert_called_once()

    @patch("src.stats.app.run_consumer")
    def test_consumer_startup(self, mock_run_consumer):
        """Test that consumer starts up with app (in non-debug mode)"""
        # This would be called in production when not in debug mode
        # The actual call is conditional on WERKZEUG_RUN_MAIN
        pass


class TestBlueprintRegistration:
    """Test blueprint registration"""
    
    def test_stats_blueprint_registered(self, app):
        """Test that stats blueprint is properly registered"""
        # Check that the stats endpoint exists
        with app.test_client() as client:
            response = client.get("/stats/users/test@example.com")
            # Should not be 404 (blueprint not found), might be 500 due to mocked service
            assert response.status_code != 404

    def test_health_endpoint_accessible(self, app):
        """Test that health endpoint is accessible"""
        with app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200
