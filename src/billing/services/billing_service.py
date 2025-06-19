# Import the logging module for logging messages
import logging
# Import List and Optional types for type hinting
from typing import List, Optional
# Import datetime and timedelta for date/time operations
from datetime import datetime, timedelta
# Import IntegrityError exception from SQLAlchemy
from sqlalchemy.exc import IntegrityError
# Import the database session from the database module
from database import db_session
# Import the BillingPlanModel and SubscriptionModel from models_db
from models_db import BillingPlanModel, SubscriptionModel
# Import various schema classes from models_dto for request/response validation
from models_dto import (
    BillingPlanResponseSchema,
    SubscriptionResponseSchema,
    UserSubscriptionStatusResponseSchema,
    SubscriptionCreateRequestSchema
)
# Import Decimal for precise decimal arithmetic
from decimal import Decimal

# Create a logger for this module
logger = logging.getLogger(__name__)

# Function to seed initial billing plans into the database
def seed_initial_plans():
    # Create a new database session
    session = db_session()
    try:
        # Define a list of default billing plans
        default_plans = [
            {"plan_id_name": "free", "name": "Free Tier", "price": Decimal("0.00"), "currency": "USD", "duration_days": None, "features_description": "Basic access, 3 exercises per workout.", "is_active": True},
            {"plan_id_name": "premium_monthly", "name": "Premium Monthly", "price": Decimal("9.99"), "currency": "USD", "duration_days": 30, "features_description": "Full access, 9 exercises per workout, advanced stats.", "is_active": True},
            {"plan_id_name": "premium_yearly", "name": "Premium Yearly", "price": Decimal("99.99"), "currency": "USD", "duration_days": 365, "features_description": "Full access, 9 exercises per workout, advanced stats, yearly discount.", "is_active": True}
        ]
        # Iterate over each plan in the default_plans list
        for plan_data in default_plans:
            # Check if the plan already exists in the database
            exists = session.query(BillingPlanModel).filter_by(plan_id_name=plan_data["plan_id_name"]).first()
            # If the plan does not exist, add it to the session
            if not exists:
                plan = BillingPlanModel(**plan_data)
                session.add(plan)
        # Commit the session to save changes
        session.commit()
    except Exception as e:
        # Log any errors and roll back the session
        logger.error(f"Error seeding billing plans: {e}", exc_info=True)
        session.rollback()
    finally:
        # Close the session
        session.close()

# Function to get all available billing plans
def get_available_plans() -> List[BillingPlanResponseSchema]:
    # Create a new database session
    session = db_session()
    try:
        # Query all active billing plans
        plans = session.query(BillingPlanModel).filter(BillingPlanModel.is_active == True).all()
        # Convert each plan to a response schema and return the list
        return [BillingPlanResponseSchema.from_orm(plan) for plan in plans]
    finally:
        # Close the session
        session.close()

# Function to create a new subscription for a user
def create_subscription(user_email: str, plan_id_name: str) -> Optional[SubscriptionResponseSchema]:
    # Create a new database session
    session = db_session()
    try:
        # Query the plan by plan_id_name and check if it is active
        plan = session.query(BillingPlanModel).filter(BillingPlanModel.plan_id_name == plan_id_name, BillingPlanModel.is_active == True).first()
        # If the plan does not exist, return None
        if not plan:
            return None
        # Check if the user already has an active subscription
        existing_active_subscription = session.query(SubscriptionModel).filter(
            SubscriptionModel.user_email == user_email,
            SubscriptionModel.is_currently_active == True,
            (SubscriptionModel.end_date == None) | (SubscriptionModel.end_date > datetime.utcnow())
        ).first()
        # If an active subscription exists, return None
        if existing_active_subscription:
            return None
        # Set the start date to now
        start_date = datetime.utcnow()
        # Initialize end_date as None
        end_date = None
        # If the plan has a duration, calculate the end date
        if plan.duration_days:
            end_date = start_date + timedelta(days=plan.duration_days)
        # Create a new SubscriptionModel instance
        new_subscription = SubscriptionModel(
            user_email=user_email,
            billing_plan_id=plan.id,
            start_date=start_date,
            end_date=end_date,
            is_currently_active=True,
            payment_status="paid"
        )
        # Add the new subscription to the session
        session.add(new_subscription)
        # Commit the session to save the subscription
        session.commit()
        # Refresh the subscription instance from the database
        session.refresh(new_subscription)
        # Return the subscription as a response schema
        return SubscriptionResponseSchema.from_orm(new_subscription)
    except IntegrityError:
        # Roll back the session if there is an integrity error
        session.rollback()
        return None
    except Exception as e:
        # Log any other errors, roll back, and return None
        logger.error(f"Error creating subscription for user '{user_email}' to plan '{plan_id_name}': {e}", exc_info=True)
        session.rollback()
        return None
    finally:
        # Close the session
        session.close()

# Function to get the subscription status for a user
def get_user_subscription_status(user_email: str) -> UserSubscriptionStatusResponseSchema:
    # Create a new database session
    session = db_session()
    try:
        # Query the most recent active subscription for the user
        subscription = session.query(SubscriptionModel).join(BillingPlanModel).filter(
            SubscriptionModel.user_email == user_email,
            SubscriptionModel.is_currently_active == True,
            (SubscriptionModel.end_date == None) | (SubscriptionModel.end_date > datetime.utcnow())
        ).order_by(SubscriptionModel.created_at.desc()).first()
        # If a subscription is found, return its status
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
            # If no subscription is found, return inactive status
            return UserSubscriptionStatusResponseSchema(user_email=user_email, is_active=False)
    finally:
        # Close the session
        session.close()

# Function to cancel a user's active subscription
def cancel_subscription(user_email: str) -> Optional[SubscriptionResponseSchema]:
    # Create a new database session
    session = db_session()
    try:
        # Query the user's active subscription
        subscription = session.query(SubscriptionModel).filter(
            SubscriptionModel.user_email == user_email,
            SubscriptionModel.is_currently_active == True,
            (SubscriptionModel.end_date == None) | (SubscriptionModel.end_date > datetime.utcnow())
        ).first()
        # If no active subscription is found, return None
        if not subscription:
            return None
        # Set the subscription as inactive
        subscription.is_currently_active = False
        # Set the end date to now
        subscription.end_date = datetime.utcnow()
        # Set the payment status to cancelled
        subscription.payment_status = "cancelled"
        # Commit the session to save changes
        session.commit()
        # Refresh the subscription instance from the database
        session.refresh(subscription)
        # Return the cancelled subscription as a response schema
        return SubscriptionResponseSchema.from_orm(subscription)
    except Exception as e:
        # Log any errors, roll back, and return None
        logger.error(f"Error cancelling subscription for user '{user_email}': {e}", exc_info=True)
        session.rollback()
        return None
    finally:
        # Close the session
        session.close()
