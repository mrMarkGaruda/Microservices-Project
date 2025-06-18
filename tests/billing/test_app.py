"""
Comprehensive tests for billing Flask app endpoints and integration.
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import datetime
from src.billing.app import create_app
from src.billing.models_dto import BillingPlanResponseSchema, SubscriptionResponseSchema, UserSubscriptionStatusResponseSchema

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['BILLING_DATABASE_URL'] = "sqlite:///:memory:"
    return app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

def test_health(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "UP"
    assert response.json["service"] == "Billing Service"

@patch("src.billing.blueprints.billing_blueprint.get_available_plans")
def test_list_plans_success(mock_get_plans, client):
    """Test successful plan listing"""
    mock_plans = [
        BillingPlanResponseSchema(
            id=1, plan_id_name="basic", name="Basic Plan", 
            price=Decimal("9.99"), currency="USD", 
            duration_days=30, features_description="Basic features", 
            is_active=True
        )
    ]
    mock_get_plans.return_value = mock_plans
    
    response = client.get("/billing/plans")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["plan_id_name"] == "basic"
    assert response.json[0]["name"] == "Basic Plan"

@patch("src.billing.blueprints.billing_blueprint.get_available_plans")
def test_list_plans_error(mock_get_plans, client):
    """Test plan listing with error"""
    mock_get_plans.side_effect = Exception("Database error")
    
    response = client.get("/billing/plans")
    assert response.status_code == 500
    assert "error" in response.json

@patch("src.billing.blueprints.billing_blueprint.create_subscription")
def test_create_subscription_success(mock_create_subscription, client):
    """Test successful subscription creation"""
    mock_subscription = SubscriptionResponseSchema(
        id=1, user_email="test@example.com", 
        start_date=datetime.now(),
        end_date=datetime.now(),
        is_currently_active=True,
        payment_status="paid",
        plan=BillingPlanResponseSchema(
            id=1, plan_id_name="basic", name="Basic Plan",
            price=Decimal("9.99"), currency="USD",
            duration_days=30, features_description="Basic features",
            is_active=True
        ),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_create_subscription.return_value = mock_subscription
    
    response = client.post("/billing/subscriptions", 
                          json={"user_email": "test@example.com", "plan_id_name": "basic"})
    assert response.status_code == 201
    assert response.json["user_email"] == "test@example.com"
    assert response.json["plan"]["plan_id_name"] == "basic"

@patch("src.billing.blueprints.billing_blueprint.create_subscription")
def test_create_subscription_validation_error(mock_create_subscription, client):
    """Test subscription creation with validation error"""
    response = client.post("/billing/subscriptions", 
                          json={"user_email": "invalid-email", "plan_id_name": "basic"})
    assert response.status_code == 400
    assert "error" in response.json

@patch("src.billing.blueprints.billing_blueprint.create_subscription")
def test_create_subscription_not_found(mock_create_subscription, client):
    """Test subscription creation with plan not found"""
    mock_create_subscription.return_value = None
    
    response = client.post("/billing/subscriptions", 
                          json={"user_email": "test@example.com", "plan_id_name": "nonexistent"})
    assert response.status_code == 404
    assert "not found" in response.json["error"]

@patch("src.billing.blueprints.billing_blueprint.create_subscription")
def test_create_subscription_server_error(mock_create_subscription, client):
    """Test subscription creation with server error"""
    mock_create_subscription.side_effect = Exception("Database error")
    
    response = client.post("/billing/subscriptions", 
                          json={"user_email": "test@example.com", "plan_id_name": "basic"})
    assert response.status_code == 500
    assert "error" in response.json

@patch("src.billing.blueprints.billing_blueprint.get_user_subscription_status")
def test_get_user_subscription_success(mock_get_subscription, client):
    """Test successful user subscription retrieval"""
    mock_subscription = UserSubscriptionStatusResponseSchema(
        user_email="test@example.com",
        plan_id_name="basic",
        plan_name="Basic Plan",
        is_active=True,
        start_date=datetime.now(),
        end_date=datetime.now()
    )
    mock_get_subscription.return_value = mock_subscription
    
    response = client.get("/billing/subscriptions/users/test@example.com")
    assert response.status_code == 200
    assert response.json["user_email"] == "test@example.com"
    assert response.json["is_active"] is True

@patch("src.billing.blueprints.billing_blueprint.get_user_subscription_status")
def test_get_user_subscription_not_found(mock_get_subscription, client):
    """Test user subscription retrieval with user not found"""
    mock_get_subscription.return_value = None
    
    response = client.get("/billing/subscriptions/users/nonexistent@example.com")
    assert response.status_code == 404
    assert "not found" in response.json["error"]

@patch("src.billing.blueprints.billing_blueprint.get_user_subscription_status")
def test_get_user_subscription_error(mock_get_subscription, client):
    """Test user subscription retrieval with error"""
    mock_get_subscription.side_effect = Exception("Database error")
    
    response = client.get("/billing/subscriptions/users/test@example.com")
    assert response.status_code == 500
    assert "error" in response.json

@patch("src.billing.blueprints.billing_blueprint.cancel_subscription")
def test_cancel_subscription_success(mock_cancel_subscription, client):
    """Test successful subscription cancellation"""
    mock_subscription = SubscriptionResponseSchema(
        id=1, user_email="test@example.com",
        start_date=datetime.now(),
        end_date=datetime.now(),
        is_currently_active=False,
        payment_status="cancelled",
        plan=BillingPlanResponseSchema(
            id=1, plan_id_name="basic", name="Basic Plan",
            price=Decimal("9.99"), currency="USD",
            duration_days=30, features_description="Basic features",
            is_active=True
        ),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_cancel_subscription.return_value = mock_subscription
    
    response = client.post("/billing/subscriptions/users/test@example.com/cancel")
    assert response.status_code == 200
    assert response.json["is_currently_active"] is False

@patch("src.billing.blueprints.billing_blueprint.cancel_subscription")
def test_cancel_subscription_not_found(mock_cancel_subscription, client):
    """Test subscription cancellation with subscription not found"""
    mock_cancel_subscription.return_value = None
    
    response = client.post("/billing/subscriptions/users/nonexistent@example.com/cancel")
    assert response.status_code == 404
    assert "not found" in response.json["error"]

@patch("src.billing.blueprints.billing_blueprint.cancel_subscription")
def test_cancel_subscription_error(mock_cancel_subscription, client):
    """Test subscription cancellation with error"""
    mock_cancel_subscription.side_effect = Exception("Database error")
    
    response = client.post("/billing/subscriptions/users/test@example.com/cancel")
    assert response.status_code == 500
    assert "error" in response.json

def test_invalid_email_format(client):
    """Test invalid email format in URL"""
    response = client.get("/billing/subscriptions/users/invalid-email-format")
    # This should still reach the endpoint, but validation might fail
    assert response.status_code in [400, 404, 500]

def test_missing_request_body(client):
    """Test POST request without body"""
    response = client.post("/billing/subscriptions")
    assert response.status_code == 400

def test_malformed_json(client):
    """Test POST request with malformed JSON"""
    response = client.post("/billing/subscriptions", 
                          data="invalid json",
                          content_type="application/json")
    assert response.status_code == 400
