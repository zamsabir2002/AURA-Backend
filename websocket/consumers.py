# consumers.py

from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
import json
import pika
from threading import Thread


class ScanResultConsumer(WebsocketConsumer):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.thread_id = None

    def connect(self):
        self.accept()
        try:
            # Connect to RabbitMQ and start consuming messages
            print("Starting Connection......")
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='result_queue')
            self.channel.basic_consume(
                # queue='json_queue',
                queue='result_queue',
                on_message_callback=self.receive_message,
                auto_ack=True
            )

            scan_thread = Thread(target=self.channel.start_consuming)

            print(scan_thread)
            scan_thread.start()

            # self.channel.start_consuming()
            # self.send(text_data=json.dumps({
            #     'type': 'connection_established',
            #     'message': 'You are connected!'
            # }))
        except Exception as E:
            print("\n\n-------------------", E)
            # self.send(text_data=json.dumps({
            #     'type': 'connection aborted',
            #     'message': 'Internal Server Error',
            #     'status_code': 500
            # }))
            # self.close()

    def disconnect(self, close_code):
        # Close connection to RabbitMQ
        try:
            self.connection.close()
            raise StopConsumer()
        except Exception as e:
            print("CLOSING" , e)
            raise StopConsumer()
        # raise StopConsumer()
        # finally:
        #     print("FINALLY")
        #     raise StopConsumer()

    def receive_message(self, ch, method, properties, body):

        # message in bytes hence decoding message
        # then passing to json.loads() to convert
        # to a python dictionary
        asset_data = json.loads(body.decode('utf-8'))

        # sending the data
        self.send(text_data=json.dumps(asset_data))

    def receive(self, text_data):
        # Handle WebSocket messages if needed
        pass

class AlertConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        try:
            # Connect to RabbitMQ and start consuming messages
            print("Starting Alert Connection......")
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='alert_queue')
            self.channel.basic_consume(
                queue='alert_queue',
                on_message_callback=self.receive_alert,
                auto_ack=True
            )

            alert_thread = Thread(target=self.channel.start_consuming)
            print(alert_thread)
            alert_thread.start()

        except Exception as e:
            print("\n\n-------------------", e)
            # self.send(text_data=json.dumps({
            #     'type': 'connection_aborted',
            #     'message': 'Internal Server Error',
            #     'status_code': 500
            # }))

    def disconnect(self, close_code):
        # Close connection to RabbitMQ
        try:
            self.connection.close()
            raise StopConsumer()
        except:
            print("CLOSING")
            raise StopConsumer()

    def receive_alert(self, ch, method, properties, body):
        # Decode message and send to WebSocket
        alert_data = json.loads(body.decode('utf-8'))
        self.send(text_data=json.dumps(alert_data))

    def receive(self, text_data):
        # Handle WebSocket messages if needed
        pass