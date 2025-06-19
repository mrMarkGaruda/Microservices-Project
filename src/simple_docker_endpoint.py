# Import Flask and related functions for web server and HTTP responses
from flask import Flask, jsonify, request, make_response
# Import json module for JSON operations
import json
# Import re module for regular expressions
import re

# Create a Flask application instance
app = Flask(__name__)

# --- Hardcoded Data from message (5).json variables ---
# These are the default values and dynamic ones will be handled by the mock server
# to mimic variable replacement.
MOCK_DATA = {
    "user_email": "jane.doe@mail.com",  # Default user email
    "user_password": "strongpassword123",  # Default user password
    "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",  # Example JWT token
    "user_id": "usr-d4e5f123-7890-1abc-def2-345678901234",  # Default user ID
    "new_user_email": "test.user@example.com",  # New user email for testing
    "new_user_id": "usr-ac8f9123-4de5-6789-abcd-0123456789ef",  # New user ID for testing
    "subscription_id": "sub-id-123-abc",  # Example subscription ID
    "last_session_id": "sess-id-123-xyz",  # Example session ID
    "integration_user_email": "integration_test_user@example.com",  # Integration test user email
    "integration_user_id": "int-user-id-123",  # Integration test user ID
    "temp_user_email": "temp.deact@example.com",  # Temporary deactivated user email
    "temp_user_id": "temp-id-deact-123",  # Temporary deactivated user ID
    # Initial states for dynamic values
    "users": {
        "usr-d4e5f123-7890-1abc-def2-345678901234": {
            "id": "usr-d4e5f123-7890-1abc-def2-345678901234",  # User ID
            "email": "jane.doe@mail.com",  # User email
            "name": "Jane Doe",  # User name
            "role": "user",  # User role
            "created_at": "2024-06-18T12:00:00Z"  # Account creation timestamp
        },
         "adm-7f8e9123-4de5-6789-abcd-0123456789ef": {
            "id": "adm-7f8e9123-4de5-6789-abcd-0123456789ef",  # Admin user ID
            "email": "admin@example.com",  # Admin email
            "name": "Admin User",  # Admin name
            "role": "admin"  # Admin role
        },
        "usr-8a9b0123-5ef6-789a-bcde-123456789012": {
            "id": "usr-8a9b0123-5ef6-789a-bcde-123456789012",  # User 1 ID
            "email": "user1@example.com",  # User 1 email
            "name": "User One",  # User 1 name
            "role": "user"  # User 1 role
        },
        "usr-9b0c1234-6f07-89ab-cdef-234567890123": {
            "id": "usr-9b0c1234-6f07-89ab-cdef-234567890123",  # User 2 ID
            "email": "user2@example.com",  # User 2 email
            "name": "User Two",  # User 2 name
            "role": "user"  # User 2 role
        },
    },
    "subscriptions": {
        "jane.doe@mail.com": {
            "id": "sub-id-123-abc",  # Subscription ID
            "user_email": "jane.doe@mail.com",  # User email for subscription
            "plan_id_name": "premium_monthly",  # Plan name
            "is_active": True,  # Subscription active status
            "start_date": "2024-06-18T11:00:00Z",  # Subscription start date
            "end_date": "2024-07-18T11:00:00Z"  # Subscription end date
        }
    },
    "workouts": {
        "jane.doe@mail.com": [
            {
                "id": "sess-id-456-abc",
                "user_email": "jane.doe@mail.com",
                "date": "2024-06-17T18:00:00Z",
                "duration_minutes": 60,
                "calories_burned": 400,
                "exercises_completed": [
                    {"exercise_id": 1, "reps": 12, "sets": 3},
                    {"exercise_id": 2, "reps": 15, "sets": 3}
                ]
            },
            {
                "id": "sess-id-123-xyz",
                "user_email": "jane.doe@mail.com",
                "date": "2024-06-16T10:00:00Z",
                "duration_minutes": 45,
                "calories_burned": 300,
                "exercises_completed": [
                    {"exercise_id": 3, "reps": 8, "sets": 4}
                ]
            }
        ]
    },
    "stats": {
        "jane.doe@mail.com": {
            "user_email": "jane.doe@mail.com",
            "total_workouts": 10,
            "total_reps": 500,
            "last_workout_date": "2024-06-17T18:00:00Z",
            "average_workout_duration_minutes": 45,
            "longest_streak_days": 7
        }
    }
}

