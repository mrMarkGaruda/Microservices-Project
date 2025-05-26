from flask import Flask
from .blueprints.auth import auth_bp
from .blueprints.users import user_bp
from .blueprints.fitness import fitness_bp
from .database import init_db
from .services.fitness_data_init import init_fitness_data

app = Flask(__name__)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(fitness_bp)

@app.route("/health")
def health():
    return {"status": "UP"}

def run_app():
    """Entry point for the application script"""
    # Initialize the database before starting the app
    init_db()
    
    # Initialize fitness data
    init_fitness_data()
    
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    run_app()