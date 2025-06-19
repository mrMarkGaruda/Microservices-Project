import logging  # Import the logging module to enable logging throughout the application
from flask import Flask, request, jsonify  # Import necessary functions and classes from Flask
from pydantic import ValidationError  # Import ValidationError from Pydantic for data validation

from .models_dto import UserSchema  # Import the UserSchema model for data validation and serialization

from .database import init_db, db_session  # Import database initialization and session management functions
from .models_db import UserModel  # Import the UserModel for database operations related to users
from .services.user_service import create_user as create_user_service  # Import the user creation service
from .blueprints import user_bp, auth_bp, workout_bp  # Import the blueprints for user, auth, and workout routes
import os  # Import os module to access environment variables

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG to capture all types of log messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Define the log message format
    datefmt='%Y-%m-%d %H:%M:%S'  # Define the date format in the log messages
)

# Create Flask app
app = Flask(__name__)  # Instantiate the Flask application
app.logger.setLevel(logging.DEBUG)  # Set the logger level to DEBUG for the app

# Force stdout to be unbuffered
import sys  # Import sys module to access system-specific parameters and functions
sys.stdout.reconfigure(line_buffering=True)  # Reconfigure stdout to be line-buffered

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/')  # Register the user blueprint with the app
app.register_blueprint(auth_bp, url_prefix='/')  # Register the auth blueprint with the app
app.register_blueprint(workout_bp, url_prefix='/workouts')  # Register the workout blueprint with the app

BOOTSTRAP_KEY = os.environ.get("BOOTSTRAP_KEY", "bootstrap-secret-key")  # Get the bootstrap key from environment variables

@app.route("/health")
def health():
    """Health check endpoint"""
    return {"status": "UP"}  # Return a JSON response indicating the service is up

@app.route("/bootstrap/admin", methods=["POST"])
def create_bootstrap_admin():
    """Endpoint to create a bootstrap admin user"""
    try:
        # This endpoint should be secured with a special bootstrap key
        bootstrap_key = request.headers.get('X-Bootstrap-Key')  # Get the bootstrap key from the request headers
        if not bootstrap_key or bootstrap_key != BOOTSTRAP_KEY:  # Check if the bootstrap key is valid
            return jsonify({"error": "Invalid bootstrap key"}), 401  # Return an error response if the key is invalid
            
        # Check if admin already exists to prevent multiple bootstraps
        db = db_session()  # Create a new database session
        admin_exists = db.query(UserModel).filter(UserModel.role == "admin").first() is not None  # Check if an admin user already exists
        db.close()  # Close the database session
        
        if admin_exists:
            return jsonify({"error": "Admin user already exists"}), 409  # Return an error if the admin user already exists
            
        # Create admin user
        admin_data = request.get_json()  # Get the admin data from the request body
        admin_data["role"] = "admin"  # Ensure the role is set to admin
        
        admin_user = UserSchema.model_validate(admin_data)  # Validate and serialize the admin data
        created_admin = create_user_service(admin_user)  # Create the admin user using the user service
        
        return jsonify(created_admin.model_dump()), 201  # Return the created admin user data with a 201 status code
        
    except ValidationError as e:
        return jsonify({"error": "Invalid admin data", "details": e.errors()}), 400  # Return validation errors if any
    except Exception as e:
        return jsonify({"error": "Error creating admin", "details": str(e)}), 500  # Return a generic error response for any other exceptions

def run_app():
    """Entry point for the application script"""
    # Initialize the database before starting the app
    init_db()  # Initialize the database

    app.run(host="0.0.0.0", port=5000, debug=True)  # Start the Flask application

if __name__ == "__main__":
    run_app()  # Run the application if this script is executed as the main module