# Helper function to substitute variables in a string
def substitute_variables(text, variables):
    """
    Replaces {{variable_name}} placeholders in a string with their values from the variables dictionary.
    Handles nested variables.
    """
    for _ in range(5):  # Max 5 iterations to resolve nested variables
        matches = re.findall(r"\{\{([a-zA-Z0-9_]+)\}\}", text)
        if not matches:
            break
        for match in matches:
            if match in variables:
                text = text.replace(f"{{{{{match}}}}}", str(variables[match]))
    return text

# Helper function to parse JSON body and substitute variables
def parse_and_substitute_body(body_raw, variables):
    """Parses a JSON string and substitutes variables within its values."""
    if not body_raw:
        return {}
    try:
        parsed_body = json.loads(body_raw)
        # Recursively substitute variables in dictionary values
        def deep_substitute(obj):
            if isinstance(obj, dict):
                return {k: deep_substitute(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [deep_substitute(elem) for elem in obj]
            elif isinstance(obj, str):
                return substitute_variables(obj, variables)
            else:
                return obj
        return deep_substitute(parsed_body)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in request body"}


# Endpoint definitions from the Postman collection
# Base URLs are replaced with relative paths for a single Flask app

# 1. Authentication Service
@app.route("/oauth/token", methods=["POST"])
def auth_token():
    try:
        req_data = request.get_json()
        email = req_data.get("email")
        password = req_data.get("password")

        if not email or not password:
            return jsonify({"message": "Both email and password are required"}), 400

        # Positive case: Login and Get JWT
        if email == MOCK_DATA["user_email"] and password == MOCK_DATA["user_password"]:
            response_body = {
                "access_token": MOCK_DATA["jwt_token"],
                "token_type": "bearer",
                "expires_in": 3600
            }
            resp = make_response(jsonify(response_body), 200)
            resp.headers["Content-Type"] = "application/json"
            resp.headers["X-RateLimit-Limit"] = "60"
            resp.headers["X-RateLimit-Remaining"] = "59"
            resp.headers["X-RateLimit-Reset"] = "1678886400" # A fixed timestamp
            return resp
        # Invalid Credentials
        elif email == "invalid@mail.com" and password == "wrongpassword":
            # The Postman test expects "Invalid credentials provided"
            return jsonify({"message": "Invalid credentials provided"}), 401
        # Integration test user login
        elif email == MOCK_DATA["integration_user_email"] and password == "Integration@123":
            response_body = {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpbnQtdXNlci1pZDEyMyIsIm5hbWUiOiJJbnRlZ3JhdGlvbiBVc2VyIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE2Nzg4ODY1MjJ9.IntegrationToken",
                "token_type": "bearer",
                "expires_in": 3600
            }
            resp = make_response(jsonify(response_body), 200)
            resp.headers["Content-Type"] = "application/json"
            resp.headers["X-RateLimit-Limit"] = "60"
            resp.headers["X-RateLimit-Remaining"] = "59"
            resp.headers["X-RateLimit-Reset"] = "1678886400"
            return resp

        return jsonify({"message": "Invalid credentials provided"}), 401
    except Exception as e:
        return jsonify({"message": f"Error processing request: {e}"}), 400


# 2. User & Monolith Service
@app.route("/users", methods=["POST"])
def create_new_user():
    try:
        req_data = request.get_json()
        email = req_data.get("email")
        name = req_data.get("name")
        password = req_data.get("password")
        role = req_data.get("role")

        if not email or not name or not password or not role:
            return jsonify({"message": "Missing required fields"}), 400

        # Existing Email Conflict
        if email == MOCK_DATA["new_user_email"] or email == MOCK_DATA["user_email"] or email in MOCK_DATA["users"]:
            return jsonify({"message": "The provided email address is already registered"}), 409
        # Invalid Role
        if role not in ["user", "admin"]:
            # The Postman test expects "The specified user role is invalid"
            return jsonify({"message": "The specified user role is invalid"}), 400
        # XSS Input Attempt
        if "<script>" in email:
            return jsonify({"message": "Invalid email format or potential malicious input detected"}), 400

        # Positive case: Create New User
        # Ensure new_user_id matches the Postman test expectation for a positive case
        if email == MOCK_DATA["new_user_email"]:
            new_user_id = MOCK_DATA["new_user_id"]
        elif email == MOCK_DATA["integration_user_email"]:
            new_user_id = MOCK_DATA["integration_user_id"]
        elif email == MOCK_DATA["temp_user_email"]:
            new_user_id = MOCK_DATA["temp_user_id"]
        else:
            # Fallback for other new user creations if needed, though Postman test targets specific emails
            new_user_id = "usr-" + str(len(MOCK_DATA["users"]) + 1) + "-new-id"


        user_data = {
            "id": new_user_id,
            "email": email,
            "name": name,
            "role": role,
            "created_at": "2024-06-18T12:00:00Z" # Hardcoded for consistency
        }
        MOCK_DATA["users"][new_user_id] = user_data # Store the new user

        return jsonify(user_data), 201
    except Exception as e:
        return jsonify({"message": f"Error creating user: {e}"}), 400

@app.route("/users/<user_id>", methods=["GET"])
def get_user_profile(user_id):
    auth_header = request.headers.get("Authorization")

    # Unauthenticated Access
    if not auth_header or not auth_header.startswith("Bearer "):
        # Modified for Postman test case to include "missing"
        return jsonify({"message": "Authentication failed: Authentication token is missing"}), 401

    token = auth_header.split(" ")[1]
    # Invalid JWT Token
    if token == "this.is.a.bad.jwt.token":
        return jsonify({"message": "Authentication failed: Invalid token provided"}), 401
    # Expired JWT Token (simplified check for hardcoded expired token)
    if token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjN9.r4k_z7eQ8Xm5h4nK2L3J_j4S5G9L7M2Y8o9U6Z0A8k":
        return jsonify({"message": "Authentication failed: Token has expired"}), 401

    # Malicious Input (SQL Injection Attempt)
    if "OR 1=1--" in user_id:
        return jsonify({"message": "Invalid input for user ID: Malicious characters detected"}), 400

    # Non-existent User Profile
    if user_id == "non-existent-user-id" or user_id == MOCK_DATA["temp_user_id"]: # Deleted user
        return jsonify({"message": "User profile not found"}), 404

    # Get User Profile (Authenticated)
    # Check if the user_id matches a known user or the dynamic user_id
    if user_id == MOCK_DATA["user_id"] or user_id == MOCK_DATA["integration_user_id"]:
        user_data = MOCK_DATA["users"].get(user_id) or {
            "id": user_id,
            "email": MOCK_DATA["user_email"] if user_id == MOCK_DATA["user_id"] else MOCK_DATA["integration_user_email"],
            "name": "Jane Doe" if user_id == MOCK_DATA["user_id"] else "Integration User",
            "role": "user"
        }
        # The Postman test for "Get User Profile (Authenticated)" expects `pm.environment.get("user_email")`
        # and `pm.environment.get("user_id")` to match.
        # So, we ensure the email and ID in the response match the "global" mock data, which aligns with Postman's variables.
        if user_id == MOCK_DATA["user_id"]:
            user_data["email"] = MOCK_DATA["user_email"]
            user_data["name"] = "Jane Smith" # This matches the positive update test
        elif user_id == MOCK_DATA["integration_user_id"]:
             user_data["email"] = MOCK_DATA["integration_user_email"]
             user_data["name"] = "Integration User"

        return jsonify(user_data), 200
    return jsonify({"message": "User profile not found"}), 404


@app.route("/users/<user_id>", methods=["PUT"])
def update_user_profile(user_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "Authentication token is required"}), 401

    # For simplicity, assume valid token if present. In a real app, validate token content.
    # The Postman collection doesn't test invalid/expired tokens for PUT requests, so we skip detailed checks here.

    try:
        req_data = request.get_json()
        if "role" in req_data and req_data["role"] == "admin":
            # For this mock, assume only specific tokens (e.g., admin token) can change roles.
            # Here we simulate the forbidden response if a non-admin token tries to change role
            # by checking if the user is not the 'admin' from the MOCK_DATA.
            # This is a simplification; a real app would use the JWT's claims.
            if request.headers.get("Authorization") != f"Bearer {MOCK_DATA['jwt_token']}" and user_id == MOCK_DATA["user_id"]: # Assuming MOCK_DATA['jwt_token'] is for a non-admin user
                 return jsonify({"message": "Forbidden: You do not have the necessary privileges to change roles"}), 403

        # Simulate update for positive case
        if user_id == MOCK_DATA["user_id"]:
            # Update name if provided, keep other fields
            MOCK_DATA["users"][user_id]["name"] = req_data.get("name", MOCK_DATA["users"][user_id]["name"])
            response_body = {
                "id": user_id,
                "email": MOCK_DATA["users"][user_id]["email"],
                "name": MOCK_DATA["users"][user_id]["name"],
                "role": MOCK_DATA["users"][user_id]["role"]
            }
            return jsonify(response_body), 200

        return jsonify({"message": "User not found or update forbidden"}), 404

    except Exception as e:
        return jsonify({"message": f"Error updating user profile: {e}"}), 400

@app.route("/users/generateWods", methods=["POST"])
def generate_wods():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "Authentication token is required"}), 401

    # Check if the token corresponds to an admin (simplified)
    # In a real scenario, you'd decode the JWT and check its 'role' claim.
    # For this mock, we assume the default jwt_token is for a non-admin.
    # If a specific 'admin' token was sent, we'd allow it.
    if auth_header != f"Bearer {MOCK_DATA['jwt_token']}" : # Assume default token is not admin for this test
        # Admin access required for this endpoint
        # The Postman test expects "Permission denied: Administrator access required"
        return jsonify({"message": "Permission denied: Administrator access required"}), 403

    # Positive case: Admin Role
    return jsonify({
        "message": "WOD generation task successfully queued for all eligible users",
        "total_users": 5,
        "users_needing_workout": 2
    }), 202

