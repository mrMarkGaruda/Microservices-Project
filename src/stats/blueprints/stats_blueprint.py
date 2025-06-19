# Import Blueprint, jsonify, and current_app from Flask
from flask import Blueprint, jsonify, current_app
# Import the function to get user workout stats from the stats service
from services.stats_service import get_user_workout_stats

# Create a Flask Blueprint for stats routes
stats_bp = Blueprint('stats', __name__, url_prefix='/stats')

# Define a route to get stats for a user
@stats_bp.route("/users/<string:user_email>", methods=["GET"])
def get_stats_for_user(user_email: str):
    # Log the request for user stats
    current_app.logger.info(f"Received request for stats for user: {user_email}")
    try:
        # Get the user's workout stats from the service
        user_stats = get_user_workout_stats(user_email)
        # If no stats are found, return a 404 response
        if user_stats is None:
            return jsonify({"message": "No stats found for this user."}), 404
        # Return the user's stats as JSON
        return jsonify(user_stats.model_dump()), 200
    except Exception as e:
        # Log and return any errors
        current_app.logger.error(f"Error fetching stats for user {user_email}: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve user statistics", "details": str(e)}), 500