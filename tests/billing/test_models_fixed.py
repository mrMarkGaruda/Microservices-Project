"""
Tests for billing.models_db and billing.models_dto
"""
import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock
from pydantic import ValidationError
from src.billing.models_dto import (
    BillingPlanBaseSchema, BillingPlanResponseSchema,
    SubscriptionCreateRequestSchema, SubscriptionBaseSchema,
    SubscriptionResponseSchema, UserSubscriptionStatusResponseSchema
)
from src.billing.models_db import BillingPlanModel, SubscriptionModel

class TestBillingPlanSchemas:
    """Test billing plan DTO schemas"""
    
    def test_billing_plan_base_schema_valid(self):
        """Test valid billing plan base schema"""
        plan = BillingPlanBaseSchema(
            plan_id_name="basic", 
            name="Basic Plan", 
            price=Decimal("9.99"), 
            currency="USD", 
            is_active=True
        )
        assert plan.plan_id_name == "basic"
        assert plan.name == "Basic Plan"
        assert plan.price == Decimal("9.99")
        assert plan.currency == "USD"
        assert plan.is_active is True
        assert plan.duration_days is None
        assert plan.features_description is None

    def test_billing_plan_base_schema_with_optional_fields(self):
        """Test billing plan base schema with optional fields"""
        plan = BillingPlanBaseSchema(
            plan_id_name="premium",
            name="Premium Plan",
            price=Decimal("19.99"),
            currency="EUR",
            duration_days=30,
            features_description="Premium features included",
            is_active=True
        )
        assert plan.duration_days == 30
        assert plan.features_description == "Premium features included"
        assert plan.currency == "EUR"

    def test_billing_plan_response_schema(self):
        """Test billing plan response schema"""
        plan = BillingPlanResponseSchema(
            id=1,
            plan_id_name="basic",
            name="Basic Plan",
            price=Decimal("9.99"),
            currency="USD",
            is_active=True
        )
        assert plan.id == 1
        assert plan.plan_id_name == "basic"

class TestSubscriptionSchemas:
    """Test subscription DTO schemas"""

    def test_subscription_create_request_schema_valid(self):
        """Test valid subscription create request schema"""
        request = SubscriptionCreateRequestSchema(
            user_email="test@example.com",
            plan_id_name="basic"
        )
        assert request.user_email == "test@example.com"
        assert request.plan_id_name == "basic"

    def test_subscription_create_request_schema_invalid_email(self):
        """Test subscription create request schema with invalid email"""
        with pytest.raises(ValidationError):
            SubscriptionCreateRequestSchema(
                user_email="invalid-email",
                plan_id_name="basic"
            )

    def test_subscription_base_schema(self):
        """Test subscription base schema"""
        now = datetime.now()
        subscription = SubscriptionBaseSchema(
            user_email="test@example.com",
            start_date=now,
            end_date=now,
            is_currently_active=True,
            payment_status="paid"
        )
        assert subscription.user_email == "test@example.com"
        assert subscription.start_date == now
        assert subscription.is_currently_active is True
        assert subscription.payment_status == "paid"

    def test_subscription_response_schema(self):
        """Test subscription response schema"""
        now = datetime.now()
        plan = BillingPlanResponseSchema(
            id=1, plan_id_name="basic", name="Basic Plan",
            price=Decimal("9.99"), currency="USD", is_active=True
        )
        subscription = SubscriptionResponseSchema(
            id=1,
            user_email="test@example.com",
            start_date=now,
            end_date=now,
            is_currently_active=True,
            payment_status="paid",
            plan=plan,
            created_at=now,
            updated_at=now
        )
        assert subscription.id == 1
        assert subscription.plan.plan_id_name == "basic"

    def test_user_subscription_status_response_schema(self):
        """Test user subscription status response schema"""
        now = datetime.now()
        status = UserSubscriptionStatusResponseSchema(
            user_email="test@example.com",
            plan_id_name="basic",
            plan_name="Basic Plan",
            is_active=True,
            start_date=now,
            end_date=now
        )
        assert status.user_email == "test@example.com"
        assert status.plan_id_name == "basic"
        assert status.is_active is True

    def test_user_subscription_status_response_schema_minimal(self):
        """Test user subscription status response schema with minimal data"""
        status = UserSubscriptionStatusResponseSchema(
            user_email="test@example.com"
        )
        assert status.user_email == "test@example.com"
        assert status.plan_id_name is None
        assert status.plan_name is None
        assert status.is_active is False
        assert status.start_date is None
        assert status.end_date is None

