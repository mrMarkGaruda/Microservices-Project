# Import Blueprint, request, and jsonify from Flask
from flask import Blueprint, request, jsonify
# Import the NutritionService for business logic
from ..services.nutrition_service import NutritionService
# Import db, FoodItem, and MealLog models
from ..models_db import db, FoodItem, MealLog

# Create a Flask Blueprint for nutrition routes
nutrition_bp = Blueprint("nutrition", __name__)

# Define a route to add a new food item
@nutrition_bp.route("/food", methods=["POST"])
def add_food():
    # Get JSON data from the request
    data = request.get_json(force=True) or {}
    # Add the food item using the NutritionService
    food = NutritionService.add_food_item(
        name=data.get("name"),
        calories=data.get("calories"),
        protein=data.get("protein"),
        carbs=data.get("carbs"),
        fat=data.get("fat"),
    )
    # Return the created food item's ID and name
    return jsonify({"id": food.id, "name": food.name}), 201

# Define a route to get all food items
@nutrition_bp.route("/food", methods=["GET"])
def get_food():
    # Get all food items using the NutritionService
    foods = NutritionService.get_food_items()
    # Return a list of food items as JSON
    return jsonify(
        [
            {
                "id": f.id,
                "name": f.name,
                "calories": f.calories,
                "protein": f.protein,
                "carbs": f.carbs,
                "fat": f.fat,
            }
            for f in foods
        ]
    )

# Define a route to log a meal
@nutrition_bp.route("/meal", methods=["POST"])
def log_meal():
    # Get JSON data from the request
    data = request.get_json(force=True) or {}
    # Log the meal using the NutritionService
    meal = NutritionService.log_meal(
        user_id=data.get("user_id"),
        food_item_id=data.get("food_item_id"),
        quantity=data.get("quantity"),
        meal_time=data.get("meal_time"),
    )
    # Return the created meal log's ID
    return jsonify({"id": meal.id}), 201

# Define a route to get all meals for a user
@nutrition_bp.route("/meals/<int:user_id>", methods=["GET"])
def get_meals(user_id):
    # Get all meals for the user using the NutritionService
    meals = NutritionService.get_meals_for_user(user_id)
    # Return a list of meal logs as JSON
    return jsonify(
        [
            {
                "id": m.id,
                "food_item": m.food_item.name,
                "quantity": m.quantity,
                "meal_time": m.meal_time.isoformat(),
            }
            for m in meals
        ]
    )
