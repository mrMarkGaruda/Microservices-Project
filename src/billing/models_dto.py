from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class BillingPlanBaseSchema(BaseModel):
    plan_id_name: str
    name: str
    price: Decimal
    currency: str
    duration_days: Optional[int] = None
    features_description: Optional[str] = None
    is_active: bool

class BillingPlanResponseSchema(BillingPlanBaseSchema):
    id: int
    class Config:
        orm_mode = True

class SubscriptionCreateRequestSchema(BaseModel):
    user_email: EmailStr
    plan_id_name: str

class SubscriptionBaseSchema(BaseModel):
    user_email: EmailStr
    start_date: datetime
    end_date: Optional[datetime] = None
    is_currently_active: bool
    payment_status: str

class SubscriptionResponseSchema(SubscriptionBaseSchema):
    id: int
    plan: BillingPlanResponseSchema
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class UserSubscriptionStatusResponseSchema(BaseModel):
    user_email: EmailStr
    plan_id_name: Optional[str] = None
    plan_name: Optional[str] = None
    is_active: bool = False
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
