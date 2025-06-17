from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from database import Base
import datetime

class BillingPlanModel(Base):
    __tablename__ = "billing_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id_name = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    duration_days = Column(Integer, nullable=True)
    features_description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    subscriptions = relationship("SubscriptionModel", back_populates="plan")

    def __repr__(self):
        return f"<BillingPlanModel(plan_id_name='{self.plan_id_name}', name='{self.name}')>"

class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_email = Column(String, index=True, nullable=False)
    billing_plan_id = Column(Integer, ForeignKey("billing_plans.id"), nullable=False)
    
    start_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    is_currently_active = Column(Boolean, default=True, nullable=False)
    payment_status = Column(String, nullable=False, default="pending")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    plan = relationship("BillingPlanModel", back_populates="subscriptions")

    def __repr__(self):
        return f"<SubscriptionModel(id={self.id}, user_email='{self.user_email}', billing_plan_id='{self.billing_plan_id}', active='{self.is_currently_active}')>"
