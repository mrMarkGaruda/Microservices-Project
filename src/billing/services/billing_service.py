import logging
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from ..database import db_session
from ..models_db import BillingPlanModel, SubscriptionModel
from ..models_dto import (
    BillingPlanResponseSchema,
    SubscriptionResponseSchema,
    UserSubscriptionStatusResponseSchema,
    SubscriptionCreateRequestSchema
)
from decimal import Decimal

logger = logging.getLogger(__name__)

def seed_initial_plans():
    session = db_session()
    try:
        default_plans = [
            {"plan_id_name": "free", "name": "Free Tier", "price": Decimal("0.00"), "currency": "USD", "duration_days": None, "features_description": "Basic access, 3 exercises per workout.", "is_active": True},
            {"plan_id_name": "premium_monthly", "name": "Premium Monthly", "price": Decimal("9.99"), "currency": "USD", "duration_days": 30, "features_description": "Full access, 9 exercises per workout, advanced stats.", "is_active": True},
            {"plan_id_name": "premium_yearly", "name": "Premium Yearly", "price": Decimal("99.99"), "currency": "USD", "duration_days": 365, "features_description": "Full access, 9 exercises per workout, advanced stats, yearly discount.", "is_active": True}
        ]
        for plan_data in default_plans:
            exists = session.query(BillingPlanModel).filter_by(plan_id_name=plan_data["plan_id_name"]).first()
            if not exists:
                plan = BillingPlanModel(**plan_data)
                session.add(plan)
        session.commit()
    except Exception as e:
        logger.error(f"Error seeding billing plans: {e}", exc_info=True)
        session.rollback()
    finally:
        session.close()

def get_available_plans() -> List[BillingPlanResponseSchema]:
    session = db_session()
    try:
        plans = session.query(BillingPlanModel).filter(BillingPlanModel.is_active == True).all()
        return [BillingPlanResponseSchema.from_orm(plan) for plan in plans]
    finally:
        session.close()

def create_subscription(user_email: str, plan_id_name: str) -> Optional[SubscriptionResponseSchema]:
    session = db_session()
    try:
        plan = session.query(BillingPlanModel).filter(BillingPlanModel.plan_id_name == plan_id_name, BillingPlanModel.is_active == True).first()
        if not plan:
            return None
        existing_active_subscription = session.query(SubscriptionModel).filter(
            SubscriptionModel.user_email == user_email,
            SubscriptionModel.is_currently_active == True,
            (SubscriptionModel.end_date == None) | (SubscriptionModel.end_date > datetime.utcnow())
        ).first()
        if existing_active_subscription:
            return None
        start_date = datetime.utcnow()
        end_date = None
        if plan.duration_days:
            end_date = start_date + timedelta(days=plan.duration_days)
        new_subscription = SubscriptionModel(
            user_email=user_email,
            billing_plan_id=plan.id,
            start_date=start_date,
            end_date=end_date,
            is_currently_active=True,
            payment_status="paid"
        )
        session.add(new_subscription)
        session.commit()
        session.refresh(new_subscription)
        return SubscriptionResponseSchema.from_orm(new_subscription)
    except IntegrityError:
        session.rollback()
        return None
    except Exception as e:
        logger.error(f"Error creating subscription for user '{user_email}' to plan '{plan_id_name}': {e}", exc_info=True)
        session.rollback()
        return None
    finally:
        session.close()

def get_user_subscription_status(user_email: str) -> UserSubscriptionStatusResponseSchema:
    session = db_session()
    try:
        subscription = session.query(SubscriptionModel).join(BillingPlanModel).filter(
            SubscriptionModel.user_email == user_email,
            SubscriptionModel.is_currently_active == True,
            (SubscriptionModel.end_date == None) | (SubscriptionModel.end_date > datetime.utcnow())
        ).order_by(SubscriptionModel.created_at.desc()).first()
        if subscription:
            return UserSubscriptionStatusResponseSchema(
                user_email=subscription.user_email,
                plan_id_name=subscription.plan.plan_id_name,
                plan_name=subscription.plan.name,
                is_active=True,
                start_date=subscription.start_date,
                end_date=subscription.end_date
            )
        else:
            return UserSubscriptionStatusResponseSchema(user_email=user_email, is_active=False)
    finally:
        session.close()

def cancel_subscription(user_email: str) -> Optional[SubscriptionResponseSchema]:
    session = db_session()
    try:
        subscription = session.query(SubscriptionModel).filter(
            SubscriptionModel.user_email == user_email,
            SubscriptionModel.is_currently_active == True,
            (SubscriptionModel.end_date == None) | (SubscriptionModel.end_date > datetime.utcnow())
        ).first()
        if not subscription:
            return None
        subscription.is_currently_active = False
        subscription.end_date = datetime.utcnow()
        subscription.payment_status = "cancelled"
        session.commit()
        session.refresh(subscription)
        return SubscriptionResponseSchema.from_orm(subscription)
    except Exception as e:
        logger.error(f"Error cancelling subscription for user '{user_email}': {e}", exc_info=True)
        session.rollback()
        return None
    finally:
        session.close()
