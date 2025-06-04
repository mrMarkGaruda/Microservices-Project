import pika
import json

RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'rabbit'
RABBITMQ_PASS = 'docker'
QUEUE_NAME = 'createWodQueue'
DLQ_NAME = 'createWodQueue.dlq'

def get_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    return pika.BlockingConnection(parameters)

def setup_queues():
    connection = get_connection()
    channel = connection.channel()

    # Dead letter queue
    channel.queue_declare(queue=DLQ_NAME, durable=True)

    # Main queue with TTL, max length, DLQ, etc.
    args = {
        'x-message-ttl': 60000,  # 1 minute
        'x-max-length': 100,
        'x-dead-letter-exchange': '',
        'x-dead-letter-routing-key': DLQ_NAME
    }
    channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments=args)
    connection.close()

def publish_message(message: dict):
    connection = get_connection()
    channel = connection.channel()
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()

def validate_message(msg):
    # Simple validation
    return isinstance(msg, dict) and 'email' in msg