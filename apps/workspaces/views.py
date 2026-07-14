from rest_framework.views import APIView
from rest_framework.response import Response
from apps.audit.models import ActivityLog
from apps.projects.models import Project
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from apps.projects.serializers import ProjectSerializer
from apps.workspaces.permissions import IsMember, IsWorkspaceAdmin, IsWorkspaceMember
from apps.workspaces.serializers import MembershipSerializer, WorkspaceSerializer
from rest_framework import status
from .models import Workspace, Membership

class TestWorkspaceView(APIView):

    def get(self, request):
        if request.workspace:
            return Response({
                "workspace_id": request.workspace.id,
                "workspace_name": request.workspace.name
            })
        return Response({
            "message": "No workspace attached"
        })

# with custom_queryset
# class WorkspaceListView(APIView):
#     permission_classes = [IsAuthenticated, IsWorkspaceAdmin]
#     def get(self, request):
#         projects = Project.objects.for_workspace(request.workspace)

#         data = [p.name for p in projects]

#         return Response({
#             "projects": data
#         })
    

class CreateWorkspaceView(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):

        serializer = WorkspaceSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        workspace = serializer.save()

        Membership.objects.create(
            user=request.user,
            workspace=workspace,
            role="owner"
        )

        ActivityLog.objects.create(
            workspace=workspace,
            user=request.user,
            action="workspace_created",
            message=f"{request.user.email} created workspace '{workspace.name}'"
        )

        return Response(
            WorkspaceSerializer(workspace).data,
            status=status.HTTP_201_CREATED
        )
    
class MyWorkspacesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):

        memberships = (
            Membership.objects
            .filter(user=request.user)
            .select_related("workspace")
            .order_by("workspace__name")
        )

        serializer = MembershipSerializer(
            memberships,
            many=True
        )

        return Response(serializer.data)

class WorkspaceDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsMember
    ]

    def get(self, request):

        serializer = WorkspaceSerializer(
            request.workspace
        )

        return Response(serializer.data)
    

class WorkspaceProjectsAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsMember,
    ]

    def get(self, request):

        projects = (
            Project.objects
            .for_workspace(request.workspace)
            .order_by("-created_at")
        )

        serializer = ProjectSerializer(
            projects,
            many=True
        )

        return Response(serializer.data)