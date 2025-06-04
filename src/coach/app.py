import os
import sys
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import random
import time

# Add database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://fitness_user:fitness_password@localhost:5432/fitness_db')

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print("✅ Coach service connected to database")
except Exception as e:
    print(f"⚠️ Coach service database connection warning: {e}")
    engine = None
    SessionLocal = None

app = Flask(__name__)

# Fallback exercise templates if database is not available
EXERCISE_TEMPLATES = [
    {"id": 1, "name": "Push-ups", "sets": 3, "reps": "10-15", "muscle_groups": ["chest", "triceps"], "muscle_group_id": 1},
    {"id": 2, "name": "Squats", "sets": 4, "reps": "12-20", "muscle_groups": ["legs", "glutes"], "muscle_group_id": 2},
    {"id": 3, "name": "Pull-ups", "sets": 3, "reps": "5-10", "muscle_groups": ["back", "biceps"], "muscle_group_id": 3},
    {"id": 4, "name": "Burpees", "sets": 3, "reps": "8-12", "muscle_groups": ["full_body"], "muscle_group_id": 4},
    {"id": 5, "name": "Lunges", "sets": 3, "reps": "10-15", "muscle_groups": ["legs", "glutes"], "muscle_group_id": 2},
    {"id": 6, "name": "Plank", "sets": 3, "duration": "30-60s", "muscle_groups": ["core"], "muscle_group_id": 5},
    {"id": 7, "name": "Mountain Climbers", "sets": 3, "reps": "15-20", "muscle_groups": ["core", "cardio"], "muscle_group_id": 5},
    {"id": 8, "name": "Deadlifts", "sets": 3, "reps": "8-12", "muscle_groups": ["back", "legs"], "muscle_group_id": 6},
]

def get_exercises_from_db():
    """Get exercises from database, fallback to templates"""
    if not engine:
        return EXERCISE_TEMPLATES
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT e.id, e.name, e.sets, e.reps, e.duration, 
                       mg.name as muscle_group_name, e.muscle_group_id
                FROM exercises e 
                JOIN muscle_groups mg ON e.muscle_group_id = mg.id
            """))
            
            exercises = []
            for row in result:
                exercise = {
                    "id": row.id,
                    "name": row.name,
                    "sets": row.sets or 3,
                    "muscle_group_id": row.muscle_group_id,
                    "muscle_groups": [row.muscle_group_name]
                }
                
                if row.reps:
                    exercise["reps"] = str(row.reps)
                if row.duration:
                    exercise["duration"] = row.duration
                    
                exercises.append(exercise)
            
            return exercises if exercises else EXERCISE_TEMPLATES
    except Exception as e:
        print(f"Database query failed, using fallback: {e}")
        return EXERCISE_TEMPLATES

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "coach"})

@app.route('/exercises', methods=['GET'])
def get_all_exercises():
    """Get all exercises"""
    exercises = get_exercises_from_db()
    return jsonify({"exercises": exercises})

@app.route('/exercises/<int:exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    """Get a specific exercise by ID"""
    exercises = get_exercises_from_db()
    exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
    
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404
    
    return jsonify(exercise)

@app.route('/exercises/muscle-group/<int:muscle_group_id>', methods=['GET'])
def get_exercises_by_muscle_group(muscle_group_id):
    """Get exercises by muscle group ID"""
    exercises = get_exercises_from_db()
    filtered_exercises = [ex for ex in exercises if ex.get('muscle_group_id') == muscle_group_id]
    
    return jsonify({"exercises": filtered_exercises})

@app.route('/generate-wod', methods=['POST'])
def generate_wod():
    """Generate workout of the day"""
    data = request.get_json() or {}
    
    # Simulate processing time
    time.sleep(random.uniform(0.5, 1.5))
    
    user_email = data.get('user_email', data.get('email'))
    excluded_exercises = data.get('excluded_exercises', [])
    
    if not user_email:
        return jsonify({"error": "User email is required"}), 400
    
    exercises = get_exercises_from_db()
    available_exercises = [
        ex for ex in exercises 
        if ex['name'].lower() not in [e.lower() for e in excluded_exercises]
    ]
    
    num_exercises = min(6, len(available_exercises))
    if num_exercises == 0:
        return jsonify({"error": "No exercises available"}), 400
    
    selected_exercises = random.sample(available_exercises, num_exercises)
    
    wod = {
        "exercises": selected_exercises,
        "generated_at": time.time(),
        "user_email": user_email,
        "source": "coach_microservice",
        "total_exercises": len(selected_exercises)
    }
    
    return jsonify(wod)

if __name__ == '__main__':
    print("🚀 Starting coach service on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=False)