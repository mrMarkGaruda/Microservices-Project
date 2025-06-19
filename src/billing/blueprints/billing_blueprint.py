# Import Blueprint, request, jsonify, and current_app from Flask
from flask import Blueprint, request, jsonify, current_app
# Import ValidationError and EmailStr from pydantic for validation
from pydantic import ValidationError, EmailStr
# Import billing service functions for use in routes
from services.billing_service import (
    get_available_plans,
    create_subscription,
    get_user_subscription_status,
    cancel_subscription,
    seed_initial_plans
)
# Import the schema for creating a subscription
from models_dto import SubscriptionCreateRequestSchema

# Create a Flask Blueprint for billing routes
billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

# Define a route to list all available billing plans
@billing_bp.route("/plans", methods=["GET"])
def list_plans_route():
    try:
        # Get the available plans from the service
        plans = get_available_plans()
        # Return the plans as JSON
        return jsonify([plan.model_dump() for plan in plans]), 200
    except Exception as e:
        # Log and return an error if something goes wrong
        current_app.logger.error(f"Error fetching available plans: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve plans"}), 500

# Define a route to create a new subscription
@billing_bp.route("/subscriptions", methods=["POST"])
def create_subscription_route():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        # If no data is provided, return an error
        if not data:
            return jsonify({"error": "Missing JSON payload"}), 400
        # Validate the data using the schema
        validated_data = SubscriptionCreateRequestSchema(**data)
        # Call the service to create the subscription
        subscription = create_subscription(
            user_email=validated_data.user_email,
            plan_id_name=validated_data.plan_id_name
        )
        # If the subscription was created, return it
        if subscription:
            return jsonify(subscription.model_dump()), 201
        else:
            # If not, return an error
            return jsonify({"error": "Failed to create subscription or user already has active subscription"}), 400
    except ValidationError as ve:
        # Log and return validation errors
        current_app.logger.warning(f"Validation error creating subscription: {ve.errors()}", exc_info=True)
        return jsonify({"error": "Invalid input", "details": ve.errors()}), 422
    except Exception as e:
        # Log and return any other errors
        current_app.logger.error(f"Error creating subscription: {e}", exc_info=True)
        return jsonify({"error": "Failed to create subscription"}), 500

# Define a route to get a user's subscription status
@billing_bp.route("/subscriptions/users/<string:user_email_str>", methods=["GET"])
def get_user_subscription_route(user_email_str: str):
    try:
        # Validate the email format
        EmailStr.validate(user_email_str)
        # Get the user's subscription status from the service
        status = get_user_subscription_status(user_email_str)
        # Return the status as JSON
        return jsonify(status.model_dump()), 200
    except ValidationError:
        # Return an error if the email is invalid
        return jsonify({"error": "Invalid email format"}), 422
    except Exception as e:
        # Log and return any other errors
        current_app.logger.error(f"Error fetching subscription status for user '{user_email_str}': {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve subscription status"}), 500

# Define a route to cancel a user's subscription
@billing_bp.route("/subscriptions/users/<string:user_email_str>/cancel", methods=["POST"])
def cancel_subscription_route(user_email_str: str):
    try:
        # Validate the email format
        EmailStr.validate(user_email_str)
        # Call the service to cancel the subscription
        subscription = cancel_subscription(user_email_str)
        # If a subscription was cancelled, return it
        if subscription:
            return jsonify(subscription.model_dump()), 200
        else:
            # If not, return an error
            return jsonify({"error": "No active subscription found to cancel or cancellation failed"}), 404
    except ValidationError:
        # Return an error if the email is invalid
        return jsonify({"error": "Invalid email format"}), 422
    except Exception as e:
        # Log and return any other errors
        current_app.logger.error(f"Error cancelling subscription for user '{user_email_str}': {e}", exc_info=True)
        return jsonify({"error": "Failed to cancel subscription"}), 500
