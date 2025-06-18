from flask import Blueprint, request, jsonify
from ..services.nutrition_service import NutritionService
from ..models_db import db, FoodItem, MealLog

nutrition_bp = Blueprint("nutrition", __name__)


@nutrition_bp.route("/food", methods=["POST"])
def add_food():
    data = request.get_json(force=True) or {}
    food = NutritionService.add_food_item(
        name=data.get("name"),
        calories=data.get("calories"),
        protein=data.get("protein"),
        carbs=data.get("carbs"),
        fat=data.get("fat"),
    )
    return jsonify({"id": food.id, "name": food.name}), 201


@nutrition_bp.route("/food", methods=["GET"])
def get_food():
    foods = NutritionService.get_food_items()
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


@nutrition_bp.route("/meal", methods=["POST"])
def log_meal():
    data = request.get_json(force=True) or {}
    meal = NutritionService.log_meal(
        user_id=data.get("user_id"),
        food_item_id=data.get("food_item_id"),
        quantity=data.get("quantity"),
        meal_time=data.get("meal_time"),
    )
    return jsonify({"id": meal.id}), 201


@nutrition_bp.route("/meals/<int:user_id>", methods=["GET"])
def get_meals(user_id):
    meals = NutritionService.get_meals_for_user(user_id)
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
