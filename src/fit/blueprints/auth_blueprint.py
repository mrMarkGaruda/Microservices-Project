# Import Blueprint, request, and jsonify from Flask
from flask import Blueprint, request, jsonify
# Import ValidationError from pydantic for validation
from pydantic import ValidationError
# Import login and token schemas from the parent models_dto module
from ..models_dto import LoginSchema, TokenSchema
# Import authentication functions from the auth_service module
from ..services.auth_service import authenticate_user, create_access_token
# Import datetime for time operations
import datetime

# Create a Flask Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# Define a route for user login and token generation
@auth_bp.route("/oauth/token", methods=["POST"])
def login():
    try:
        # Check if content type is application/x-www-form-urlencoded (OAuth standard)
        content_type = request.headers.get('Content-Type', '')
        if 'application/x-www-form-urlencoded' in content_type:
            # Parse form data for OAuth
            login_data = {
                "email": request.form.get("username"),  # OAuth uses 'username' 
                "password": request.form.get("password")
            }
        else:  # Fallback to JSON
            login_data = request.get_json()
            
        # Validate the login data using the schema
        login_schema = LoginSchema.model_validate(login_data)
        
        # Authenticate the user
        user = authenticate_user(login_schema.email, login_schema.password)
        # If authentication fails, return an error
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Create access token with standard OAuth claims
        token_data = {
            "sub": user.email,
            "name": user.name,
            "role": user.role,
            "iss": "fit-api", 
            "iat": datetime.datetime.now(datetime.UTC), 
        }
        
        # Generate the access token
        access_token = create_access_token(
            data=token_data, 
        )
        
        # Create the token schema for the response
        token = TokenSchema(
            access_token=access_token,
            token_type="bearer"
        )
        
        # Include onboarding status in response
        response_data = token.model_dump()
        response_data["onboarded"] = user.onboarded
        
        # Return the token and onboarding status as JSON
        return jsonify(response_data), 200
        
    except ValidationError as e:
        # Return validation errors if the data is invalid
        return jsonify({"error": "Invalid login data", "details": e.errors()}), 400
    except Exception as e:
        # Return an error if something else goes wrong
        return jsonify({"error": "Error logging in", "details": str(e)}), 500