@app.route("/users", methods=["GET"])
def get_all_users():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "Authentication token is required"}), 401

    # Check if the token corresponds to an admin (simplified)
    # For this mock, we assume the default jwt_token is for a non-admin.
    # If a specific 'admin' token was sent, we'd allow it.
    if auth_header != f"Bearer {MOCK_DATA['jwt_token']}" : # Assuming default token is not admin for this test
        # Modified for Postman test case to match "Admin access required"
        return jsonify({"message": "Forbidden: Admin access required to view all users"}), 403

    # Positive case: Admin Access
    users_list = [
        MOCK_DATA["users"]["adm-7f8e9123-4de5-6789-abcd-0123456789ef"],
        MOCK_DATA["users"]["usr-8a9b0123-5ef6-789a-bcde-123456789012"],
        MOCK_DATA["users"]["usr-9b0c1234-6f07-89ab-cdef-234567890123"]
    ]
    return jsonify(users_list), 200

@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "Authentication token is required"}), 401

    # Check for admin privileges (simplified)
    if auth_header != f"Bearer {MOCK_DATA['jwt_token']}" : # Assuming default token is not admin
        return jsonify({"message": "Forbidden: Administrative access is required to delete users"}), 403

    if user_id in MOCK_DATA["users"] or user_id == MOCK_DATA["new_user_id"] or user_id == MOCK_DATA["temp_user_id"]:
        # Simulate deletion
        if user_id in MOCK_DATA["users"]:
            del MOCK_DATA["users"][user_id]
        return "", 204 # No Content
    else:
        # Non-existent user to delete (though Postman test expects forbidden for non-admin)
        return jsonify({"message": "User not found"}), 404


