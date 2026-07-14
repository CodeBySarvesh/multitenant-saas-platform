from django.urls import path
from .views import *

urlpatterns = [
    path('projects/', ProjectListCreateAPIView.as_view()),
    path('projects/<int:pk>/archive/', ProjectDeleteAPIView.as_view()),
    path('projects/<int:pk>/restore/', ProjectRestoreAPIView.as_view()),
    path('tasks/<int:pk>', TaskListCreateAPIView.as_view()),
    path('tasks/<int:pk>/archive/', TaskDeleteAPIView.as_view()),
    path('tasks/<int:pk>/restore/', TaskRestoreAPIView.as_view()),
    path('task_comment/<int:pk>', TaskCommentAPIView.as_view()),
    path('task_comment/<int:pk>/archive/', TaskCommentDeleteAPIView.as_view()),
    path('task_comment/<int:pk>/restore/', TaskCommentRestoreAPIView.as_view()),
    path('task_attach/<int:task_id>/', TaskAttachmentAPIView.as_view()),
]