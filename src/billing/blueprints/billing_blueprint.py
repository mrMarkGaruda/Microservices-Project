from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError, EmailStr
from services.billing_service import (
    get_available_plans,
    create_subscription,
    get_user_subscription_status,
    cancel_subscription,
    seed_initial_plans
)
from models_dto import SubscriptionCreateRequestSchema

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

@billing_bp.route("/plans", methods=["GET"])
def list_plans_route():
    try:
        plans = get_available_plans()
        return jsonify([plan.model_dump() for plan in plans]), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching available plans: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve plans"}), 500

@billing_bp.route("/subscriptions", methods=["POST"])
def create_subscription_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON payload"}), 400
        validated_data = SubscriptionCreateRequestSchema(**data)
        subscription = create_subscription(
            user_email=validated_data.user_email,
            plan_id_name=validated_data.plan_id_name
        )
        if subscription:
            return jsonify(subscription.model_dump()), 201
        else:
            return jsonify({"error": "Failed to create subscription or user already has active subscription"}), 400
    except ValidationError as ve:
        current_app.logger.warning(f"Validation error creating subscription: {ve.errors()}", exc_info=True)
        return jsonify({"error": "Invalid input", "details": ve.errors()}), 422
    except Exception as e:
        current_app.logger.error(f"Error creating subscription: {e}", exc_info=True)
        return jsonify({"error": "Failed to create subscription"}), 500

@billing_bp.route("/subscriptions/users/<string:user_email_str>", methods=["GET"])
def get_user_subscription_route(user_email_str: str):
    try:
        EmailStr.validate(user_email_str)
        status = get_user_subscription_status(user_email_str)
        return jsonify(status.model_dump()), 200
    except ValidationError:
        return jsonify({"error": "Invalid email format"}), 422
    except Exception as e:
        current_app.logger.error(f"Error fetching subscription status for user '{user_email_str}': {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve subscription status"}), 500

@billing_bp.route("/subscriptions/users/<string:user_email_str>/cancel", methods=["POST"])
def cancel_subscription_route(user_email_str: str):
    try:
        EmailStr.validate(user_email_str)
        subscription = cancel_subscription(user_email_str)
        if subscription:
            return jsonify(subscription.model_dump()), 200
        else:
            return jsonify({"error": "No active subscription found to cancel or cancellation failed"}), 404
    except ValidationError:
        return jsonify({"error": "Invalid email format"}), 422
    except Exception as e:
        current_app.logger.error(f"Error cancelling subscription for user '{user_email_str}': {e}", exc_info=True)
        return jsonify({"error": "Failed to cancel subscription"}), 500
