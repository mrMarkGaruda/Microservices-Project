from flask import Flask, request, jsonify
import random
import time

app = Flask(__name__)

EXERCISE_TEMPLATES = [
    {"id": 1, "name": "Push-ups", "sets": 3, "reps": "10-15", "muscle_groups": ["chest", "triceps"]},
    {"id": 2, "name": "Squats", "sets": 4, "reps": "12-20", "muscle_groups": ["legs", "glutes"]},
    {"id": 3, "name": "Pull-ups", "sets": 3, "reps": "5-10", "muscle_groups": ["back", "biceps"]},
    {"id": 4, "name": "Burpees", "sets": 3, "reps": "8-12", "muscle_groups": ["full_body"]},
    {"id": 5, "name": "Lunges", "sets": 3, "reps": "10-15", "muscle_groups": ["legs", "glutes"]},
    {"id": 6, "name": "Plank", "sets": 3, "duration": "30-60s", "muscle_groups": ["core"]},
]

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "coach"})

@app.route('/generate-wod', methods=['POST'])
def generate_wod():
    data = request.get_json()
    
    time.sleep(random.uniform(1, 2))
    
    user_email = data.get('user_email')
    excluded_exercises = data.get('excluded_exercises', [])
    
    available_exercises = [
        ex for ex in EXERCISE_TEMPLATES 
        if ex['name'].lower() not in [e.lower() for e in excluded_exercises]
    ]
    
    num_exercises = min(6, len(available_exercises))
    selected_exercises = random.sample(available_exercises, num_exercises)
    
    wod = {
        "exercises": selected_exercises,
        "generated_at": time.time(),
        "user_email": user_email,
        "source": "coach_microservice"
    }
    
    return jsonify(wod)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)