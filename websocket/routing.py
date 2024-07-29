from django.urls import path
from websocket.consumers import ScanResultConsumer, AlertConsumer

websocket_urlpatterns = [
    path('ws/scan_results/', ScanResultConsumer.as_asgi()),
    path('ws/alerts/', AlertConsumer.as_asgi()),
]
