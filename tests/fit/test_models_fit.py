"""
Tests for fit.models_db and fit.models_dto
"""
from src.fit.models_dto import UserSchema

def test_user_schema_validation():
    user = UserSchema(email="a@b.com", name="Test", role="user")
    assert user.email == "a@b.com"

# Add more tests for all DTOs and models
