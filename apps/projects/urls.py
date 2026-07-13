from django.urls import path
from .views import *

urlpatterns = [
    path('projects/', ProjectListCreateAPIView.as_view()),
    path('projects/<int:pk>/archive/', ProjectDeleteAPIView.as_view()),
    path('projects/<int:pk>/restore/', ProjectRestoreAPIView.as_view()),
    path('projects/<int:project_id>/tasks/', TaskListCreateAPIView.as_view()),
    path('projects/<int:task_id>/task_comment/', TaskCommentAPIView.as_view()),
    path('projects/<int:task_id>/task_attach/', TaskAttachmentAPIView.as_view()),
]