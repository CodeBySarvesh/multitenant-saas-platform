from django.urls import path
from .views import *

urlpatterns = [
    path('workspace/list/test/', TestWorkspaceView.as_view()),
    path('workspace/create/', CreateWorkspaceView.as_view()),
    path('workspace/update/', WorkspaceUpdateAPIView.as_view()),
    path('workspace/', MyWorkspacesView.as_view()),
    path('workspace/details/', WorkspaceDetailAPIView.as_view()),
    path('workspace/project/', WorkspaceProjectsAPIView.as_view()),
    path('membership/create/', MembershipCreateAPIView.as_view()),
    path('membership/update/<int:pk>', MembershipUpdateAPIView.as_view()),
    path('membership/remove/<int:pk>', MembershipDeleteAPIView.as_view()),
    path('membership/', MembershipListAPIView.as_view()),
]