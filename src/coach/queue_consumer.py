import pika
import json
import random
import os
from .fitness_coach_service import request_wod

RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'rabbit'
RABBITMQ_PASS = 'docker'
QUEUE_NAME = 'createWodQueue'
DLQ_NAME = 'createWodQueue.dlq'

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        # Simulate 20% random failure
        if random.random() < 0.2:
            raise Exception("Random failure in WOD generation")
        # Generate and persist WOD for user
        user_email = message['email']
        request_wod(user_email)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        # Retry logic: check x-retries header
        retries = properties.headers.get('x-retries', 0) if properties.headers else 0
        if retries < 3:
            # Requeue with incremented retry count
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            ch.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=body,
                properties=pika.BasicProperties(
                    headers={'x-retries': retries + 1},
                    delivery_mode=2
                )
            )
        else:
            # Move to DLQ
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_consumer():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    print("Coach consumer started")
    channel.start_consuming()