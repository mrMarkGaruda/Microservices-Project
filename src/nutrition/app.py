# Import Flask to create the web application
from flask import Flask
# Import the database and migration objects from the local database module
from .database import db, migrate
# Import the nutrition blueprint for registering routes
from .blueprints.nutrition import nutrition_bp

# Create a new Flask application instance
app = Flask(__name__)
# Set the database URI for SQLAlchemy to use a local SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nutrition.db"
# Disable SQLAlchemy event system to save resources
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database with the Flask app context
db.init_app(app)
# Initialize database migrations with the app and db
migrate.init_app(app, db)

# Register the nutrition blueprint with a URL prefix
app.register_blueprint(nutrition_bp, url_prefix="/nutrition")

# If this script is run directly, start the Flask app on port 5004
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
