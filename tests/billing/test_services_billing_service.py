"""
Unit tests for billing.services.billing_service
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.billing.services import billing_service
from src.billing.models_db import BillingPlanModel, SubscriptionModel
from src.billing.models_dto import (
    BillingPlanResponseSchema, 
    SubscriptionResponseSchema,
    UserSubscriptionStatusResponseSchema
)

class TestSeedInitialPlans:
    """Test seed_initial_plans function"""

    @patch("src.billing.services.billing_service.db_session")
    @patch("src.billing.services.billing_service.BillingPlanModel")
    def test_seed_initial_plans_success(self, mock_plan_model, mock_db_session):
        """Test successful seeding of initial plans"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.return_value.count.return_value = 0  # No existing plans
        
        billing_service.seed_initial_plans()
        
        # Should add plans and commit
        assert mock_db.add.call_count >= 1
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("src.billing.services.billing_service.db_session")
    @patch("src.billing.services.billing_service.BillingPlanModel")
    def test_seed_initial_plans_already_exists(self, mock_plan_model, mock_db_session):
        """Test seeding when plans already exist"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.return_value.count.return_value = 5  # Plans already exist
        
        billing_service.seed_initial_plans()
        
        # Should not add new plans
        mock_db.add.assert_not_called()
        mock_db.close.assert_called_once()

    @patch("src.billing.services.billing_service.db_session")
    def test_seed_initial_plans_exception(self, mock_db_session):
        """Test seeding with database exception"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.side_effect = Exception("Database error")
        
        # Should handle exception gracefully
        billing_service.seed_initial_plans()
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()

