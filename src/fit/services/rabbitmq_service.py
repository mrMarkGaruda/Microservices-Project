import os
import pika
import json
import logging
from typing import Dict, Any
from pydantic import BaseModel 

from ..queue_messages import CreateWodMessage, WorkoutPerformedMessage 

logger = logging.getLogger(__name__)

logging.getLogger("pika").setLevel(logging.WARNING)

class RabbitMQService:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RabbitMQService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            self.connection = None
            self.channel = None
            self.create_wod_queue_name = "createWodQueue"
            self.workout_performed_exchange_name = "workout.performed" 
            self._is_initialized = True

    def ensure_connection(self):
        """Ensure connection is established"""
        if not self.connection or self.connection.is_closed:
            self.connect()

    def connect(self):
        """Establish connection to RabbitMQ server and declare queues/exchanges"""
        logger.debug("Attempting to connect to RabbitMQ")
        credentials = pika.PlainCredentials(
            username=os.getenv("RABBITMQ_DEFAULT_USER", "rabbit"),
            password=os.getenv("RABBITMQ_DEFAULT_PASS", "docker")
        )
        parameters = pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
            port=5672, 
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        try:
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self._declare_resources()
            logger.info("Successfully connected to RabbitMQ and declared resources.")
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}", exc_info=True)
            raise

    def _declare_resources(self):
        """Declare all necessary queues and exchanges."""
        if not self.channel or self.channel.is_closed:
            logger.error("Cannot declare resources, channel is not open.")
            return

        dlx_name = "dlx"
        dead_letter_routing_key_create_wod = f"{self.create_wod_queue_name}-dead"
        
        self.channel.exchange_declare(exchange=dlx_name, exchange_type="direct", durable=True)
        self.channel.queue_declare(queue=dead_letter_routing_key_create_wod, durable=True)
        self.channel.queue_bind(
            exchange=dlx_name,
            queue=dead_letter_routing_key_create_wod,
            routing_key=dead_letter_routing_key_create_wod
        )
        arguments_create_wod = {
            "x-message-ttl": 60000,  
            "x-max-length": 100,
            "x-dead-letter-exchange": dlx_name,
            "x-dead-letter-routing-key": dead_letter_routing_key_create_wod
        }
        self.channel.queue_declare(
            queue=self.create_wod_queue_name,
            durable=True,
            arguments=arguments_create_wod
        )
        logger.info(f"Declared queue '{self.create_wod_queue_name}' with DLX settings.")

        self.channel.exchange_declare(
            exchange=self.workout_performed_exchange_name,
            exchange_type="fanout",
            durable=True 
        )
        logger.info(f"Declared fanout exchange '{self.workout_performed_exchange_name}'.")


    def publish_create_wod_message(self, message: CreateWodMessage) -> bool:
        """Publish a message to the createWodQueue"""
        return self._publish(
            exchange_name="", 
            routing_key=self.create_wod_queue_name,
            message_model=message,
            description=f"create WOD for user {message.email}"
        )

    def publish_workout_performed_event(self, event: WorkoutPerformedMessage) -> bool:
        """Publish a WorkoutPerformedMessage to the fanout exchange."""
        return self._publish(
            exchange_name=self.workout_performed_exchange_name,
            routing_key="", 
            message_model=event,
            description=f"workout performed event for user {event.user_email}"
        )

    def _publish(self, exchange_name: str, routing_key: str, message_model: BaseModel, description: str) -> bool:
        """Generic publish method."""
        try:
            self.ensure_connection()

            message_data_dict = message_model.dict() 

            def convert_datetime_to_iso(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError("Type not serializable")

            message_body = json.dumps(message_data_dict, default=convert_datetime_to_iso)

            logger.debug(f"Publishing message to exchange '{exchange_name}', routing_key '{routing_key}': {message_body}")
            
            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE, 
                    content_type="application/json"
                )
            )
            logger.info(f"Successfully published {description}.")
            return True
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Connection error while publishing {description}: {e}", exc_info=True)
            self.connection = None 
            return False
        except Exception as e:
            logger.error(f"Failed to publish {description} to RabbitMQ: {e}", exc_info=True)
            return False

    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            logger.info("Closing RabbitMQ connection")
            try:
                self.connection.close()
            except Exception as e:
                logger.error(f"Error closing RabbitMQ connection: {e}", exc_info=True)
        self.connection = None
        self.channel = None

rabbitmq_service = RabbitMQService()