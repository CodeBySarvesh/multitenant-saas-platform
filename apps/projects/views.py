from rest_framework.views import APIView
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


class ProjectListCreateAPIView(APIView):
    # permission_classes = [IsAuthenticated,IsWorkspaceMember]
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), IsMember()]
        return [IsAuthenticated(), IsAdmin()]  # only admin+ can create

    def get(self, request):
        projects = Project.objects.filter(workspace=request.workspace)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(workspace=request.workspace)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=400)
    

class TaskListCreateAPIView(APIView):
    pagination_class = PageNumberPagination
    def get_permissions(self):
        return [IsAuthenticated(), IsMember()]

    # def get(self, request, project_id):
    #     tasks = Task.objects.filter(
    #         project__id=project_id,
    #         project__workspace=request.workspace
    #     ).select_related("project", "assigned_to")

    #     serializer = TaskSerializer(tasks, many=True)
    #     return Response(serializer.data)

    # ---after pagination class---
    def get(self, request, project_id):
        tasks = Task.objects.filter(
            project__id=project_id,
            project__workspace=request.workspace
        ).select_related("project", "assigned_to")

        paginator = self.pagination_class()
        paginated_tasks = paginator.paginate_queryset(tasks, request)

        serializer = TaskSerializer(paginated_tasks, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, project_id):
        try:
            project = Project.objects.get(
                id=project_id,
                workspace=request.workspace
            )
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=404)

        serializer = TaskSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            assigned_user = serializer.validated_data.get("assigned_to")

            membership = Membership.objects.get(
                user=request.user,
                workspace=request.workspace
            )

            if membership.role not in ["admin", "owner"]:
                if assigned_user and assigned_user != request.user:
                    return Response(
                        {"error": "You can assign task only to yourself"},
                        status=403
                    )

            task_title = serializer.validated_data.get("title")
            serializer.save(project=project)
            ActivityLog.objects.create(
                user=request.user,
                workspace=request.workspace,
                action="task_created",
                message=f"{request.user.email} created task '{task_title}'"
            )
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
 
    
class TaskCommentAPIView(APIView):

    def get_permissions(self):
        return [IsAuthenticated(), IsMember()]

    def get(self, request, task_id):
        comments = TaskComment.objects.filter(
            task__id=task_id,
            task__project__workspace=request.workspace
        ).select_related("user")

        serializer = TaskCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        try:
            task = Task.objects.get(
                id=task_id,
                project__workspace=request.workspace
            )
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)

        serializer = TaskCommentSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            
            serializer.save(user=request.user, task=task)
            ActivityLog.objects.create(
                user=request.user,
                workspace=request.workspace,
                action="comment_added",
                message=f"{request.user.email} commented on task '{task.title}'"
            )
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)