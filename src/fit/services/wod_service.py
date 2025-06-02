import os
import requests
import logging
from typing import List, Tuple
from ..services.fitness_coach_service import request_wod as legacy_request_wod, get_recent_exercises
from ..models_db import ExerciseModel, MuscleGroupModel
from ..database import db_session

logger = logging.getLogger(__name__)

class WODService:
    def __init__(self):
        self.coach_service_url = os.getenv('COACH_SERVICE_URL', 'http://localhost:5001')
        self.use_microservice = os.getenv('USE_COACH_MICROSERVICE', 'false').lower() == 'true'
    
    def request_wod(self, user_email: str) -> List[Tuple[ExerciseModel, List[Tuple[MuscleGroupModel, bool]]]]:
        """
        Generate WOD using strangler fig pattern
        """
        if self.use_microservice:
            try:
                logger.info(f"Attempting to use coach microservice for user: {user_email}")
                return self._request_wod_microservice(user_email)
            except Exception as e:
                logger.warning(f"Coach microservice failed: {e}. Falling back to legacy.")
                return legacy_request_wod(user_email)
        else:
            logger.info("Using legacy WOD generation")
            return legacy_request_wod(user_email)
    
    def _request_wod_microservice(self, user_email: str) -> List[Tuple[ExerciseModel, List[Tuple[MuscleGroupModel, bool]]]]:
        """
        Call coach microservice for WOD generation
        """
        recent_exercise_ids = get_recent_exercises(user_email)
        excluded_exercises = self._get_exercise_names(recent_exercise_ids)
        
        payload = {
            "user_email": user_email,
            "excluded_exercises": excluded_exercises
        }
        
        response = requests.post(
            f"{self.coach_service_url}/generate-wod",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        coach_wod = response.json()
        logger.info(f"Coach microservice returned WOD with {len(coach_wod.get('exercises', []))} exercises")

        # For now, still use legacy to get proper database objects
        return legacy_request_wod(user_email)
    
    def _get_exercise_names(self, exercise_ids: List[int]) -> List[str]:
        """Get exercise names from IDs"""
        if not exercise_ids:
            return []
            
        db = db_session()
        try:
            exercises = db.query(ExerciseModel).filter(ExerciseModel.id.in_(exercise_ids)).all()
            return [ex.name for ex in exercises]
        finally:
            db.close()