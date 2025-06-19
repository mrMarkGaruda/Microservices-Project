# Import SQLAlchemy column types and relationship function
from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
# Import the declarative base from the database module
from database import Base
# Import datetime for default timestamps
import datetime

# Define the BillingPlanModel class for the billing_plans table
class BillingPlanModel(Base):
    __tablename__ = "billing_plans"  # Set the table name

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Primary key column
    plan_id_name = Column(String, unique=True, index=True, nullable=False)  # Unique plan identifier
    name = Column(String, nullable=False)  # Name of the plan
    price = Column(Numeric(10, 2), nullable=False)  # Price of the plan
    currency = Column(String(3), nullable=False, default="USD")  # Currency code
    duration_days = Column(Integer, nullable=True)  # Duration in days (nullable for free plans)
    features_description = Column(String, nullable=True)  # Description of plan features
    is_active = Column(Boolean, default=True, nullable=False)  # Whether the plan is active

    subscriptions = relationship("SubscriptionModel", back_populates="plan")  # Relationship to subscriptions

    def __repr__(self):
        # String representation for debugging
        return f"<BillingPlanModel(plan_id_name='{self.plan_id_name}', name='{self.name}')>"

# Define the SubscriptionModel class for the subscriptions table
class SubscriptionModel(Base):
    __tablename__ = "subscriptions"  # Set the table name

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Primary key column
    user_email = Column(String, index=True, nullable=False)  # Email of the user
    billing_plan_id = Column(Integer, ForeignKey("billing_plans.id"), nullable=False)  # Foreign key to billing plan
    
    start_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)  # Subscription start date
    end_date = Column(DateTime, nullable=True)  # Subscription end date (nullable)
    is_currently_active = Column(Boolean, default=True, nullable=False)  # Whether the subscription is active
    payment_status = Column(String, nullable=False, default="pending")  # Payment status

    created_at = Column(DateTime, default=datetime.datetime.utcnow)  # Creation timestamp
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)  # Update timestamp

    plan = relationship("BillingPlanModel", back_populates="subscriptions")  # Relationship to billing plan

    def __repr__(self):
        # String representation for debugging
        return f"<SubscriptionModel(id={self.id}, user_email='{self.user_email}', billing_plan_id='{self.billing_plan_id}', active='{self.is_currently_active}')>"
