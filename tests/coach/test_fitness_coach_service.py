"""
Unit tests for coach.fitness_coach_service
"""
import pytest
from unittest.mock import patch, MagicMock
import requests
from src.coach import fitness_coach_service


class TestCalculateIntensity:
    """Test calculate_intensity function"""
    
    def test_calculate_intensity_min_difficulty(self):
        """Test intensity calculation for minimum difficulty"""
        assert fitness_coach_service.calculate_intensity(1) == 0.0

    def test_calculate_intensity_max_difficulty(self):
        """Test intensity calculation for maximum difficulty"""
        assert fitness_coach_service.calculate_intensity(5) == 1.0

    def test_calculate_intensity_mid_difficulty(self):
        """Test intensity calculation for middle difficulty"""
        assert fitness_coach_service.calculate_intensity(3) == 0.5

    def test_calculate_intensity_other_values(self):
        """Test intensity calculation for other difficulty values"""
        assert fitness_coach_service.calculate_intensity(2) == 0.25
        assert fitness_coach_service.calculate_intensity(4) == 0.75


class TestHeavyComputation:
    """Test heavy_computation function"""
    
    def test_heavy_computation_runs_without_error(self):
        """Test heavy computation runs without raising errors"""
        # Should not raise and should run for at least a short time
        fitness_coach_service.heavy_computation(0)

    def test_heavy_computation_short_duration(self):
        """Test heavy computation with very short duration"""
        import time
        start = time.time()
        fitness_coach_service.heavy_computation(1)  # Use integer for 1 second
        duration = time.time() - start
        # Should run for approximately the requested duration
        assert duration >= 0.5  # Allow some tolerance for 1 second duration


class TestGetLastWorkoutExercises:
    """Test get_last_workout_exercises function"""
    
    @patch("src.coach.fitness_coach_service.requests.get")
    def test_get_last_workout_exercises_success(self, mock_get):
        """Test successful retrieval of last workout exercises"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [1, 2, 3]
        mock_get.return_value = mock_response
        
        result = fitness_coach_service.get_last_workout_exercises("test@example.com")
        
        assert result == [1, 2, 3]
        mock_get.assert_called_once()

    @patch("src.coach.fitness_coach_service.requests.get")
    def test_get_last_workout_exercises_empty_response(self, mock_get):
        """Test retrieval when no exercises found"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        result = fitness_coach_service.get_last_workout_exercises("test@example.com")
        
        assert result == []

    @patch("src.coach.fitness_coach_service.requests.get")
    def test_get_last_workout_exercises_api_error(self, mock_get):
        """Test handling of API errors"""
        mock_get.side_effect = requests.RequestException("API error")
        
        result = fitness_coach_service.get_last_workout_exercises("test@example.com")
        
        assert result == []

    @patch("src.coach.fitness_coach_service.requests.get")
    def test_get_last_workout_exercises_404(self, mock_get):
        """Test handling of 404 responses"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = fitness_coach_service.get_last_workout_exercises("test@example.com")
        
        assert result == []

    @patch("src.coach.fitness_coach_service.requests.get")
    def test_get_last_workout_exercises_invalid_json(self, mock_get):
        """Test handling of invalid JSON responses"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        result = fitness_coach_service.get_last_workout_exercises("test@example.com")
        
        assert result == []


class TestSaveWorkoutExercises:
    """Test save_workout_exercises function"""
    
    @patch("src.coach.fitness_coach_service.requests.post")
    def test_save_workout_exercises_success(self, mock_post):
        """Test successful saving of workout exercises"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Should not raise any exceptions
        fitness_coach_service.save_workout_exercises("test@example.com", [1, 2, 3])
        
        mock_post.assert_called_once()

    @patch("src.coach.fitness_coach_service.requests.post")
    def test_save_workout_exercises_api_error(self, mock_post):
        """Test handling of API errors during save"""
        mock_post.side_effect = requests.RequestException("API error")
        
        # Should not raise any exceptions
        fitness_coach_service.save_workout_exercises("test@example.com", [1, 2, 3])


class TestIsUserPremium:
    """Test is_user_premium function"""
    
    @patch("src.coach.fitness_coach_service.requests.get")
    def test_is_user_premium_true(self, mock_get):
        """Test premium user detection"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"is_active": True}
        mock_get.return_value = mock_response
        
        result = fitness_coach_service.is_user_premium("test@example.com")
        
        assert result is True

    @patch("src.coach.fitness_coach_service.requests.get")
    def test_is_user_premium_false(self, mock_get):
        """Test non-premium user detection"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"is_active": False}
        mock_get.return_value = mock_response
        
        result = fitness_coach_service.is_user_premium("test@example.com")
        
        assert result is False

    @patch("src.coach.fitness_coach_service.requests.get")
    def test_is_user_premium_api_error(self, mock_get):
        """Test handling of API errors"""
        mock_get.side_effect = requests.RequestException("API error")
        
        result = fitness_coach_service.is_user_premium("test@example.com")
        
        assert result is False

    @patch("src.coach.fitness_coach_service.requests.get")
    def test_is_user_premium_404(self, mock_get):
        """Test handling of user not found"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = fitness_coach_service.is_user_premium("test@example.com")
        
        assert result is False


class TestCancelUserSubscription:
    """Test cancel_user_subscription function"""
    
    @patch("src.coach.fitness_coach_service.requests.post")
    def test_cancel_user_subscription_success(self, mock_post):
        """Test successful subscription cancellation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = fitness_coach_service.cancel_user_subscription("test@example.com")
        
        assert result is True
        mock_post.assert_called_once()

    @patch("src.coach.fitness_coach_service.requests.post")
    def test_cancel_user_subscription_failure(self, mock_post):
        """Test subscription cancellation failure"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        result = fitness_coach_service.cancel_user_subscription("test@example.com")
        
        assert result is False

    @patch("src.coach.fitness_coach_service.requests.post")
    def test_cancel_user_subscription_api_error(self, mock_post):
        """Test handling of API errors during cancellation"""
        mock_post.side_effect = requests.RequestException("API error")
        
        result = fitness_coach_service.cancel_user_subscription("test@example.com")
        
        assert result is False


