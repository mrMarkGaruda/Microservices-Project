# Import BaseModel and EmailStr from pydantic for data validation
from pydantic import BaseModel, EmailStr
# Import List and Optional for type hinting
from typing import List, Optional
# Import datetime for date/time fields
from datetime import datetime
# Import Decimal for precise decimal values
from decimal import Decimal

# Define the base schema for a billing plan
class BillingPlanBaseSchema(BaseModel):
    plan_id_name: str  # Unique plan identifier
    name: str  # Name of the plan
    price: Decimal  # Price of the plan
    currency: str  # Currency code
    duration_days: Optional[int] = None  # Duration in days (optional)
    features_description: Optional[str] = None  # Description of plan features (optional)
    is_active: bool  # Whether the plan is active

# Define the response schema for a billing plan
class BillingPlanResponseSchema(BillingPlanBaseSchema):
    id: int  # ID of the plan
    class Config:
        orm_mode = True  # Enable ORM mode for Pydantic

# Define the schema for creating a subscription request
class SubscriptionCreateRequestSchema(BaseModel):
    user_email: EmailStr  # Email of the user
    plan_id_name: str  # Plan identifier

# Define the base schema for a subscription
class SubscriptionBaseSchema(BaseModel):
    user_email: EmailStr  # Email of the user
    start_date: datetime  # Start date of the subscription
    end_date: Optional[datetime] = None  # End date (optional)
    is_currently_active: bool  # Whether the subscription is active
    payment_status: str  # Payment status

# Define the response schema for a subscription
class SubscriptionResponseSchema(SubscriptionBaseSchema):
    id: int  # ID of the subscription
    plan: BillingPlanResponseSchema  # Associated billing plan
    created_at: datetime  # Creation timestamp
    updated_at: datetime  # Update timestamp
    class Config:
        orm_mode = True  # Enable ORM mode for Pydantic

# Define the response schema for a user's subscription status
class UserSubscriptionStatusResponseSchema(BaseModel):
    user_email: EmailStr  # Email of the user
    plan_id_name: Optional[str] = None  # Plan identifier (optional)
    plan_name: Optional[str] = None  # Plan name (optional)
    is_active: bool = False  # Whether the user has an active subscription
    start_date: Optional[datetime] = None  # Start date (optional)
    end_date: Optional[datetime] = None  # End date (optional)
