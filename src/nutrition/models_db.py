from .database import db  # Import the db object from the local database module
from datetime import datetime  # Import datetime for default timestamps


# Define the FoodItem model for the food_item table/class
class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key column
    name = db.Column(db.String(128), nullable=False)  # Name of the food item
    calories = db.Column(db.Float, nullable=False)  # Calories in the food item
    protein = db.Column(db.Float, nullable=False)  # Protein content
    carbs = db.Column(db.Float, nullable=False)  # Carbohydrate content
    fat = db.Column(db.Float, nullable=False)  # Fat content


# Define the MealLog model for the meal_log table/class
class MealLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key column
    user_id = db.Column(db.Integer, nullable=False)  # ID of the user
    food_item_id = db.Column(db.Integer, db.ForeignKey("food_item.id"), nullable=False)  # Foreign key to food item
    quantity = db.Column(db.Float, nullable=False)  # Quantity consumed
    meal_time = db.Column(db.DateTime, default=datetime.utcnow)  # Time of the meal
    food_item = db.relationship("FoodItem")  # Relationship to the FoodItem model
