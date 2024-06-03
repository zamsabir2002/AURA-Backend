# consumers.py

from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
import json
import pika
from threading import Thread


class QueueConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        try:
            # Connect to RabbitMQ and start consuming messages
            print("Starting Connection......")
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='json_queue')
            self.channel.basic_consume(
                queue='json_queue',
                on_message_callback=self.receive_message,
                auto_ack=True
            )
            print("HERE")
            scan_thread = Thread(target=self.channel.start_consuming)
            print("HERE2")
            print(scan_thread)
            scan_thread.start()

            # self.channel.start_consuming()
            self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'You are connected!'
            }))
        except Exception as E:
            print("\n\n-----\n\n---------\n\n-----", E)
            self.send(text_data=json.dumps({
                'type': 'connection aborted',
                'message': 'Internal Server Error',
                'status_code': 500
            }))
            # self.close()

    def disconnect(self, close_code):
        # Close connection to RabbitMQ
        try:
            print("CLOSING1")
            self.connection.close()
            print("CLOSING")
            raise StopConsumer()
        except:
            print("CLOSING")
            raise StopConsumer()
        # raise StopConsumer()
        # finally:
        #     print("FINALLY")
        #     raise StopConsumer()

    def receive_message(self, ch, method, properties, body):
        # Process the message from RabbitMQ
        # print(body)
        message = body.decode('utf-8')
        message2 = json.loads(body.decode('utf-8'))
        print(message2)
        print(type(message2))
        # self.send(text_data=message)
        self.send(text_data=json.dumps(message2))

    def receive(self, text_data):
        # Handle WebSocket messages if needed
        pass
