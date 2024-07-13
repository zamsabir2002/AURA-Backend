from django.urls import path
from .consumers import ScanResultConsumer

websocket_urlpatterns = [
    path('ws/scan_results/', ScanResultConsumer.as_asgi()),
    # path('ws/alerts/', QueueConsumer.as_asgi()),
]
