from rest_framework.views import APIView, PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from apps.audit.models import ActivityLog
from apps.tasks.models import Task, TaskComment
from apps.workspaces.models import Membership
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from apps.workspaces.permissions import IsAdmin, IsMember, IsWorkspaceMember
from .models import Project
from .serializers import ProjectSerializer, TaskCommentSerializer, TaskSerializer
from rest_framework.generics import ListCreateAPIView, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

class ProjectListCreateAPIView(ListCreateAPIView):
    serializer_class = ProjectSerializer

    # Filter & Search
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["name"]
    search_fields = ["name", "description"]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), IsMember()]
        return [IsAuthenticated(), IsAdmin()]

    def get_queryset(self):
        return Project.objects.filter(
            workspace=self.request.workspace
        )

    def perform_create(self, serializer):
        serializer.save(workspace=self.request.workspace)
    


class TaskListCreateAPIView(ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMember]

    filter_backends = [DjangoFilterBackend,SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        return Task.objects.filter(
            project__id=self.kwargs["project_id"],
            project__workspace=self.request.workspace
        ).select_related("project", "assigned_to")

    def perform_create(self, serializer):
        project = get_object_or_404(
            Project,
            id=self.kwargs["project_id"],
            workspace=self.request.workspace
        )

        assigned_user = serializer.validated_data.get("assigned_to")

        membership = Membership.objects.get(
            user=self.request.user,
            workspace=self.request.workspace
        )

        if membership.role not in ["admin", "owner"]:
            if assigned_user and assigned_user != self.request.user:
                raise PermissionDenied(
                    "You can assign task only to yourself."
                )

        task = serializer.save(project=project)

        ActivityLog.objects.create(
            user=self.request.user,
            workspace=self.request.workspace,
            action="task_created",
            message=f"{self.request.user.email} created task '{task.title}'"
        )
 
    
class TaskCommentAPIView(ListCreateAPIView):
    serializer_class = TaskCommentSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["user"]
    search_fields = ["content"]

    def get_permissions(self):
        return [IsAuthenticated(), IsMember()]

    def get_queryset(self):
        return (
            TaskComment.objects.filter(
                task__id=self.kwargs["task_id"],
                task__project__workspace=self.request.workspace,
            )
            .select_related("user")
        )

    def perform_create(self, serializer):
        task = get_object_or_404(
            Task,
            id=self.kwargs["task_id"],
            project__workspace=self.request.workspace,
        )

        serializer.save(
            user=self.request.user,
            task=task,
        )

        ActivityLog.objects.create(
            user=self.request.user,
            workspace=self.request.workspace,
            action="comment_added",
            message=f"{self.request.user.email} commented on task '{task.title}'",
        )