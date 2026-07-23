from rest_framework.views import APIView, PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from apps.audit.models import ActivityLog
from apps.common.docs import WORKSPACE_HEADER
from apps.tasks.models import Task, TaskComment
from apps.workspaces.models import Membership
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from apps.workspaces.permissions import IsAdmin, IsMember
from .models import Project
from apps.common.serializers import MessageSerializer
from .serializers import ProjectSerializer, TaskAttachmentCreateSerializer, TaskAttachmentSerializer, TaskCommentSerializer, TaskSerializer
from rest_framework.generics import ListCreateAPIView, UpdateAPIView, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from apps.notifications.tasks import send_task_assignment_email_task
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import (extend_schema,OpenApiParameter,OpenApiTypes)

@extend_schema_view(
    get=extend_schema(
        summary="List projects",
        description="Retrieve all projects in the current workspace.",
        parameters=[WORKSPACE_HEADER],
        responses={200: ProjectSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create project",
        description="Create a new project in the current workspace.",
        parameters=[WORKSPACE_HEADER],
        request=ProjectSerializer,
        responses={201: ProjectSerializer},
    ),
)
class ProjectListCreateAPIView(ListCreateAPIView):
    serializer_class = ProjectSerializer
    queryset = Project.objects.none()

    # Filter & Search
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["name"]
    search_fields = ["name", "description"]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), IsMember()]
        return [IsAuthenticated(), IsAdmin()]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset

        return Project.objects.filter(
            workspace=self.request.workspace
        )

    def perform_create(self, serializer):
        project = serializer.save(workspace=self.request.workspace)

        ActivityLog.objects.create(
            workspace=self.request.workspace,
            user=self.request.user,
            action="project_created",
            message=f"{self.request.user.email} created project '{project.name}'"
        )

