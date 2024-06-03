from django.urls import path
from .views import AssetIdentifierView

urlpatterns = [
    path('initiate/', AssetIdentifierView.as_view()),
]
