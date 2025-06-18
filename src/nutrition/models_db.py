from .database import db
from datetime import datetime


class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)


class MealLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    food_item_id = db.Column(db.Integer, db.ForeignKey("food_item.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    meal_time = db.Column(db.DateTime, default=datetime.utcnow)
    food_item = db.relationship("FoodItem")
