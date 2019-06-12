#!/usr/bin/python
import pika
import time

credentials = pika.PlainCredentials('admin','123456')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    '0.0.0.0',5672,'/',credentials
))
channel = connection.channel()

#channel.exchange_declare(exchange='Clogs', exchange_type='fanout')

# Declare queue, create if needed. This method creates or checks a queue. 
result = channel.queue_declare(queue='hello')

for i in range(1000000):
    channel.basic_publish(exchange='',
        routing_key='hello',
        body='hello word@{0}'.format(i))
    print("[X] send 'Hello World@{0}'".format(i))
    time.sleep(1)

connection.close()
