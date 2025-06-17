from flask import Blueprint, jsonify, current_app
from services.stats_service import get_user_workout_stats

stats_bp = Blueprint('stats', __name__, url_prefix='/stats')

@stats_bp.route("/users/<string:user_email>", methods=["GET"])
def get_stats_for_user(user_email: str):
    current_app.logger.info(f"Received request for stats for user: {user_email}")
    try:
        user_stats = get_user_workout_stats(user_email)
        if user_stats is None:
            return jsonify({"message": "No stats found for this user."}), 404
        return jsonify(user_stats.model_dump()), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching stats for user {user_email}: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve user statistics", "details": str(e)}), 500