# 3. Coach Service
@app.route("/createWod", methods=["POST"])
def create_wod():
    try:
        req_data = request.get_json()
        user_email = req_data.get("user_email")

        # Non-existent User for WOD
        if user_email == "nonexistent@example.com":
            return jsonify({"message": "User not found for WOD generation"}), 404

        # Simulate WOD generation based on user email (simplified for Free/Premium)
        if user_email == "premium.user@example.com":
            response_body = {
                "user_email": user_email,
                "generated_at": "2024-06-18T10:35:00Z",
                "exercises": [
                    {"id": 201, "name": "Deadlifts", "difficulty": 5, "description": "Barbell deadlifts, challenging."},
                    {"id": 202, "name": "Bench Press", "difficulty": 4, "description": "Barbell bench press."},
                    {"id": 203, "name": "Overhead Press", "difficulty": 4, "description": "Strict overhead press."},
                    {"id": 204, "name": "Pull-ups", "difficulty": 5, "description": "Bodyweight pull-ups."},
                    {"id": 205, "name": "Barbell Rows", "difficulty": 4, "description": "Bent-over barbell rows."},
                    {"id": 206, "name": "Front Squats", "difficulty": 4, "description": "Barbell front squats."},
                    {"id": 207, "name": "Box Jumps", "difficulty": 3, "description": "Explosive jumps onto a box."},
                    {"id": 208, "name": "Kettlebell Swings", "difficulty": 3, "description": "Powerful kettlebell swings."},
                    {"id": 209, "name": "Burpees", "difficulty": 5, "description": "Full body exercise: burpees."}
                ]
            }
        elif user_email == MOCK_DATA["integration_user_email"]:
             response_body = {
                "user_email": user_email,
                "generated_at": "2024-06-18T13:05:00Z",
                "exercises": [
                    {"id": 101, "name": "Integration Push-ups", "difficulty": 2},
                    {"id": 102, "name": "Integration Squats", "difficulty": 2}
                ]
            }
        else: # Free user or default
            response_body = {
                "user_email": user_email,
                "generated_at": "2024-06-18T10:30:00Z",
                "exercises": [
                    {"id": 101, "name": "Push-ups", "difficulty": 2, "description": "Standard bodyweight push-ups."},
                    {"id": 102, "name": "Squats", "difficulty": 2, "description": "Bodyweight squats."},
                    {"id": 103, "name": "Plank", "difficulty": 1, "description": "Hold plank position for 60 seconds."}
                ]
            }
        return jsonify(response_body), 200
    except Exception as e:
        return jsonify({"message": f"Error creating WOD: {e}"}), 400

