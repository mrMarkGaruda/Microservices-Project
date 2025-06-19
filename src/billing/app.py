# Import the logging module for logging messages
import logging
# Import Flask and jsonify for creating the web app and JSON responses
from flask import Flask, jsonify
# Import functions to initialize the database and get the session
from database import init_db, db_session
# Import the billing blueprint for registering routes
from blueprints.billing_blueprint import billing_bp
# Import the function to seed initial billing plans
from services.billing_service import seed_initial_plans
# Import os and sys for environment and system operations
import os
import sys

# Configure the logging settings for the application
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
# Create a logger for this module
logger = logging.getLogger(__name__)

# Function to create and configure the Flask app
def create_app():
    # Create a new Flask app instance
    app = Flask(__name__)
    # Set the logger level for the app
    app.logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    # Initialize the database and seed plans within the app context
    with app.app_context():
        init_db()
        seed_initial_plans()
    # Register the billing blueprint with the app
    app.register_blueprint(billing_bp)
    # Define a health check endpoint
    @app.route("/health")
    def health():
        logger.debug("Billing service health check endpoint called")
        return jsonify({"status": "UP", "service": "Billing Service"})
    # Remove the database session after each request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
        logger.debug("Billing DB session removed.")
    # Return the configured app
    return app

# Create the Flask app instance
app = create_app()

# Function to run the Flask app with environment-based configuration
def run_flask_app():
    # Get the port from the environment or use 5003 by default
    port = int(os.getenv("BILLING_SERVICE_PORT", 5003))
    # Determine if debug mode should be enabled
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    logger.info(f"Starting Billing Service on port {port} with debug mode: {debug_mode}")
    # Run the Flask app
    app.run(host="0.0.0.0", port=port, debug=debug_mode, use_reloader=not debug_mode)

# If this script is run directly, start the Flask app
if __name__ == "__main__":
    run_flask_app()
