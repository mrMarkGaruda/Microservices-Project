"""
Comprehensive tests for coach Flask app endpoints and integration.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.coach.app import app
from src.coach.models_dto import Exercise, MuscleGroupWithPrimary, WodExerciseSchema, WodResponseSchema


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health(self, client):
        """Test health endpoint returns correct status"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json["status"] == "UP"


class TestExercisesEndpoints:
    """Test exercise-related endpoints"""
    
    @patch("src.coach.app.get_all_exercises")
    def test_get_exercises_success(self, mock_get_all_exercises, client):
        """Test successful retrieval of all exercises"""
        mock_exercises = [
            Exercise(
                id=1,
                name="Push-up",
                description="Basic push-up",
                difficulty=3,
                equipment="None",
                instructions="Push up from the ground",
                muscle_groups=[]
            ),
            Exercise(
                id=2,
                name="Squat",
                description="Basic squat",
                difficulty=4,
                equipment="None",
                instructions="Squat down and up",
                muscle_groups=[]
            )
        ]
        mock_get_all_exercises.return_value = mock_exercises
        
        response = client.get("/exercises")
        assert response.status_code == 200
        data = response.json
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["name"] == "Push-up"
        assert data[1]["name"] == "Squat"
        
        mock_get_all_exercises.assert_called_once()

    @patch("src.coach.app.get_exercises_by_muscle_group")
    def test_get_exercises_by_muscle_group_success(self, mock_get_exercises_by_muscle_group, client):
        """Test successful retrieval of exercises by muscle group"""
        mock_exercises = [
            Exercise(
                id=1,
                name="Push-up",
                description="Basic push-up",
                difficulty=3,
                equipment="None",
                instructions="Push up from the ground",
                muscle_groups=[]
            )
        ]
        mock_get_exercises_by_muscle_group.return_value = mock_exercises
        
        response = client.get("/exercises?muscle_group_id=1")
        assert response.status_code == 200
        data = response.json
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == "Push-up"
        
        mock_get_exercises_by_muscle_group.assert_called_once_with(1)

    @patch("src.coach.app.get_all_exercises")
    def test_get_exercises_error(self, mock_get_all_exercises, client):
        """Test handling of error during exercise retrieval"""
        mock_get_all_exercises.side_effect = Exception("Database error")
        
        response = client.get("/exercises")
        assert response.status_code == 500
        data = response.json
        assert "error" in data
        assert "Error retrieving exercises" in data["error"]
        assert "details" in data

    @patch("src.coach.app.get_exercise_by_id")
    def test_get_exercise_by_id_success(self, mock_get_exercise_by_id, client):
        """Test successful retrieval of specific exercise"""
        mock_exercise = Exercise(
            id=1,
            name="Push-up",
            description="Basic push-up",
            difficulty=3,
            equipment="None",
            instructions="Push up from the ground",
            muscle_groups=[]
        )
        mock_get_exercise_by_id.return_value = mock_exercise
        
        response = client.get("/exercises/1")
        assert response.status_code == 200
        data = response.json
        assert data["id"] == 1
        assert data["name"] == "Push-up"
        assert data["difficulty"] == 3
        
        mock_get_exercise_by_id.assert_called_once_with(1)

    @patch("src.coach.app.get_exercise_by_id")
    def test_get_exercise_by_id_not_found(self, mock_get_exercise_by_id, client):
        """Test retrieval of non-existent exercise"""
        mock_get_exercise_by_id.return_value = None
        
        response = client.get("/exercises/999")
        assert response.status_code == 404
        data = response.json
        assert "Exercise not found" in data["error"]
        
        mock_get_exercise_by_id.assert_called_once_with(999)

    @patch("src.coach.app.get_exercise_by_id")
    def test_get_exercise_by_id_error(self, mock_get_exercise_by_id, client):
        """Test handling of error during specific exercise retrieval"""
        mock_get_exercise_by_id.side_effect = Exception("Database error")
        
        response = client.get("/exercises/1")
        assert response.status_code == 500
        data = response.json
        assert "error" in data
        assert "Error retrieving exercise" in data["error"]


