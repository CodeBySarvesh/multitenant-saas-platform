from django.urls import path
from .views import *

urlpatterns = [
    path('test-workspace/', TestWorkspaceView.as_view()),
    path('test-workspace/custom_queryset/', TestWorkspaceDataView.as_view()),
]