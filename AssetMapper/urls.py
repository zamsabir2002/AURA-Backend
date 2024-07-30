from django.urls import path
from .views import AssetMapperView, AssetGet, UpdateAsset, GenerateAlerts

urlpatterns = [
    path('initiate/', AssetMapperView.as_view()),
    path('get_data/', AssetGet.as_view()),
    path('update_data/', UpdateAsset.as_view()),
    path('generate_alerts/', GenerateAlerts.as_view()),
]
