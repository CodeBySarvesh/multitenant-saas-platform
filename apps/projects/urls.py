from django.urls import path
from .views import ProjectListCreateAPIView, TaskCommentAPIView, TaskListCreateAPIView

urlpatterns = [
    path('projects/', ProjectListCreateAPIView.as_view()),
    path('projects/<int:project_id>/tasks/', TaskListCreateAPIView.as_view()),
    path('projects/<int:task_id>/task_comment/', TaskCommentAPIView.as_view()),
]