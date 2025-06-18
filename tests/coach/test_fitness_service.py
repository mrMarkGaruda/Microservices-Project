"""
Unit tests for coach.fitness_service
"""
import pytest
from unittest.mock import patch, MagicMock
from src.coach import fitness_service
from src.coach.models_dto import MuscleGroup, Exercise, MuscleGroupWithPrimary


class TestGetAllMuscleGroups:
    """Test get_all_muscle_groups function"""
    
    @patch("src.coach.fitness_service.db_session")
    def test_get_all_muscle_groups_success(self, mock_db_session):
        """Test successful retrieval of all muscle groups"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        mock_mg1 = MagicMock()
        mock_mg1.id = 1
        mock_mg1.name = "Chest"
        mock_mg1.body_part = "Upper Body"
        mock_mg1.description = "Chest muscles"
        
        mock_mg2 = MagicMock()
        mock_mg2.id = 2
        mock_mg2.name = "Legs"
        mock_mg2.body_part = "Lower Body"
        mock_mg2.description = "Leg muscles"
        
        mock_db.query.return_value.all.return_value = [mock_mg1, mock_mg2]
        
        result = fitness_service.get_all_muscle_groups()
        
        assert len(result) == 2
        assert result[0].name == "Chest"
        assert result[1].name == "Legs"
        mock_db.close.assert_called()

    @patch("src.coach.fitness_service.db_session")
    def test_get_all_muscle_groups_empty(self, mock_db_session):
        """Test retrieval when no muscle groups exist"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.return_value.all.return_value = []
        
        result = fitness_service.get_all_muscle_groups()
        
        assert result == []
        mock_db.close.assert_called()

    @patch("src.coach.fitness_service.db_session")
    def test_get_all_muscle_groups_database_error(self, mock_db_session):
        """Test handling of database errors"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            fitness_service.get_all_muscle_groups()
        
        mock_db.close.assert_called()


class TestGetMuscleGroupById:
    """Test get_muscle_group_by_id function"""
    
    @patch("src.coach.fitness_service.db_session")
    def test_get_muscle_group_by_id_success(self, mock_db_session):
        """Test successful retrieval of muscle group by ID"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        mock_mg = MagicMock()
        mock_mg.id = 1
        mock_mg.name = "Chest"
        mock_mg.body_part = "Upper Body"
        mock_mg.description = "Chest muscles"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_mg
        
        result = fitness_service.get_muscle_group_by_id(1)
        
        assert result is not None
        assert result.name == "Chest"
        assert result.id == 1
        mock_db.close.assert_called()

    @patch("src.coach.fitness_service.db_session")
    def test_get_muscle_group_by_id_not_found(self, mock_db_session):
        """Test retrieval when muscle group not found"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = fitness_service.get_muscle_group_by_id(999)
        
        assert result is None
        mock_db.close.assert_called()


class TestGetAllExercises:
    """Test get_all_exercises function"""
    
    @patch("src.coach.fitness_service.db_session")
    def test_get_all_exercises_success(self, mock_db_session):
        """Test successful retrieval of all exercises"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        # Mock exercise
        mock_exercise = MagicMock()
        mock_exercise.id = 1
        mock_exercise.name = "Push-up"
        mock_exercise.description = "Basic push-up"
        mock_exercise.difficulty = 3
        mock_exercise.equipment = "None"
        mock_exercise.instructions = "Push up from ground"
        mock_exercise.muscle_groups = []
        
        mock_db.query.return_value.options.return_value.all.return_value = [mock_exercise]
        
        result = fitness_service.get_all_exercises()
        
        assert len(result) == 1
        assert result[0].name == "Push-up"
        mock_db.close.assert_called()


class TestGetExerciseById:
    """Test get_exercise_by_id function"""
    
    @patch("src.coach.fitness_service.db_session")
    def test_get_exercise_by_id_success(self, mock_db_session):
        """Test successful retrieval of exercise by ID"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        mock_exercise = MagicMock()
        mock_exercise.id = 1
        mock_exercise.name = "Push-up"
        mock_exercise.description = "Basic push-up"
        mock_exercise.difficulty = 3
        mock_exercise.equipment = "None"
        mock_exercise.instructions = "Push up from ground"
        mock_exercise.muscle_groups = []
        
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_exercise
        
        result = fitness_service.get_exercise_by_id(1)
        
        assert result is not None
        assert result.name == "Push-up"
        assert result.id == 1
        mock_db.close.assert_called()

    @patch("src.coach.fitness_service.db_session")
    def test_get_exercise_by_id_not_found(self, mock_db_session):
        """Test retrieval when exercise not found"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = None
        
        result = fitness_service.get_exercise_by_id(999)
        
        assert result is None
        mock_db.close.assert_called()


class TestGetExercisesByMuscleGroup:
    """Test get_exercises_by_muscle_group function"""
    
    @patch("src.coach.fitness_service.db_session")
    def test_get_exercises_by_muscle_group_success(self, mock_db_session):
        """Test successful retrieval of exercises by muscle group"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        mock_exercise = MagicMock()
        mock_exercise.id = 1
        mock_exercise.name = "Push-up"
        mock_exercise.muscle_groups = []
        
        mock_db.query.return_value.join.return_value.filter.return_value.options.return_value.all.return_value = [mock_exercise]
        
        result = fitness_service.get_exercises_by_muscle_group(1)
        
        assert len(result) == 1
        assert result[0].name == "Push-up"
        mock_db.close.assert_called()

    @patch("src.coach.fitness_service.db_session")
    def test_get_exercises_by_muscle_group_empty(self, mock_db_session):
        """Test retrieval when no exercises found for muscle group"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.return_value.join.return_value.filter.return_value.options.return_value.all.return_value = []
        
        result = fitness_service.get_exercises_by_muscle_group(999)
        
        assert result == []
        mock_db.close.assert_called()
