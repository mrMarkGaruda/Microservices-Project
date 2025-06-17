import pika
import os
import json
import logging
import time
from pydantic import ValidationError
from ..queue_messages import WorkoutPerformedMessage # Message schema from stats service
from .stats_service import store_workout_stat # Service function to store data (M will complete)

logger = logging.getLogger(__name__)

# Disable pika's verbose logging if desired, or set to WARNING
logging.getLogger("pika").setLevel(logging.WARNING)

class StatsRabbitMQConsumer:
    def __init__(self):
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "rabbit")
        self.rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS", "docker")
        
        self.exchange_name = "workout.performed"
        self.queue_name = "stats_service_workout_events_queue" # Durable queue for stats service
        
        self.connection = None
        self.channel = None
        self._is_consuming = False

    def _connect(self):
        logger.info(f"Attempting to connect to RabbitMQ at {self.rabbitmq_host}...")
        credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
        parameters = pika.ConnectionParameters(
            host=self.rabbitmq_host,
            port=5672,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        try:
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Successfully connected to RabbitMQ.")
            return True
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}", exc_info=False) # exc_info=False to avoid spamming logs on retries
            return False

    def _setup_consumer(self):
        if not self.channel or self.channel.is_closed:
            logger.error("Cannot setup consumer, channel is not open.")
            return False

        try:
            # Declare the fanout exchange (durable, idempotent)
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type="fanout",
                durable=True
            )
            logger.info(f"Exchange '{self.exchange_name}' declared.")

            # Declare a durable queue for the stats service
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True # Ensure messages persist server restarts
            )
            logger.info(f"Queue '{self.queue_name}' declared.")

            # Bind the queue to the exchange
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name
                # routing_key is ignored for fanout exchanges, but pika might require empty string
            )
            logger.info(f"Queue '{self.queue_name}' bound to exchange '{self.exchange_name}'.")
            
            # Set prefetch count to 1 to ensure messages are processed one by one by this consumer instance
            # This helps if processing is resource-intensive or if order matters strictly for a single consumer.
            # For multiple consumer instances, this means each gets one message at a time.
            self.channel.basic_qos(prefetch_count=1)
            return True
        except Exception as e:
            logger.error(f"Error setting up RabbitMQ consumer resources: {e}", exc_info=True)
            return False

    def _on_message_callback(self, ch, method, properties, body):
        logger.debug(f"Received message: {body[:200]}...") # Log snippet of body
        try:
            message_data_str = body.decode('utf-8')
            # Pydantic V1: model_validate_json, Pydantic V2: model_validate_json
            message_obj = WorkoutPerformedMessage.model_validate_json(message_data_str)
            
            logger.info(f"Processing WorkoutPerformedMessage for user: {message_obj.user_email}, workout_id: {message_obj.workout_id}")
            
            # Call the service function to store the workout stat
            # This function will be fully implemented by Member M
            store_workout_stat(message_obj) 
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug(f"Message acknowledged: {method.delivery_tag}")

        except ValidationError as ve:
            logger.error(f"Message validation failed: {ve.errors()}", exc_info=True)
            # Decide whether to nack and requeue, or move to DLQ, or discard
            # For now, nack without requeue to avoid poison pill loop if message is malformed
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            # Nack and potentially requeue, or implement a retry mechanism with delay
            # For simplicity, nack without requeue. Consider a DLQ for persistent errors.
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False) # requeue=True could lead to loop

    def start_consuming(self):
        self._is_consuming = True
        logger.info("Consumer loop started. Waiting for messages...")
        while self._is_consuming:
            if not self.connection or self.connection.is_closed:
                if not self._connect():
                    logger.info("Connection failed, retrying in 5 seconds...")
                    time.sleep(5)
                    continue # Retry connection
            
            if not self.channel or self.channel.is_closed: # Should be recreated if connection was remade
                if self.connection and not self.connection.is_closed:
                    self.channel = self.connection.channel()
                else: # Should not happen if _connect succeeded
                    logger.error("Connection is closed, cannot create channel. Retrying connection.")
                    self.connection = None # Force reconnect
                    time.sleep(5)
                    continue


            if not self._setup_consumer(): # Idempotent setup
                logger.info("Setup failed, retrying in 5 seconds...")
                # If setup fails, connection might be an issue, close and retry
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
                self.channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=self._on_message_callback,
                    auto_ack=False # We will manually acknowledge
                )
                logger.info(f"Consumer started on queue '{self.queue_name}'. Waiting for messages.")
                self.channel.start_consuming() # Blocking call
            except pika.exceptions.StreamLostError as sle:
                logger.error(f"RabbitMQ StreamLostError: {sle}. Reconnecting...", exc_info=False)
                self._close_connection() # Ensure clean close
            except pika.exceptions.AMQPConnectionError as ace:
                logger.error(f"RabbitMQ AMQPConnectionError: {ace}. Reconnecting...", exc_info=False)
                self._close_connection()
            except Exception as e:
                logger.error(f"Unexpected error in consumer loop: {e}", exc_info=True)
                self._close_connection()
                time.sleep(5) # Wait before retrying the whole loop
            
            if not self._is_consuming: # Check if stop was requested
                break
            logger.info("Consumer loop restarting due to connection issue or graceful stop of start_consuming().")
            time.sleep(5) # Wait before attempting to reconnect and consume

        logger.info("Consumer has stopped.")
        self._close_connection()

    def _close_connection(self):
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
                logger.info("RabbitMQ channel closed.")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ channel: {e}", exc_info=True)
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
                logger.info("RabbitMQ connection closed.")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}", exc_info=True)
        self.channel = None
        self.connection = None

    def stop_consuming(self):
        logger.info("Stop consuming requested.")
        self._is_consuming = False
        if self.channel and self.channel.is_open and self.channel.is_consuming:
            try:
                self.channel.stop_consuming() # This will break the blocking start_consuming() loop
                logger.info("RabbitMQ channel stop_consuming called.")
            except Exception as e:
                logger.error(f"Error calling stop_consuming on channel: {e}", exc_info=True)
        # The main loop in start_consuming will then exit.

_consumer_instance = None
_consumer_lock = threading.Lock()

def get_consumer_instance():
    global _consumer_instance
    with _consumer_lock:
        if _consumer_instance is None:
            _consumer_instance = StatsRabbitMQConsumer()
    return _consumer_instance

def run_consumer():
    """Entry point to start the consumer."""
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

# Example of how to stop it if needed from another thread (e.g., on app shutdown)
# def shutdown_consumer():
#     consumer = get_consumer_instance()
#     consumer.stop_consuming()