class TestCreateWodForUser:
    """Test create_wod_for_user function"""
    
    @patch("src.coach.fitness_coach_service.heavy_computation")
    @patch("src.coach.fitness_coach_service.is_user_premium")
    @patch("src.coach.fitness_coach_service.get_last_workout_exercises")
    @patch("src.coach.fitness_coach_service.save_workout_exercises")
    @patch("src.coach.fitness_coach_service.db_session")
    def test_create_wod_for_user_premium(self, mock_db_session, mock_save_workout, 
                                       mock_get_last_workout, mock_is_premium, 
                                       mock_heavy_computation):
        """Test WOD creation for premium user"""
        # Setup mocks
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        mock_is_premium.return_value = True
        mock_get_last_workout.return_value = [1, 2]
        
        # Mock exercises query
        mock_exercise1 = MagicMock()
        mock_exercise1.id = 3
        mock_exercise1.name = "Exercise 3"
        mock_exercise1.difficulty = 3
        
        mock_exercise2 = MagicMock()
        mock_exercise2.id = 4
        mock_exercise2.name = "Exercise 4"
        mock_exercise2.difficulty = 4
        
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = [
            mock_exercise1, mock_exercise2
        ]
        
        # Mock muscle groups
        mock_muscle_group = MagicMock()
        mock_muscle_group.id = 1
        mock_muscle_group.name = "Chest"
        mock_muscle_group.body_part = "Upper Body"
        
        mock_exercise1.muscle_groups = [mock_muscle_group]
        mock_exercise2.muscle_groups = [mock_muscle_group]
        
        result = fitness_coach_service.create_wod_for_user("test@example.com")
        
        assert len(result) == 2
        mock_heavy_computation.assert_called()
        mock_save_workout.assert_called()
        mock_db.close.assert_called()

    @patch("src.coach.fitness_coach_service.heavy_computation")
    @patch("src.coach.fitness_coach_service.is_user_premium")
    @patch("src.coach.fitness_coach_service.get_last_workout_exercises")
    @patch("src.coach.fitness_coach_service.save_workout_exercises")
    @patch("src.coach.fitness_coach_service.db_session")
    def test_create_wod_for_user_free(self, mock_db_session, mock_save_workout,
                                    mock_get_last_workout, mock_is_premium,
                                    mock_heavy_computation):
        """Test WOD creation for free user"""
        # Setup mocks
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        mock_is_premium.return_value = False
        mock_get_last_workout.return_value = [1]
        
        # Mock exercises query - only one exercise for free users
        mock_exercise = MagicMock()
        mock_exercise.id = 2
        mock_exercise.name = "Exercise 2"
        mock_exercise.difficulty = 2
        mock_exercise.muscle_groups = []
        
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = [
            mock_exercise
        ]
        
        result = fitness_coach_service.create_wod_for_user("test@example.com")
        
        assert len(result) == 1
        # Free users should not get heavy computation
        mock_heavy_computation.assert_not_called()
        mock_save_workout.assert_called()

    @patch("src.coach.fitness_coach_service.is_user_premium")
    @patch("src.coach.fitness_coach_service.get_last_workout_exercises")
    @patch("src.coach.fitness_coach_service.db_session")
    def test_create_wod_for_user_no_exercises(self, mock_db_session, mock_get_last_workout, 
                                            mock_is_premium):
        """Test WOD creation when no exercises available"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        mock_is_premium.return_value = True
        mock_get_last_workout.return_value = []
        
        # No exercises available
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        
        result = fitness_coach_service.create_wod_for_user("test@example.com")
        
        assert result == []
        mock_db.close.assert_called()

    @patch("src.coach.fitness_coach_service.is_user_premium")
    @patch("src.coach.fitness_coach_service.get_last_workout_exercises")
    @patch("src.coach.fitness_coach_service.db_session")
    def test_create_wod_for_user_database_error(self, mock_db_session, mock_get_last_workout,
                                              mock_is_premium):
        """Test WOD creation with database error"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        mock_is_premium.return_value = True
        mock_get_last_workout.return_value = []
        
        # Database error
        mock_db.query.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            fitness_coach_service.create_wod_for_user("test@example.com")
        
        mock_db.close.assert_called()


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_calculate_intensity_boundary_values(self):
        """Test intensity calculation with boundary values"""
        # Test values outside normal range
        assert fitness_coach_service.calculate_intensity(0) == -0.25
        assert fitness_coach_service.calculate_intensity(6) == 1.25

    @patch("src.coach.fitness_coach_service.requests.get")
    def test_get_last_workout_exercises_timeout(self, mock_get):
        """Test handling of request timeout"""
        mock_get.side_effect = requests.Timeout("Request timeout")
        
        result = fitness_coach_service.get_last_workout_exercises("test@example.com")
        
        assert result == []

    @patch("src.coach.fitness_coach_service.requests.get")
    def test_is_user_premium_malformed_response(self, mock_get):
        """Test handling of malformed API response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unexpected_field": "value"}
        mock_get.return_value = mock_response
        
        result = fitness_coach_service.is_user_premium("test@example.com")
        
        assert result is False

    def test_heavy_computation_zero_duration(self):
        """Test heavy computation with zero duration"""
        # Should complete immediately without error
        fitness_coach_service.heavy_computation(0)
