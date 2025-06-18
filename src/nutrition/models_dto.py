from dataclasses import dataclass
from datetime import datetime


@dataclass
class FoodItemDTO:
    id: int
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float


@dataclass
class MealLogDTO:
    id: int
    user_id: int
    food_item_id: int
    quantity: float
    meal_time: datetime
    food_item: FoodItemDTO
