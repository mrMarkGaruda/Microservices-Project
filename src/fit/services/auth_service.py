# Import the jwt library for encoding and decoding JWT tokens
import jwt
# Import datetime for date and time operations
import datetime
# Import os for environment variable access
import os
# Import Optional and Callable for type hinting
from typing import Optional, Callable
# Import wraps to preserve function metadata in decorators
from functools import wraps
# Import request, jsonify, and g from Flask for HTTP handling and context
from flask import request, jsonify, g
# Import the UserModel from the parent models_db module
from ..models_db import UserModel
# Import the database session from the parent database module
from ..database import db_session
# Import the hash_password function from the user_service module
from ..services.user_service import hash_password


# Define the secret key for JWT token encoding/decoding
SECRET_KEY = "fit-secret-key" 
# Define the default access token expiration time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8

# Function to authenticate a user by email and password
def authenticate_user(email: str, password: str) -> Optional[UserModel]:
    """
    Authenticate a user by email and password
    """
    # Create a new database session
    db = db_session()
    try:
        # Query the user by email
        user = db.query(UserModel).filter(UserModel.email == email).first()
        # If the user does not exist, return None
        if not user:
            return None
        
        # Check if password matches
        hashed_password = hash_password(password)
        # If the password hash does not match, return None
        if user.password_hash != hashed_password:
            return None
            
        # Return the user if authentication is successful
        return user
    finally:
        # Close the database session
        db.close()

# Function to create a JWT access token
def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """
    Create a JWT token
    """
    # Copy the data to encode
    to_encode = data.copy()
    
    # Set the expiration time
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add the expiration to the payload
    to_encode.update({"exp": expire})
    # Encode the JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    
    # Return the encoded JWT token
    return encoded_jwt

# Function to decode a JWT token
def decode_token(token: str) -> dict:
    """
    Decode a JWT token
    """
    try:
        # Decode the token using the secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        # Return the decoded payload
        return payload
    except jwt.ExpiredSignatureError:
        # Return an error if the token is expired
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        # Return an error if the token is invalid
        return {"error": "Invalid token"}

# Decorator to require admin role for an endpoint
def admin_required(f: Callable) -> Callable:
    """
    Decorator to require admin role for an endpoint
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if Authorization header is present
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        
        # Check if it's a Bearer token
        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        # Extract the token from the header
        token = parts[1]
        # Decode the token
        payload = decode_token(token)
        
        # Check if token is valid
        if "error" in payload:
            return jsonify({"error": payload["error"]}), 401
        
        # Check if user has admin role
        if payload.get("role") != "admin":
            return jsonify({"error": "Admin privileges required"}), 403
            
        # Call the wrapped function if all checks pass
        return f(*args, **kwargs)
    
    return decorated_function

# Decorator to require a valid JWT token and set the user identity in Flask's g object
def jwt_required(f: Callable) -> Callable:
    """
    Decorator to require a valid JWT token and set the user identity in Flask's g object
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if Authorization header is present
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        
        # Check if it's a Bearer token
        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        # Extract the token from the header
        token = parts[1]
        # Decode the token
        payload = decode_token(token)
        
        # Check if token is valid
        if "error" in payload:
            return jsonify({"error": payload["error"]}), 401
        
        # Store user email in Flask's g object for the view function to use
        g.user_email = payload.get("sub")
            
        # Call the wrapped function if all checks pass
        return f(*args, **kwargs)
    
    return decorated_function 

# Decorator to require a valid API key in the X-API-Key header
def api_key_required(f: Callable) -> Callable:
    """
    Decorator to require a valid API key in the X-API-Key header
    The API key must match the FIT_API_KEY environment variable
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the API key from the request headers
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "X-API-Key header missing"}), 401
        
        # Get the expected API key from the environment
        expected_key = os.getenv('FIT_API_KEY')
        if not expected_key:
            return jsonify({"error": "API key not configured on server"}), 500
            
        # Check if the provided API key matches the expected key
        if api_key != expected_key:
            return jsonify({"error": "Invalid API key"}), 401
            
        # Call the wrapped function if the API key is valid
        return f(*args, **kwargs)
    
    return decorated_function