class TestGetAvailablePlans:
    """Test get_available_plans function"""

    @patch("src.billing.services.billing_service.db_session")
    @patch("src.billing.services.billing_service.BillingPlanModel")
    def test_get_available_plans_success(self, mock_plan_model, mock_db_session):
        """Test successful retrieval of available plans"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        # Mock plan data
        mock_plan = MagicMock()
        mock_plan.id = 1
        mock_plan.plan_id_name = "basic"
        mock_plan.name = "Basic Plan"
        mock_plan.price = Decimal("9.99")
        mock_plan.currency = "USD"
        mock_plan.is_active = True
        mock_plan.duration_days = 30
        mock_plan.features_description = "Basic features"
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_plan]
        
        result = billing_service.get_available_plans()
        
        assert len(result) == 1
        assert isinstance(result[0], BillingPlanResponseSchema)
        mock_db.close.assert_called_once()

    @patch("src.billing.services.billing_service.db_session")
    def test_get_available_plans_empty(self, mock_db_session):
        """Test retrieval when no plans available"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        result = billing_service.get_available_plans()
        
        assert result == []
        mock_db.close.assert_called_once()

    @patch("src.billing.services.billing_service.db_session")
    def test_get_available_plans_exception(self, mock_db_session):
        """Test retrieval with database exception"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            billing_service.get_available_plans()
        
        mock_db.close.assert_called_once()

class TestCreateSubscription:
    """Test create_subscription function"""

    @patch("src.billing.services.billing_service.db_session")
    @patch("src.billing.services.billing_service.BillingPlanModel")
    @patch("src.billing.services.billing_service.SubscriptionModel")
    def test_create_subscription_success(self, mock_subscription_model, mock_plan_model, mock_db_session):
        """Test successful subscription creation"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        # Mock plan lookup
        mock_plan = MagicMock()
        mock_plan.id = 1
        mock_plan.plan_id_name = "basic"
        mock_plan.name = "Basic Plan"
        mock_plan.price = Decimal("9.99")
        mock_plan.currency = "USD"
        mock_plan.is_active = True
        mock_plan.duration_days = 30
        mock_plan.features_description = "Basic features"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_plan
        
        # Mock subscription creation
        mock_subscription = MagicMock()
        mock_subscription.id = 1
        mock_subscription.user_email = "test@example.com"
        mock_subscription.start_date = datetime.now()
        mock_subscription.end_date = datetime.now() + timedelta(days=30)
        mock_subscription.is_currently_active = True
        mock_subscription.payment_status = "pending"
        mock_subscription.created_at = datetime.now()
        mock_subscription.updated_at = datetime.now()
        mock_subscription.plan = mock_plan
        
        mock_subscription_model.return_value = mock_subscription
        
        result = billing_service.create_subscription("test@example.com", "basic")
        
        assert result is not None
        assert isinstance(result, SubscriptionResponseSchema)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("src.billing.services.billing_service.db_session")
    def test_create_subscription_plan_not_found(self, mock_db_session):
        """Test subscription creation with non-existent plan"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = billing_service.create_subscription("test@example.com", "nonexistent")
        
        assert result is None
        mock_db.close.assert_called_once()

    @patch("src.billing.services.billing_service.db_session")
    def test_create_subscription_integrity_error(self, mock_db_session):
        """Test subscription creation with integrity error"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        # Mock plan lookup
        mock_plan = MagicMock()
        mock_plan.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_plan
        
        # Mock integrity error on commit
        mock_db.commit.side_effect = IntegrityError("duplicate", "params", "orig")
        
        result = billing_service.create_subscription("test@example.com", "basic")
        
        assert result is None
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("src.billing.services.billing_service.db_session")
    def test_create_subscription_general_exception(self, mock_db_session):
        """Test subscription creation with general exception"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.side_effect = Exception("Database error")
        
        result = billing_service.create_subscription("test@example.com", "basic")
        
        assert result is None
        mock_db.close.assert_called_once()

class TestGetUserSubscriptionStatus:
    """Test get_user_subscription_status function"""

    @patch("src.billing.services.billing_service.db_session")
    @patch("src.billing.services.billing_service.SubscriptionModel")
    def test_get_user_subscription_status_active(self, mock_subscription_model, mock_db_session):
        """Test getting user subscription status with active subscription"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        # Mock active subscription
        mock_subscription = MagicMock()
        mock_subscription.user_email = "test@example.com"
        mock_subscription.is_currently_active = True
        mock_subscription.start_date = datetime.now()
        mock_subscription.end_date = datetime.now() + timedelta(days=30)
        
        # Mock plan
        mock_plan = MagicMock()
        mock_plan.plan_id_name = "basic"
        mock_plan.name = "Basic Plan"
        mock_subscription.plan = mock_plan
        
        mock_db.query.return_value.join.return_value.filter.return_value.filter.return_value.first.return_value = mock_subscription
        
        result = billing_service.get_user_subscription_status("test@example.com")
        
        assert result is not None
        assert isinstance(result, UserSubscriptionStatusResponseSchema)
        assert result.user_email == "test@example.com"
        assert result.is_active is True
        mock_db.close.assert_called_once()

    @patch("src.billing.services.billing_service.db_session")
    def test_get_user_subscription_status_no_subscription(self, mock_db_session):
        """Test getting user subscription status with no subscription"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.return_value.join.return_value.filter.return_value.filter.return_value.first.return_value = None
        
        result = billing_service.get_user_subscription_status("test@example.com")
        
        assert result is not None
        assert isinstance(result, UserSubscriptionStatusResponseSchema)
        assert result.user_email == "test@example.com"
        assert result.is_active is False
        assert result.plan_id_name is None
        mock_db.close.assert_called_once()

    @patch("src.billing.services.billing_service.db_session")
    def test_get_user_subscription_status_exception(self, mock_db_session):
        """Test getting user subscription status with exception"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.side_effect = Exception("Database error")
        
        result = billing_service.get_user_subscription_status("test@example.com")
        
        assert result is None
        mock_db.close.assert_called_once()

