from django.urls import path
from .views import AssetMapperView, AssetGet, UpdateAsset

urlpatterns = [
    path('initiate/', AssetMapperView.as_view()),
    path('get_data/', AssetGet.as_view()),
    path('update_data/', UpdateAsset.as_view()),
]
