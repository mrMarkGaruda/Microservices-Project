# Import dataclass decorator for data transfer objects
from dataclasses import dataclass
# Import datetime for date/time fields
from datetime import datetime


# Define a data transfer object for a food item
@dataclass
class FoodItemDTO:
    id: int  # ID of the food item
    name: str  # Name of the food item
    calories: float  # Calories in the food item
    protein: float  # Protein content
    carbs: float  # Carbohydrate content
    fat: float  # Fat content


# Define a data transfer object for a meal log
@dataclass
class MealLogDTO:
    id: int  # ID of the meal log
    user_id: int  # ID of the user
    food_item_id: int  # ID of the food item
    quantity: float  # Quantity consumed
    meal_time: datetime  # Time of the meal
    food_item: FoodItemDTO  # The food item object