@app.route("/exercises", methods=["GET"])
def get_all_exercises():
    exercises = [
        {"id": 1, "name": "Push-up", "description": "Classic push-up exercise.", "difficulty": 2},
        {"id": 2, "name": "Squat", "description": "Bodyweight squat for legs and glutes.", "difficulty": 2},
        {"id": 3, "name": "Deadlift", "description": "Full body strength exercise with a barbell.", "difficulty": 5},
        {"id": 4, "name": "Plank", "description": "Core strengthening exercise.", "difficulty": 1},
        {"id": 5, "name": "Burpee", "description": "High-intensity full-body exercise.", "difficulty": 4}
    ]
    return jsonify(exercises), 200

@app.route("/exercises/<int:exercise_id>", methods=["GET"])
def get_specific_exercise(exercise_id):
    exercises = {
        1: {"id": 1, "name": "Push-up", "description": "Classic push-up exercise.", "difficulty": 2},
        2: {"id": 2, "name": "Squat", "description": "Bodyweight squat for legs and glutes.", "difficulty": 2},
        3: {"id": 3, "name": "Deadlift", "description": "Full body strength exercise with a barbell.", "difficulty": 5},
        4: {"id": 4, "name": "Plank", "description": "Core strengthening exercise.", "difficulty": 1},
        5: {"id": 5, "name": "Burpee", "description": "High-intensity full-body exercise.", "difficulty": 4}
    }
    exercise = exercises.get(exercise_id)
    if exercise:
        return jsonify(exercise), 200
    return jsonify({"message": "Exercise with the specified ID could not be found"}), 404


# 4. Billing Service
@app.route("/billing/plans", methods=["GET"])
def list_billing_plans():
    plans = [
        {"plan_id_name": "basic", "name": "Basic Plan", "price": 0.00, "currency": "USD", "features": ["3 WODs/week", "Basic Stats"]},
        {"plan_id_name": "premium_monthly", "name": "Premium Monthly", "price": 19.99, "currency": "USD", "features": ["Unlimited WODs", "Advanced Stats", "Personal Coaching"]},
        {"plan_id_name": "premium_yearly", "name": "Premium Yearly", "price": 199.99, "currency": "USD", "features": ["Unlimited WODs", "Advanced Stats", "Personal Coaching", "Annual Discount"]}
    ]
    return jsonify(plans), 200

