from django.urls import path
from .views import *

urlpatterns = [
    path('activity_logs/', ActivityLogAPIView.as_view())
]