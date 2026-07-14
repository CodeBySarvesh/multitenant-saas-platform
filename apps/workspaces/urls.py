from django.urls import path
from .views import *

urlpatterns = [
    path('workspace/list/test/', TestWorkspaceView.as_view()),
    path('workspace/create/', CreateWorkspaceView.as_view()),
    path('workspace/', MyWorkspacesView.as_view()),
    path('workspace/details/', WorkspaceDetailAPIView.as_view()),
    path('workspace/project/', WorkspaceProjectsAPIView.as_view()),
]