class TestBillingModels:
    """Test billing database models"""
    
    def test_billing_plan_model_repr(self):
        """Test billing plan model string representation"""
        # Test repr method directly 
        plan = MagicMock()
        plan.plan_id_name = "basic"
        plan.name = "Basic Plan"
        
        # Manually call the repr method
        result = BillingPlanModel.__repr__(plan)
        assert "basic" in result
        assert "Basic Plan" in result

    def test_subscription_model_repr(self):
        """Test subscription model string representation"""
        # Test repr method directly
        subscription = MagicMock()
        subscription.id = 1
        subscription.user_email = "test@example.com"
        subscription.billing_plan_id = 1
        subscription.is_currently_active = True
        
        # Manually call the repr method
        result = SubscriptionModel.__repr__(subscription)
        assert "test@example.com" in result
        assert "1" in result

class TestModelValidations:
    """Test model field validations and edge cases"""

    def test_negative_price_validation(self):
        """Test that negative prices are handled appropriately"""
        plan = BillingPlanBaseSchema(
            plan_id_name="basic",
            name="Basic Plan",
            price=Decimal("-9.99"),  # Negative price
            currency="USD",
            is_active=True
        )
        assert plan.price == Decimal("-9.99")

    def test_zero_price_validation(self):
        """Test zero price handling"""
        plan = BillingPlanBaseSchema(
            plan_id_name="free",
            name="Free Plan",
            price=Decimal("0.00"),
            currency="USD",
            is_active=True
        )
        assert plan.price == Decimal("0.00")

    def test_very_long_strings(self):
        """Test handling of very long strings"""
        long_name = "x" * 1000
        plan = BillingPlanBaseSchema(
            plan_id_name="basic",
            name=long_name,
            price=Decimal("9.99"),
            currency="USD",
            is_active=True
        )
        assert plan.name == long_name

    def test_special_characters_in_email(self):
        """Test email validation with valid special characters"""
        request = SubscriptionCreateRequestSchema(
            user_email="test+special@example.com",  # Should be valid
            plan_id_name="basic"
        )
        assert request.user_email == "test+special@example.com"
        
        # Test actually invalid email
        with pytest.raises(ValidationError):
            SubscriptionCreateRequestSchema(
                user_email="not-an-email",
                plan_id_name="basic"
            )

    def test_empty_string_validations(self):
        """Test empty string validations"""
        with pytest.raises(ValidationError):
            BillingPlanBaseSchema(
                plan_id_name="",  # Empty string
                name="Basic Plan",
                price=Decimal("9.99"),
                currency="USD",
                is_active=True
            )

    def test_currency_code_validation(self):
        """Test currency code validation"""
        # Test valid currency codes
        plan = BillingPlanBaseSchema(
            plan_id_name="basic",
            name="Basic Plan",
            price=Decimal("9.99"),
            currency="EUR",
            is_active=True
        )
        assert plan.currency == "EUR"

        # Test with longer currency code
        plan_invalid = BillingPlanBaseSchema(
            plan_id_name="basic",
            name="Basic Plan",
            price=Decimal("9.99"),
            currency="INVALID",  # Longer currency code
            is_active=True
        )
        assert plan_invalid.currency == "INVALID"

    def test_boolean_field_validation(self):
        """Test boolean field validation"""
        plan = BillingPlanBaseSchema(
            plan_id_name="basic",
            name="Basic Plan",
            price=Decimal("9.99"),
            currency="USD",
            is_active=False
        )
        assert plan.is_active is False

    def test_none_values_in_optional_fields(self):
        """Test None values in optional fields"""
        plan = BillingPlanBaseSchema(
            plan_id_name="basic",
            name="Basic Plan",
            price=Decimal("9.99"),
            currency="USD",
            duration_days=None,
            features_description=None,
            is_active=True
        )
        assert plan.duration_days is None
        assert plan.features_description is None

    def test_model_equality(self):
        """Test model equality comparisons"""
        plan1 = BillingPlanBaseSchema(
            plan_id_name="basic",
            name="Basic Plan",
            price=Decimal("9.99"),
            currency="USD",
            is_active=True
        )
        plan2 = BillingPlanBaseSchema(
            plan_id_name="basic",
            name="Basic Plan",
            price=Decimal("9.99"),
            currency="USD",
            is_active=True
        )
        assert plan1 == plan2

    def test_model_inequality(self):
        """Test model inequality comparisons"""
        plan1 = BillingPlanBaseSchema(
            plan_id_name="basic",
            name="Basic Plan",
            price=Decimal("9.99"),
            currency="USD",
            is_active=True
        )
        plan2 = BillingPlanBaseSchema(
            plan_id_name="premium",
            name="Premium Plan",
            price=Decimal("19.99"),
            currency="USD",
            is_active=True
        )
        assert plan1 != plan2
