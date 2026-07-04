from django.urls import path
from .views import ProjectListCreateAPIView, TaskListCreateAPIView

urlpatterns = [
    path('projects/', ProjectListCreateAPIView.as_view()),
    path('projects/<int:project_id>/tasks/', TaskListCreateAPIView.as_view()),
]