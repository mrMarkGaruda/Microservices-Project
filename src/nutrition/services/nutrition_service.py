from ..models_db import db, FoodItem, MealLog
from datetime import datetime


class NutritionService:
    @staticmethod
    def add_food_item(name, calories, protein, carbs, fat):
        """Create a new food item and save it to the database."""
        food = FoodItem(
            name=name, calories=calories, protein=protein, carbs=carbs, fat=fat
        )
        db.session.add(food)
        db.session.commit()
        return food

    @staticmethod
    def log_meal(user_id, food_item_id, quantity, meal_time=None):
        """Log a meal for a user, associating it with a food item."""
        meal = MealLog(
            user_id=user_id,
            food_item_id=food_item_id,
            quantity=quantity,
            meal_time=meal_time or datetime.utcnow(),
        )
        db.session.add(meal)
        db.session.commit()
        return meal

    @staticmethod
    def get_meals_for_user(user_id, start_date=None, end_date=None):
        """Retrieve meal logs for a specific user, optionally filtered by date."""
        query = MealLog.query.filter_by(user_id=user_id)
        if start_date:
            query = query.filter(MealLog.meal_time >= start_date)
        if end_date:
            query = query.filter(MealLog.meal_time <= end_date)
        return query.all()

    @staticmethod
    def get_food_items():
        """Retrieve all food items from the database."""
        return FoodItem.query.all()
