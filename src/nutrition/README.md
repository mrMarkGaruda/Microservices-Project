# Nutrition Microservice

This service allows users to track their nutrition by logging meals and food items. It provides endpoints to add food items, log meals, and retrieve meal history for users.

## Endpoints

- `POST /nutrition/food` — Add a new food item
- `GET /nutrition/food` — List all food items
- `POST /nutrition/meal` — Log a meal for a user
- `GET /nutrition/meals/<user_id>` — Get all meals for a user

## Running Locally

1. Build and start with Docker Compose:
   ```sh
   docker-compose up --build nutrition
   ```
2. Initialize the database (if needed):
   ```sh
   docker-compose run nutrition python db_init_scripts/init_nutrition_db.py
   ```

## Environment Variables

- `NUTRITION_DB_URL` — Database connection string (default: sqlite:///nutrition.db)
