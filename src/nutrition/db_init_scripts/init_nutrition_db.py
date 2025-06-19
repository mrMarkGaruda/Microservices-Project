# Import the app instance from the nutrition app module
from src.nutrition.app import app
# Import the db object from the nutrition database module
from src.nutrition.database import db

# Create a new application context for the app
with app.app_context():
    # Create all tables in the database
    db.create_all()
    # Print a message indicating the database was initialized
    print("Nutrition DB initialized.")
