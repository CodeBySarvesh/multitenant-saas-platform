from rest_framework.views import APIView, PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from apps.audit.models import ActivityLog
from apps.tasks.models import Task, TaskComment
from apps.workspaces.models import Membership
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from apps.workspaces.permissions import IsAdmin, IsMember
from .models import Project
from .serializers import ProjectSerializer, TaskAttachmentSerializer, TaskCommentSerializer, TaskSerializer
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
    
class ProjectDeleteAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, pk):

        project = get_object_or_404(
            Project.all_objects.for_workspace(request.workspace),
            pk=pk
        )

        if project.is_deleted:
            return Response(
                {"detail": "Project is already archived."},
                status=status.HTTP_400_BAD_REQUEST
            )

        project.soft_delete()

        ActivityLog.objects.create(
            workspace=request.workspace,
            user=request.user,
            action="project_archived",
            message=f"{request.user.email} archived project '{project.name}'"
        )

        return Response(
            {"detail": "Project archived successfully."},
            status=status.HTTP_200_OK
        )

class ProjectRestoreAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):

        project = get_object_or_404(
            Project.all_objects.for_workspace(request.workspace),
            pk=pk
        )

        if not project.is_deleted:
            return Response(
                {"detail": "Project is already active."},
                status=status.HTTP_400_BAD_REQUEST
            )

        project.restore()

        ActivityLog.objects.create(
            workspace=request.workspace,
            user=request.user,
            action="project_restored",
            message=f"{request.user.email} restored project '{project.name}'"
        )

        return Response(
            {"detail": "Project restored successfully."},
            status=status.HTTP_200_OK
        )
# ---- Task-----
class TaskListCreateAPIView(ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMember]

    filter_backends = [DjangoFilterBackend,SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        return Task.objects.filter(
            project__id=self.kwargs["pk"],
            project__workspace=self.request.workspace
        ).select_related("project", "assigned_to")

    def perform_create(self, serializer):
        project = get_object_or_404(
            Project,
            id=self.kwargs["pk"],
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
 
class TaskDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, pk):

        task = get_object_or_404(
            Task.all_objects.for_workspace(request.workspace),
            pk=pk
        )

        if task.is_deleted:
            return Response(
                {"detail": "Task is already archived."},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.soft_delete()

        ActivityLog.objects.create(
            workspace=request.workspace,
            user=request.user,
            action="task_archived",
            message=f"{request.user.email} archived task '{task.title}'"
        )

        return Response(
            {"detail": "Task archived successfully."},
            status=status.HTTP_200_OK
        )
    
class TaskRestoreAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):

        task = get_object_or_404(
            Task.all_objects.for_workspace(request.workspace),
            pk=pk
        )

        if not task.is_deleted:
            return Response(
                {"detail": "Task is already active."},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.restore()

        ActivityLog.objects.create(
            workspace=request.workspace,
            user=request.user,
            action="task_restored",
            message=f"{request.user.email} restored task '{task.title}'"
        )

        return Response(
            {"detail": "Task restored successfully."},
            status=status.HTTP_200_OK
        )

# ---Task Comment---
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
                task__id=self.kwargs["pk"],
                task__project__workspace=self.request.workspace,
            )
            .select_related("user")
        )

    def perform_create(self, serializer):
        task = get_object_or_404(
            Task,
            id=self.kwargs["pk"],
            project__workspace=self.request.workspace,
        )

        serializer.save(
            user=self.request.user,
            task=task,
        )

        ActivityLog.objects.create(
            user=self.request.user,
            workspace=self.request.workspace,
            action="task_comment_created",
            message=f"{self.request.user.email} commented on task '{task.title}'",
        )

class TaskCommentDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, pk):

        comment = TaskComment.all_objects.filter(
            pk=pk
        ).first()

        if not comment:
            return Response(
                {"detail": "Task comment not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if comment.task.project.workspace != request.workspace:
            return Response(
                {"detail": "You do not have permission to access this task comment."},
                status=status.HTTP_403_FORBIDDEN
            )

        if comment.is_deleted:
            return Response(
                {"detail": "Task comment is already archived."},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment.soft_delete()

        ActivityLog.objects.create(
            workspace=request.workspace,
            user=request.user,
            action="task_comment_archived",
            message=f"{request.user.email} archived a comment on task '{comment.task.title}'"
        )

        return Response(
            {"detail": "Task comment archived successfully."},
            status=status.HTTP_200_OK
        )


class TaskCommentRestoreAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):

        comment = get_object_or_404(
            TaskComment.all_objects.for_workspace(request.workspace),
            pk=pk
        )

        if not comment.is_deleted:
            return Response(
                {"detail": "Task comment is already active."},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment.restore()

        ActivityLog.objects.create(
            workspace=request.workspace,
            user=request.user,
            action="task_comment_restored",
            message=f"{request.user.email} restored a comment on task '{comment.task.title}'"
        )

        return Response(
            {"detail": "Task comment restored successfully."},
            status=status.HTTP_200_OK
        )

# ---Task Attachment ---
class TaskAttachmentAPIView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), IsMember()]
    def post(self, request, task_id):
        try:
            task = Task.objects.get(
                id=task_id,
                project__workspace=request.workspace
            )
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)

        serializer = TaskAttachmentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(task=task, uploaded_by=request.user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)