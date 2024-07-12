import pika
import json


def publish_message(message, queue):

    with pika.BlockingConnection(pika.ConnectionParameters('localhost')) as connection:
        channel = connection.channel()

        channel.queue_declare(queue=queue)
        channel.basic_publish(exchange='',
                              routing_key=queue,
                              body=json.dumps(message).encode('utf-8'))
        #   body=json.dumps(message))
        print(" [x] Sent JSON object to queue")