@app.route("/billing/subscriptions", methods=["POST"])
def create_user_subscription():
    try:
        req_data = request.get_json()
        user_email = req_data.get("user_email")
        plan_id_name = req_data.get("plan_id_name")

        # Invalid Plan
        if plan_id_name == "non_existent_plan":
            return jsonify({"message": "The specified plan ID does not exist"}), 400

        # Already Subscribed
        if user_email in MOCK_DATA["subscriptions"] and MOCK_DATA["subscriptions"][user_email]["is_active"]:
            return jsonify({"message": "This user already possesses an active subscription"}), 409

        # Positive Case
        new_sub_id = MOCK_DATA["subscription_id"] if user_email == MOCK_DATA["user_email"] else "sub-" + str(len(MOCK_DATA["subscriptions"]) + 1) + "-new"
        if user_email == MOCK_DATA["integration_user_email"]:
            new_sub_id = "int-sub-id-123"
        if user_email == MOCK_DATA["temp_user_email"]:
            new_sub_id = "temp-sub-id-1"


        subscription_data = {
            "id": new_sub_id,
            "user_email": user_email,
            "plan_id_name": plan_id_name,
            "is_active": True,
            "start_date": "2024-06-18T11:00:00Z", # Hardcoded
            "end_date": "2024-07-18T11:00:00Z" if plan_id_name == "premium_monthly" else "2025-06-18T13:10:00Z"
        }
        MOCK_DATA["subscriptions"][user_email] = subscription_data
        return jsonify(subscription_data), 201
    except Exception as e:
        return jsonify({"message": f"Error creating subscription: {e}"}), 400


@app.route("/billing/subscriptions/users/<user_email>", methods=["GET"])
def get_user_subscription_status(user_email):
    # No Subscription Found
    if user_email == "unsubscribed@example.com" or user_email == MOCK_DATA["temp_user_email"]:
        return jsonify({"message": "No active subscription found for this user"}), 404

    # Positive case
    if user_email in MOCK_DATA["subscriptions"]:
        sub = MOCK_DATA["subscriptions"][user_email]
        plan_details = next((p for p in list_billing_plans().json if p["plan_id_name"] == sub["plan_id_name"]), {})
        response_body = {
            "id": sub["id"],
            "user_email": sub["user_email"],
            "plan_id_name": sub["plan_id_name"],
            "plan_name": plan_details.get("name"),
            "price": plan_details.get("price"),
            "is_active": sub["is_active"],
            "start_date": sub["start_date"],
            "end_date": sub["end_date"]
        }
        return jsonify(response_body), 200
    return jsonify({"message": "No active subscription found for this user"}), 404


@app.route("/billing/subscriptions/<user_email>", methods=["DELETE"])
def cancel_user_subscription(user_email):
    # Non-existent Subscription to cancel
    if user_email == "nonexistent@example.com":
        return jsonify({"message": "No active subscription found for this user to cancel"}), 404

    # Positive case
    if user_email in MOCK_DATA["subscriptions"] and MOCK_DATA["subscriptions"][user_email]["is_active"]:
        MOCK_DATA["subscriptions"][user_email]["is_active"] = False
        MOCK_DATA["subscriptions"][user_email]["cancellation_date"] = "2024-06-18T12:00:00Z" # Hardcoded
        return jsonify(MOCK_DATA["subscriptions"][user_email]), 200
    return jsonify({"message": "No active subscription found for this user to cancel"}), 404


# 5. Stats Service
@app.route("/stats/users/<user_email>", methods=["GET"])
def get_user_workout_stats(user_email):
    # Non-existent User for Stats
    if user_email == "nonexistent@example.com" or user_email == MOCK_DATA["temp_user_email"]:
        return jsonify({"message": "Workout statistics not found for this user"}), 404

    # Positive case
    if user_email in MOCK_DATA["stats"]:
        return jsonify(MOCK_DATA["stats"][user_email]), 200
    # For integration user
    if user_email == MOCK_DATA["integration_user_email"]:
        return jsonify({
            "user_email": user_email,
            "total_workouts": 1,
            "total_reps": 75,
            "last_workout_date": "2024-06-18T13:15:00Z",
            "average_workout_duration_minutes": 60,
            "longest_streak_days": 1
        }), 200
    return jsonify({"message": "Workout statistics not found for this user"}), 404

