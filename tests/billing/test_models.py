"""
Tests for billing.models_db and billing.models_dto
"""
from src.billing.models_dto import BillingPlanBaseSchema
from src.billing.models_db import BillingPlanModel

def test_billing_plan_schema():
    plan = BillingPlanBaseSchema(plan_id_name="basic", name="Basic", price=10, currency="USD", is_active=True)
    assert plan.plan_id_name == "basic"
    assert plan.name == "Basic"
    assert plan.price == 10
    assert plan.currency == "USD"
    assert plan.is_active is True

def test_billing_plan_model_repr():
    bpm = BillingPlanModel(plan_id_name="basic", name="Basic", price=10, currency="USD")
    assert "basic" in repr(bpm)

# Add more tests for all DTOs and models, including __repr__, __eq__, and edge cases.
