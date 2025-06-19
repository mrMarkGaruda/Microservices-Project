# Import Blueprint, g, request, and jsonify from Flask
from flask import Blueprint, g, request, jsonify
# Import ValidationError from pydantic for validation
from pydantic import ValidationError
# Import the RegisterWorkoutSchema from the parent models_dto module
from ..models_dto import  RegisterWorkoutSchema
# Import workout service functions for workout management
from ..services.workout_service import get_most_recent_workout_exercises, get_user_next_workout, perform_workout, register_workout
# Import authentication and API key decorators
from ..services.auth_service import  api_key_required, jwt_required

# Create a Flask Blueprint for workout routes
workout_bp = Blueprint('workout', __name__)
   

# Define a route to get the user's last performed workout
@workout_bp.route("/last", methods=["POST"])
@api_key_required
def get_user_last_performed_workout():
    try:
        # Get the email from the request JSON
        email = request.json.get("email")
        # If email is not provided, return an error
        if not email:
            return jsonify({"error": "email is required"}), 400
        
        # Get the most recent performed workout exercises for the user
        exercises = get_most_recent_workout_exercises(email, performed=True)
        # If no exercises are found, return an empty list
        if exercises is None:
            return jsonify([]), 200
            
        # Return the exercises as JSON
        return jsonify(exercises.exercises), 200
        
    except Exception as e:
        # Return an error if something goes wrong
        return jsonify({"error": "Error retrieving last workout", "details": str(e)}), 500 
    
# Define a route to create a new workout
@workout_bp.route("/", methods=["POST"])
@api_key_required
def create_workout():
    try:
        # Get the workout data from the request JSON
        workout_data = request.get_json()
        # Validate the workout data using the schema
        workout = RegisterWorkoutSchema.model_validate(workout_data)
        # Register the workout using the service
        register_workout(workout.email, workout.exercises)
        # Return a success message
        return jsonify({"message": "Workout registered successfully"}), 200
        
    except ValidationError as e:
        # Return validation errors if the data is invalid
        return jsonify({"error": "Invalid workout data", "details": e.errors()}), 400
    except Exception as e:
        # Return an error if something else goes wrong
        return jsonify({"error": "Error registering workout", "details": str(e)}), 500 
    
# Define a route to mark a workout as performed
@workout_bp.route("/<int:workout_id>/perform", methods=["POST"])
@jwt_required
def perform_workout_api(workout_id: int):
    try:
        # Get the user email from the JWT token
        user_email = g.user_email
        # Mark the workout as performed for the user
        perform_workout(workout_id, user_email)
        # Return a success message
        return jsonify({"message": "Workout marked as performed"}), 200
    except Exception as e:
        # Return an error if something goes wrong
        return jsonify({"error": "Error marking workout as performed", "details": str(e)}), 500 

# Define a route to get the next workout to perform
@workout_bp.route("/", methods=["GET"])
@jwt_required
def get_next_workout_to_perform():
    try:
        # Get the user email from the JWT token
        user_email = g.user_email
        # Get the next workout exercises for the user
        exercises = get_user_next_workout(user_email)
        # If no exercises are found, return an empty object
        if exercises is None:
            return jsonify({}), 200
        
        # Return the exercises as JSON
        return exercises.model_dump_json(), 200
        
    except Exception as e:
        # Return an error if something goes wrong
        return jsonify({"error": "Error retrieving unperformed workout", "details": str(e)}), 500