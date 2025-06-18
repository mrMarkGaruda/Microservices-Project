import datetime
import random
import os
import sys
import logging
import requests
from flask import Flask, request, jsonify
from pydantic import ValidationError

# Local application imports
from .models_dto import MuscleGroupImpact, WodExerciseSchema, WodResponseSchema
from .fitness_coach_service import calculate_intensity, create_wod_for_user, cancel_user_subscription
from .fitness_service import get_exercises_by_muscle_group, get_all_exercises, get_exercise_by_id
from .database import init_db
from .fitness_data_init import init_fitness_data

# Ensure unbuffered stdout for Docker logs
sys.stdout.reconfigure(line_buffering=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# Load FIT API key, default for tests/dev
FIT_API_KEY = os.getenv("FIT_API_KEY", "test-key")
if FIT_API_KEY == "test-key":
    logger.info("FIT_API_KEY not set—using default for tests/dev.")

# Add API key to config
app.config['FIT_API_KEY'] = FIT_API_KEY

# Initialize DB and data
init_db()
init_fitness_data()

# Health endpoint
@app.route("/health")
def health():
    return {"status": "UP"}

# Exercise endpoints
@app.route("/exercises", methods=["GET"])
def get_exercises():
    try:
        muscle_group_id = request.args.get("muscle_group_id")
        if muscle_group_id:
            exercises = get_exercises_by_muscle_group(int(muscle_group_id))
        else:
            exercises = get_all_exercises()
        return jsonify([ex.model_dump() for ex in exercises]), 200
    except Exception as e:
        logger.error(f"Error retrieving exercises: {e}", exc_info=True)
        return jsonify({"error": "Error retrieving exercises", "details": str(e)}), 500

@app.route("/exercises/<int:exercise_id>", methods=["GET"])
def get_exercise(exercise_id):
    try:
        exercise = get_exercise_by_id(exercise_id)
        if not exercise:
            return jsonify({"error": "Exercise not found"}), 404
        return jsonify(exercise.model_dump()), 200
    except Exception as e:
        logger.error(f"Error retrieving exercise: {e}", exc_info=True)
        return jsonify({"error": "Error retrieving exercise", "details": str(e)}), 500

# WOD generation endpoint
@app.route("/createWod", methods=["POST"])
def create_wod_for_user_endpoint():
    user_email = request.json.get("user_email")
    if not user_email:
        return jsonify({"error": "user_email is required"}), 400
    try:
        exercises_with_muscles = create_wod_for_user(user_email)
        wod_exercises = []
        for exercise, muscle_groups in exercises_with_muscles:
            muscle_impacts = [
                MuscleGroupImpact(
                    id=mg.id,
                    name=mg.name,
                    body_part=mg.body_part,
                    is_primary=is_primary,
                    intensity=calculate_intensity(exercise.difficulty)
                              * (1.2 if is_primary else 0.8)
                )
                for mg, is_primary in muscle_groups
            ]
            wod_exercise = WodExerciseSchema(
                id=exercise.id,
                name=exercise.name,
                description=exercise.description,
                difficulty=exercise.difficulty,
                muscle_groups=muscle_impacts,
                suggested_weight=random.uniform(5.0, 50.0),
                suggested_reps=random.randint(8, 15)
            )
            wod_exercises.append(wod_exercise)
        response = WodResponseSchema(
            exercises=wod_exercises,
            generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        return jsonify(response.model_dump()), 200
    except requests.RequestException as e:
        logger.error(f"Failed to fetch user history: {e}", exc_info=True)
        return jsonify({"error": f"Failed to fetch user history: {str(e)}"}), 500
    except ValidationError as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        return jsonify({"error": "Invalid data", "details": e.errors()}), 422

# Subscription cancellation endpoint
@app.route("/subscription/cancel", methods=["POST"])
def cancel_subscription():
    data = request.get_json()
    user_email = data.get("user_email")
    if not user_email:
        return jsonify({"error": "user_email is required"}), 400
    success = cancel_user_subscription(user_email)
    if success:
        return jsonify({"message": "Subscription cancelled"}), 200
    else:
        return jsonify({"error": "Failed to cancel subscription"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
