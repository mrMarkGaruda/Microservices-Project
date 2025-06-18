from src.nutrition.app import app
from src.nutrition.database import db

with app.app_context():
    db.create_all()
    print("Nutrition DB initialized.")
