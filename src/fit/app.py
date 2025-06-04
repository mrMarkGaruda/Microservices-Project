import os
import sys
from flask import Flask

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from blueprints.auth import auth_bp
from blueprints.users import user_bp
from blueprints.fitness import fitness_bp
from database import init_db
from services.fitness_data_init import init_fitness_data

def create_app(config=None):
    """Application factory pattern for testing"""
    app = Flask(__name__)
    
    # Apply configuration
    if config:
        app.config.update(config)
    
    # Set default configuration
    app.config.setdefault('SECRET_KEY', os.getenv('SECRET_KEY', 'fit-secret-key'))
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(fitness_bp)

    @app.route("/health")
    def health():
        return {"status": "UP"}
    
    return app

# Create the app instance for direct usage
app = create_app()

def run_app():
    """Entry point for the application script"""
    try:
        # Initialize the database before starting the app
        init_db()
        
        # Initialize fitness data
        init_fitness_data()
        
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
    
    print("🚀 Starting monolith service on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    run_app()