@extend_schema(
    summary="Update project",
    description="Update an existing project.",
    parameters=[WORKSPACE_HEADER],
    request=ProjectSerializer,
    responses={200: ProjectSerializer},
)
class ProjectUpdateAPIView(UpdateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Project.objects.filter(workspace=self.request.workspace)

    def perform_update(self, serializer):
        project = serializer.save()

        ActivityLog.objects.create(
            workspace=self.request.workspace,
            user=self.request.user,
            action="project_updated",
            message=f"{self.request.user.email} updated project '{project.name}'"
        )

@extend_schema(
    summary="Archive project",
    description="Soft delete (archive) a project in the current workspace.",
    parameters=[WORKSPACE_HEADER],
    request=None,
    responses={
        200: MessageSerializer,
        400: MessageSerializer,
        404: MessageSerializer,
    },
)
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

@extend_schema(
    summary="Restore project",
    description="Restore a previously archived project.",
    parameters=[WORKSPACE_HEADER],
    request=None,
    responses={
        200: MessageSerializer,
        400: MessageSerializer,
        404: MessageSerializer,
    },
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

@extend_schema_view(
    get=extend_schema(
        summary="List tasks",
        parameters=[WORKSPACE_HEADER],
        responses={200: TaskSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create task",
        parameters=[WORKSPACE_HEADER],
        request=TaskSerializer,
        responses={201: TaskSerializer},
    ),
)
class TaskListCreateAPIView(ListCreateAPIView):
    queryset = Task.objects.none()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMember]

    filter_backends = [DjangoFilterBackend,SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset

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
        if task.assigned_to:
            send_task_assignment_email_task.delay(task.id)

        ActivityLog.objects.create(
            user=self.request.user,
            workspace=self.request.workspace,
            action="task_created",
            message=f"{self.request.user.email} created task '{task.title}'"
        )

@extend_schema(
    parameters=[WORKSPACE_HEADER]
)
class TaskUpdateAPIView(UpdateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMember]

    def get_queryset(self):
        return Task.objects.filter(
            project__workspace=self.request.workspace
        ).select_related("project", "assigned_to")

    def perform_update(self, serializer):
        assigned_user = serializer.validated_data.get(
            "assigned_to",
            serializer.instance.assigned_to
        )

        membership = Membership.objects.get(
            user=self.request.user,
            workspace=self.request.workspace
        )

        if membership.role not in ["admin", "owner"]:
            if assigned_user and assigned_user != self.request.user:
                raise PermissionDenied(
                    "You can only update your own task."
                )

        # Store the current assignee before saving
        old_assignee_id = serializer.instance.assigned_to_id

        # Save the task
        task = serializer.save()

        # Get the new assignee after saving
        new_assignee_id = task.assigned_to_id

        # Send email only if the assignee changed
        if (
            new_assignee_id is not None
            and old_assignee_id != new_assignee_id
        ):
            send_task_assignment_email_task.delay(task.id)

        ActivityLog.objects.create(
            user=self.request.user,
            workspace=self.request.workspace,
            action="task_updated",
            message=f"{self.request.user.email} updated task '{task.title}'"
        )

@extend_schema(
    summary="Archive task",
    description="Soft delete (archive) a task in the current workspace.",
    parameters=[WORKSPACE_HEADER],
    request=None,
    responses={
        200: MessageSerializer,
        400: MessageSerializer,
        404: MessageSerializer,
    },
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

@extend_schema(
    summary="Restore task",
    description="Restore a previously archived task.",
    parameters=[WORKSPACE_HEADER],
    request=None,
    responses={
        200: MessageSerializer,
        400: MessageSerializer,
        404: MessageSerializer,
    },
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
@extend_schema_view(
    get=extend_schema(
        summary="List task comments",
        description="Retrieve all comments for a task.",
        parameters=[WORKSPACE_HEADER],
        responses={200: TaskCommentSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create task comment",
        description="Add a comment to a task.",
        parameters=[WORKSPACE_HEADER],
        request=TaskCommentSerializer,
        responses={201: TaskCommentSerializer},
    ),
)
class TaskCommentAPIView(ListCreateAPIView):
    queryset = TaskComment.objects.none()
    serializer_class = TaskCommentSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["user"]
    search_fields = ["content"]

    def get_permissions(self):
        return [IsAuthenticated(), IsMember()]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset

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

@extend_schema(
    parameters=[WORKSPACE_HEADER]
)
class TaskCommentUpdateAPIView(UpdateAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, IsMember]

    def get_queryset(self):
        return TaskComment.objects.filter(
            task__project__workspace=self.request.workspace
        ).select_related("user", "task")

    def perform_update(self, serializer):
        comment = serializer.instance

        membership = Membership.objects.get(
            user=self.request.user,
            workspace=self.request.workspace
        )

        if (
            comment.user != self.request.user
            and membership.role not in ["admin", "owner"]
        ):
            raise PermissionDenied(
                "You can update only your own comments."
            )

        comment = serializer.save()

        ActivityLog.objects.create(
            user=self.request.user,
            workspace=self.request.workspace,
            action="task_comment_updated",
            message=f"{self.request.user.email} updated comment on task '{comment.task.title}'"
        )

@extend_schema(
    summary="Archive task comment",
    description="Soft delete (archive) a task comment.",
    parameters=[WORKSPACE_HEADER],
    request=None,
    responses={
        200: MessageSerializer,
        400: MessageSerializer,
        403: MessageSerializer,
        404: MessageSerializer,
    },
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

@extend_schema(
    summary="Restore task comment",
    description="Restore a previously archived task comment.",
    parameters=[WORKSPACE_HEADER],
    request=None,
    responses={
        200: MessageSerializer,
        400: MessageSerializer,
        404: MessageSerializer,
    },
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
@extend_schema(
    parameters=[
        WORKSPACE_HEADER,
        OpenApiParameter(
            name="task_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Task ID",
        ),
    ],
    request=TaskAttachmentCreateSerializer,
    responses={
        201: TaskAttachmentSerializer,
    },
)
class TaskAttachmentAPIView(APIView):

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get_permissions(self):
        return [IsAuthenticated(), IsMember()]

    def post(self, request, task_id):

        task = get_object_or_404(
            Task,
            id=task_id,
            project__workspace=request.workspace
        )

        serializer = TaskAttachmentCreateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        attachment = serializer.save(
            task=task,
            uploaded_by=request.user
        )

        return Response(
            TaskAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED
        )