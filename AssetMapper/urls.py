from django.urls import path
from .views import AssetMapperView

urlpatterns = [
    path('initiate/', AssetMapperView.as_view()),
]