class TestCancelSubscription:
    """Test cancel_subscription function"""

    @patch("src.billing.services.billing_service.db_session")
    @patch("src.billing.services.billing_service.SubscriptionModel")
    def test_cancel_subscription_success(self, mock_subscription_model, mock_db_session):
        """Test successful subscription cancellation"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        # Mock active subscription
        mock_subscription = MagicMock()
        mock_subscription.id = 1
        mock_subscription.user_email = "test@example.com"
        mock_subscription.is_currently_active = True
        mock_subscription.start_date = datetime.now()
        mock_subscription.end_date = datetime.now() + timedelta(days=30)
        mock_subscription.payment_status = "paid"
        mock_subscription.created_at = datetime.now()
        mock_subscription.updated_at = datetime.now()
        
        # Mock plan
        mock_plan = MagicMock()
        mock_plan.id = 1
        mock_plan.plan_id_name = "basic"
        mock_plan.name = "Basic Plan"
        mock_plan.price = Decimal("9.99")
        mock_plan.currency = "USD"
        mock_plan.is_active = True
        mock_plan.duration_days = 30
        mock_plan.features_description = "Basic features"
        mock_subscription.plan = mock_plan
        
        mock_db.query.return_value.join.return_value.filter.return_value.filter.return_value.first.return_value = mock_subscription
        
        result = billing_service.cancel_subscription("test@example.com")
        
        assert result is not None
        assert isinstance(result, SubscriptionResponseSchema)
        # Subscription should be marked as inactive
        assert mock_subscription.is_currently_active is False
        assert mock_subscription.payment_status == "cancelled"
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("src.billing.services.billing_service.db_session")
    def test_cancel_subscription_not_found(self, mock_db_session):
        """Test cancelling non-existent subscription"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.return_value.join.return_value.filter.return_value.filter.return_value.first.return_value = None
        
        result = billing_service.cancel_subscription("test@example.com")
        
        assert result is None
        mock_db.close.assert_called_once()

    @patch("src.billing.services.billing_service.db_session")
    def test_cancel_subscription_exception(self, mock_db_session):
        """Test cancelling subscription with exception"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        mock_db.query.side_effect = Exception("Database error")
        
        result = billing_service.cancel_subscription("test@example.com")
        
        assert result is None
        mock_db.close.assert_called_once()

class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios"""

    @patch("src.billing.services.billing_service.db_session")
    def test_database_connection_failure(self, mock_db_session):
        """Test handling of database connection failures"""
        mock_db_session.side_effect = Exception("Connection failed")
        
        # All functions should handle this gracefully
        result_plans = billing_service.get_available_plans()
        result_create = billing_service.create_subscription("test@example.com", "basic")
        result_status = billing_service.get_user_subscription_status("test@example.com")
        result_cancel = billing_service.cancel_subscription("test@example.com")
        
        # Should return appropriate default values
        assert result_plans == [] or result_plans is None
        assert result_create is None
        assert result_status is None
        assert result_cancel is None

    @patch("src.billing.services.billing_service.db_session")
    def test_memory_leak_prevention(self, mock_db_session):
        """Test that database sessions are properly closed"""
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        # Call each function
        try:
            billing_service.get_available_plans()
        except:
            pass
        
        try:
            billing_service.create_subscription("test@example.com", "basic")
        except:
            pass
        
        try:
            billing_service.get_user_subscription_status("test@example.com")
        except:
            pass
        
        try:
            billing_service.cancel_subscription("test@example.com")
        except:
            pass
        
        # Verify close is called for each function call
        assert mock_db.close.call_count >= 4

    def test_invalid_input_handling(self):
        """Test handling of invalid inputs"""
        # Test with None values
        result1 = billing_service.create_subscription(None, "basic")
        result2 = billing_service.create_subscription("test@example.com", None)
        result3 = billing_service.get_user_subscription_status(None)
        result4 = billing_service.cancel_subscription(None)
        
        # Should handle gracefully (actual behavior depends on implementation)
        # At minimum, should not crash
        assert True  # If we reach here, no exceptions were thrown

    def test_empty_string_handling(self):
        """Test handling of empty strings"""
        # Test with empty strings
        result1 = billing_service.create_subscription("", "basic")
        result2 = billing_service.create_subscription("test@example.com", "")
        result3 = billing_service.get_user_subscription_status("")
        result4 = billing_service.cancel_subscription("")
        
        # Should handle gracefully
        assert True  # If we reach here, no exceptions were thrown