class TestCreateWodEndpoint:
    """Test workout of the day creation endpoint"""
    
    @patch("src.coach.app.create_wod_for_user")
    @patch("src.coach.app.calculate_intensity")
    def test_create_wod_success(self, mock_calculate_intensity, mock_create_wod_for_user, client):
        """Test successful WOD creation"""
        # Mock exercise with muscle groups
        mock_exercise = Exercise(
            id=1,
            name="Push-up",
            description="Basic push-up",
            difficulty=3,
            equipment="None",
            instructions="Push up from the ground",
            muscle_groups=[]
        )
        
        mock_muscle_group = MagicMock()
        mock_muscle_group.id = 1
        mock_muscle_group.name = "Chest"
        mock_muscle_group.body_part = "Upper Body"
        
        mock_create_wod_for_user.return_value = [
            (mock_exercise, [(mock_muscle_group, True)])
        ]
        mock_calculate_intensity.return_value = 0.6
        
        payload = {"user_email": "test@example.com"}
        response = client.post("/createWod", json=payload)
        
        assert response.status_code == 200
        data = response.json
        assert "exercises" in data
        assert "generated_at" in data
        assert len(data["exercises"]) == 1
        assert data["exercises"][0]["name"] == "Push-up"
        
        mock_create_wod_for_user.assert_called_once_with("test@example.com")

    def test_create_wod_missing_email(self, client):
        """Test WOD creation with missing user email"""
        payload = {}
        response = client.post("/createWod", json=payload)
        
        assert response.status_code == 400
        data = response.json
        assert "user_email is required" in data["error"]

    def test_create_wod_empty_email(self, client):
        """Test WOD creation with empty user email"""
        payload = {"user_email": ""}
        response = client.post("/createWod", json=payload)
        
        assert response.status_code == 400
        data = response.json
        assert "user_email is required" in data["error"]

    @patch("src.coach.app.create_wod_for_user")
    def test_create_wod_service_error(self, mock_create_wod_for_user, client):
        """Test WOD creation with service error"""
        import requests
        mock_create_wod_for_user.side_effect = requests.RequestException("API error")
        
        payload = {"user_email": "test@example.com"}
        response = client.post("/createWod", json=payload)
        
        assert response.status_code == 500
        data = response.json
        assert "Failed to fetch user history" in data["error"]

    @patch("src.coach.app.create_wod_for_user")
    def test_create_wod_multiple_exercises(self, mock_create_wod_for_user, client):
        """Test WOD creation with multiple exercises"""
        mock_exercises = []
        mock_muscle_groups = []
        
        for i in range(3):
            exercise = Exercise(
                id=i+1,
                name=f"Exercise {i+1}",
                description=f"Description {i+1}",
                difficulty=3,
                equipment="None",
                instructions=f"Instructions {i+1}",
                muscle_groups=[]
            )
            muscle_group = MagicMock()
            muscle_group.id = i+1
            muscle_group.name = f"Muscle {i+1}"
            muscle_group.body_part = "Upper Body"
            
            mock_exercises.append((exercise, [(muscle_group, True)]))
        
        mock_create_wod_for_user.return_value = mock_exercises
        
        with patch("src.coach.app.calculate_intensity", return_value=0.6):
            payload = {"user_email": "test@example.com"}
            response = client.post("/createWod", json=payload)
        
        assert response.status_code == 200
        data = response.json
        assert len(data["exercises"]) == 3
        for i, exercise in enumerate(data["exercises"]):
            assert exercise["name"] == f"Exercise {i+1}"

    def test_create_wod_invalid_json(self, client):
        """Test WOD creation with invalid JSON"""
        response = client.post("/createWod", data="invalid json", content_type="application/json")
        
        assert response.status_code == 400


class TestCancelSubscriptionEndpoint:
    """Test subscription cancellation endpoint"""
    
    @patch("src.coach.app.cancel_user_subscription")
    def test_cancel_subscription_success(self, mock_cancel_subscription, client):
        """Test successful subscription cancellation"""
        mock_cancel_subscription.return_value = True
        
        payload = {"user_email": "test@example.com"}
        response = client.post("/subscription/cancel", json=payload)
        
        assert response.status_code == 200
        data = response.json
        assert "Subscription cancelled" in data["message"]
        
        mock_cancel_subscription.assert_called_once_with("test@example.com")

    @patch("src.coach.app.cancel_user_subscription")
    def test_cancel_subscription_failure(self, mock_cancel_subscription, client):
        """Test failed subscription cancellation"""
        mock_cancel_subscription.return_value = False
        
        payload = {"user_email": "test@example.com"}
        response = client.post("/subscription/cancel", json=payload)
        
        assert response.status_code == 400
        data = response.json
        assert "Failed to cancel subscription" in data["error"]

    def test_cancel_subscription_missing_email(self, client):
        """Test subscription cancellation with missing email"""
        payload = {}
        response = client.post("/subscription/cancel", json=payload)
        
        assert response.status_code == 400
        data = response.json
        assert "user_email is required" in data["error"]

    def test_cancel_subscription_empty_email(self, client):
        """Test subscription cancellation with empty email"""
        payload = {"user_email": ""}
        response = client.post("/subscription/cancel", json=payload)
        
        assert response.status_code == 400
        data = response.json
        assert "user_email is required" in data["error"]

    def test_cancel_subscription_invalid_json(self, client):
        """Test subscription cancellation with invalid JSON"""
        response = client.post("/subscription/cancel", data="invalid json", content_type="application/json")
        
        assert response.status_code == 400


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_invalid_endpoint(self, client):
        """Test request to invalid endpoint"""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404

    def test_wrong_http_method(self, client):
        """Test using wrong HTTP method"""
        response = client.post("/health")
        assert response.status_code == 405

    def test_invalid_exercise_id_type(self, client):
        """Test using invalid exercise ID type"""
        response = client.get("/exercises/invalid")
        assert response.status_code == 404  # Flask converts this to 404


class TestAppConfiguration:
    """Test app configuration and setup"""
    
    def test_app_debug_mode(self):
        """Test app debug mode configuration"""
        assert app.logger.level is not None

    @patch("src.coach.app.init_db")
    @patch("src.coach.app.init_fitness_data")
    def test_app_initialization(self, mock_init_fitness_data, mock_init_db):
        """Test app initialization functions"""
        # These would be called when running the app
        # We can't test them directly here as they're only called in run_app()
        pass
