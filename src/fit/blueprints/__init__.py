# Import the user_bp Blueprint from the user_blueprint module
from .user_blueprint import user_bp
# Import the auth_bp Blueprint from the auth_blueprint module
from .auth_blueprint import auth_bp
# Import the workout_bp Blueprint from the workout_blueprint module
from .workout_blueprint import workout_bp

# Define __all__ to specify what is exported from this module
__all__ = ['user_bp', 'auth_bp', 'workout_bp']