@app.route("/stats/workouts", methods=["POST"])
def record_new_workout_session():
    try:
        req_data = request.get_json()
        user_email = req_data.get("user_email")

        # Invalid User for Workout Recording
        if user_email == "invalid-workout-user@example.com":
            return jsonify({"message": "The provided user email is invalid or not found"}), 400

        # Positive case
        session_id = MOCK_DATA["last_session_id"] if user_email == MOCK_DATA["user_email"] else "sess-" + str(len(MOCK_DATA["workouts"].get(user_email, [])) + 1) + "-new"
        if user_email == MOCK_DATA["integration_user_email"]:
            session_id = "int-sess-id-1"
        if user_email == MOCK_DATA["temp_user_email"]:
            session_id = "temp-sess-id-1"

        workout_data = {
            "id": session_id,
            "user_email": user_email,
            "date": "2024-06-18T12:00:00Z", # Hardcoded
            "duration_minutes": req_data.get("duration_minutes"),
            "calories_burned": req_data.get("calories_burned"),
            "exercises_completed": req_data.get("exercises_completed", [])
        }
        if user_email not in MOCK_DATA["workouts"]:
            MOCK_DATA["workouts"][user_email] = []
        MOCK_DATA["workouts"][user_email].append(workout_data)

        return jsonify({
            "message": "Workout session recorded successfully",
            "session_id": session_id,
            "user_email": user_email,
            "date": "2024-06-18T12:00:00Z" # Hardcoded
        }), 201
    except Exception as e:
        return jsonify({"message": f"Error recording workout: {e}"}), 400

@app.route("/stats/workouts/users/<user_email>", methods=["GET"])
def get_workout_history_for_user(user_email):
    # No History
    if user_email == "nohistory@example.com":
        return jsonify([]), 200

    # Positive case
    if user_email in MOCK_DATA["workouts"]:
        return jsonify(MOCK_DATA["workouts"][user_email]), 200

    return jsonify([]), 200 # Default to empty array if user has no history or is unknown


# 7. Security & Edge Cases
@app.route("/admin/auditlogs", methods=["GET"])
def access_forbidden_endpoint():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "Authentication token is required"}), 401
    # Assuming the default jwt_token is for a non-admin.
    if auth_header == f"Bearer {MOCK_DATA['jwt_token']}":
        return jsonify({"message": "Forbidden: Insufficient privileges for this operation"}), 403
    # If it was an admin token (not mocked here), it would return logs.
    return jsonify({"message": "Forbidden: Insufficient privileges for this operation"}), 403


@app.route("/some/rate-limited/endpoint", methods=["GET"])
def rate_limited_endpoint():
    # Simulate Rate Limit Exceeded
    resp = make_response(jsonify({
        "message": "Too many requests: You have exceeded the allowed rate limit. Please try again after 60 seconds."
    }), 429)
    resp.headers["Content-Type"] = "application/json"
    resp.headers["X-RateLimit-Retry-After"] = "60"
    return resp

@app.route("/health", methods=["GET"])
def health_check_endpoint():
    return jsonify({
        "status": "UP",
        "version": "1.0.0",
        "timestamp": "2024-06-18T15:00:00Z" # Hardcoded
    }), 200

@app.route("/metrics", methods=["GET"])
def metrics_endpoint():
    resp_body = """# HELP application_http_requests_total Total number of HTTP requests.
# TYPE application_http_requests_total counter
application_http_requests_total{method="GET",path="/health",status="200"} 1
# HELP application_database_queries_total Total number of database queries.
# TYPE application_database_queries_total counter
application_database_queries_total{operation="read"} 5"""
    resp = make_response(resp_body, 200)
    resp.headers["Content-Type"] = "text/plain; version=0.0.4; charset=utf-8"
    return resp

# Default root and error handlers
@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "ok", "message": "Mock API is running"}), 200

@app.errorhandler(404)
def handle_404(e):
    # This handler catches requests to non-defined routes that Flask would normally return 404 for.
    # We want to return a more "believable" API error if it's not a known route.
    # For paths that are specifically tested as 404 in Postman, they are handled in their respective routes.
    return jsonify({"message": "Resource not found"}), 404

@app.errorhandler(415)
def handle_415(e):
    # Specifically for "Unsupported Media Type"
    return jsonify({"message": "Unsupported Media Type: Please use application/json"}), 415

@app.errorhandler(Exception)
def handle_exception(e):
    # Catch-all for other unhandled exceptions, returning a generic server error
    app.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    return jsonify({"message": "An unexpected server error occurred."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)

