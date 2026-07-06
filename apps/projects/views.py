from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.tasks.models import Task
from apps.workspaces.models import Membership
from rest_framework.permissions import IsAuthenticated

from apps.workspaces.permissions import IsAdmin, IsMember, IsWorkspaceMember
from .models import Project
from .serializers import ProjectSerializer, TaskSerializer


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
    # permission_classes = [IsAuthenticated, IsWorkspaceMember]
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), IsMember()]
        return [IsAuthenticated(), IsAdmin()]  # only admin+ can create
    def get(self, request, project_id):
        tasks = Task.objects.filter(
            project__id=project_id,
            project__workspace=request.workspace
        )
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):
        try:
            project = Project.objects.get(
            id=project_id,
            workspace=request.workspace
            )
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=404)

        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)