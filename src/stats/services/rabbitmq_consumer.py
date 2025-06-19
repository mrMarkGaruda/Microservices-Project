# Import pika for RabbitMQ communication
import pika
# Import os for environment variable access
import os
# Import json for JSON operations
import json
# Import logging for logging messages
import logging
# Import time for sleep operations
import time
# Import threading for thread safety
import threading
# Import sys for system path manipulation
import sys
# Add parent directory to sys.path for module imports
sys.path.append('..')
# Import ValidationError from pydantic for validation
from pydantic import ValidationError
# Import message schema for workout performed events
from queue_messages import WorkoutPerformedMessage
# Import the function to store workout stats
from services.stats_service import store_workout_stat

# Create a logger for this module
logger = logging.getLogger(__name__)
# Set pika logging to warning level
logging.getLogger("pika").setLevel(logging.WARNING)

# Define the RabbitMQ consumer class for stats
class StatsRabbitMQConsumer:
    def __init__(self):
        # Get RabbitMQ connection details from environment variables
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "rabbit")
        self.rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS", "docker")
        self.exchange_name = "workout.performed"  # Exchange name
        self.queue_name = "stats_service_workout_events_queue"  # Queue name
        self.connection = None  # RabbitMQ connection
        self.channel = None  # RabbitMQ channel
        self._is_consuming = False  # Consumer state

    def _connect(self):
        # Log connection attempt
        logger.info(f"Attempting to connect to RabbitMQ at {self.rabbitmq_host}...")
        # Create credentials for RabbitMQ
        credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
        # Set connection parameters
        parameters = pika.ConnectionParameters(
            host=self.rabbitmq_host,
            port=5672,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        try:
            # Attempt to create a blocking connection
            self.connection = pika.BlockingConnection(parameters)
            # Create a channel from the connection
            self.channel = self.connection.channel()
            logger.info("Successfully connected to RabbitMQ.")
            return True
        except pika.exceptions.AMQPConnectionError as e:
            # Log connection error
            logger.error(f"Failed to connect to RabbitMQ: {e}", exc_info=False)
            return False

    def _setup_consumer(self):
        # Ensure the channel is open before setup
        if not self.channel or self.channel.is_closed:
            logger.error("Cannot setup consumer, channel is not open.")
            return False
        try:
            # Declare the exchange for workout events
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type="fanout",
                durable=True
            )
            logger.info(f"Exchange '{self.exchange_name}' declared.")
            # Declare the queue for the stats service
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            logger.info(f"Queue '{self.queue_name}' declared.")
            # Bind the queue to the exchange
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name
            )
            logger.info(f"Queue '{self.queue_name}' bound to exchange '{self.exchange_name}'.")
            # Set prefetch count for fair dispatch
            self.channel.basic_qos(prefetch_count=1)
            return True
        except Exception as e:
            # Log any setup errors
            logger.error(f"Error setting up RabbitMQ consumer resources: {e}", exc_info=True)
            return False

    def _on_message_callback(self, ch, method, properties, body):
        # Log the received message
        logger.debug(f"Received message: {body[:200]}...")
        try:
            # Decode the message body
            message_data_str = body.decode('utf-8')
            # Validate and parse the message as a WorkoutPerformedMessage
            message_obj = WorkoutPerformedMessage.model_validate_json(message_data_str)
            logger.info(f"Processing WorkoutPerformedMessage for user: {message_obj.user_email}, workout_id: {message_obj.workout_id}")
            # Store the workout stat in the database
            store_workout_stat(message_obj)
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug(f"Message acknowledged: {method.delivery_tag}")
        except ValidationError as ve:
            # Log validation errors and reject the message
            logger.error(f"Message validation failed: {ve.errors()}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            # Log any other errors and reject the message
            logger.error(f"Error processing message: {e}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start_consuming(self):
        # Set the consumer state to active
        self._is_consuming = True
        logger.info("Consumer loop started. Waiting for messages...")
        while self._is_consuming:
            # Reconnect if the connection is closed
            if not self.connection or self.connection.is_closed:
                if not self._connect():
                    logger.info("Connection failed, retrying in 5 seconds...")
                    time.sleep(5)
                    continue
            # Recreate the channel if needed
            if not self.channel or self.channel.is_closed:
                if self.connection and not self.connection.is_closed:
                    self.channel = self.connection.channel()
                else:
                    logger.error("Connection is closed, cannot create channel. Retrying connection.")
                    self.connection = None
                    time.sleep(5)
                    continue
            # Setup the consumer resources
            if not self._setup_consumer():
                logger.info("Setup failed, retrying in 5 seconds...")
                if self.connection and not self.connection.is_closed:
                    try:
                        self.connection.close()
                    except Exception as e_close:
                        logger.error(f"Error closing connection during setup retry: {e_close}")
                self.connection = None
                self.channel = None
                time.sleep(5)
                continue
            try:
                # Start consuming messages from the queue
                self.channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=self._on_message_callback,
                    auto_ack=False
                )
                logger.info(f"Consumer started on queue '{self.queue_name}'. Waiting for messages.")
                self.channel.start_consuming()
            except pika.exceptions.StreamLostError as sle:
                # Log stream lost errors and reconnect
                logger.error(f"RabbitMQ StreamLostError: {sle}. Reconnecting...", exc_info=False)
                self._close_connection()
            except pika.exceptions.AMQPConnectionError as ace:
                # Log AMQP connection errors and reconnect
                logger.error(f"RabbitMQ AMQPConnectionError: {ace}. Reconnecting...", exc_info=False)
                self._close_connection()
            except Exception as e:
                # Log any other errors and reconnect
                logger.error(f"Unexpected error in consumer loop: {e}", exc_info=True)
                self._close_connection()
                time.sleep(5)
            # Break the loop if consuming is stopped
            if not self._is_consuming:
                break
            logger.info("Consumer loop restarting due to connection issue or graceful stop of start_consuming().")
            time.sleep(5)
        logger.info("Consumer has stopped.")
        self._close_connection()

    def _close_connection(self):
        # Close the channel if open
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
                logger.info("RabbitMQ channel closed.")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ channel: {e}", exc_info=True)
        # Close the connection if open
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
                logger.info("RabbitMQ connection closed.")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}", exc_info=True)
        self.channel = None
        self.connection = None

    def stop_consuming(self):
        # Request to stop consuming messages
        logger.info("Stop consuming requested.")
        self._is_consuming = False
        if self.channel and self.channel.is_open and self.channel.is_consuming:
            try:
                self.channel.stop_consuming()
                logger.info("RabbitMQ channel stop_consuming called.")
            except Exception as e:
                logger.error(f"Error calling stop_consuming on channel: {e}", exc_info=True)

# Global consumer instance and lock for thread safety
_consumer_instance = None
_consumer_lock = threading.Lock()

# Function to get the singleton consumer instance
def get_consumer_instance():
    global _consumer_instance
    with _consumer_lock:
        if _consumer_instance is None:
            _consumer_instance = StatsRabbitMQConsumer()
    return _consumer_instance

# Function to run the consumer in a thread
def run_consumer():
    consumer = get_consumer_instance()
    try:
        logger.info("Starting StatsRabbitMQConsumer...")
        consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Stopping consumer...")
    except Exception as e:
        logger.error(f"Unhandled exception in run_consumer: {e}", exc_info=True)
    finally:
        logger.info("Consumer process is shutting down.")
        consumer.stop_consuming()
