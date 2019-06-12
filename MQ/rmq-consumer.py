#!/usr/bin/python
import pika
import time

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

credentials = pika.PlainCredentials('admin','123456')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    '0.0.0.0',5672,'/',credentials
))
channel = connection.channel()
result = channel.queue_declare(queue='hello')
channel.basic_consume(queue='hello',
                      auto_ack=True,
                      on_message_callback=callback)
channel.start_consuming()
