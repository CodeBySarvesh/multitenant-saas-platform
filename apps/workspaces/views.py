from rest_framework.views import APIView
from rest_framework.response import Response
from apps.audit.models import ActivityLog
from apps.projects.models import Project
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from apps.projects.serializers import ProjectSerializer
from apps.workspaces.permissions import IsAdmin, IsMember, IsOwner
from apps.workspaces.serializers import MembershipReadSerializer, MembershipSerializer, WorkspaceSerializer
from rest_framework import status
from .models import Workspace, Membership
from django.core.cache import cache
from rest_framework.generics import get_object_or_404
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
    
class WorkspaceUpdateAPIView(APIView):

    permission_classes = [IsAuthenticated, IsOwner]

    def patch(self, request):

        serializer = WorkspaceSerializer(
            request.workspace,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        workspace = serializer.save()

        cache.delete(
            f"workspace:{workspace.id}"
        )

        ActivityLog.objects.create(
            workspace=workspace,
            user=request.user,
            action="workspace_updated",
            message=f"{request.user.email} updated workspace '{workspace.name}'"
        )

        return Response(serializer.data)
    
class MyWorkspacesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):

        memberships = (
            Membership.objects
            .filter(user=request.user)
            .select_related("workspace")
            .order_by("workspace__name")
        )

        serializer = MembershipReadSerializer(
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

# -----Membership -------  
class MembershipListAPIView(APIView):

    permission_classes = [IsAuthenticated, IsMember]

    def get(self, request):

        members = (
            Membership.objects
            .filter(workspace=request.workspace)
            .select_related("user")
            .order_by("user__email")
        )

        serializer = MembershipSerializer(
            members,
            many=True
        )

        return Response(serializer.data)
    

class MembershipCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def post(self, request):

        serializer = MembershipSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        if Membership.objects.filter(
            workspace=request.workspace,
            user=user
        ).exists():

            return Response(
                {"detail": "User is already a member."},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership = Membership.objects.create(
            workspace=request.workspace,
            user=user,
            role=serializer.validated_data["role"]
        )

        cache.delete(
            f"membership:{user.id}:{request.workspace.id}"
        )

        ActivityLog.objects.create(
            workspace=request.workspace,
            user=request.user,
            action="member_created",
            message=f"{request.user.email} added {user.email} as {membership.role}"
        )

        return Response(
            MembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED
        )
    
class MembershipUpdateAPIView(APIView):

    permission_classes = [IsAuthenticated, IsOwner]

    def patch(self, request, pk):

        membership = get_object_or_404(
            Membership,
            id=pk,
            workspace=request.workspace
        )

        role = request.data.get("role")

        if role not in ['admin','member','owner',
        ]:
            return Response(
                {"detail": "Invalid role."},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership.role = role
        membership.save(update_fields=["role"])

        cache.delete(
            f"membership:{membership.user.id}:{request.workspace.id}"
        )

        ActivityLog.objects.create(
            workspace=request.workspace,
            user=request.user,
            action="member_role_updated",
            message=(
                f"{request.user.email} changed "
                f"{membership.user.email}'s role to {role}"
            )
        )

        return Response(
            MembershipSerializer(membership).data
        )
    
class MembershipDeleteAPIView(APIView):

    permission_classes = [IsAuthenticated, IsOwner]

    def delete(self, request, pk):

        membership = get_object_or_404(
            Membership,
            id=pk,
            workspace=request.workspace
        )

        if membership.role == "owner":
            return Response(
                {"detail": "Owner cannot be removed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = membership.user

        membership.delete()

        cache.delete(
            f"membership:{user.id}:{request.workspace.id}"
        )

        ActivityLog.objects.create(
            workspace=request.workspace,
            user=request.user,
            action="member_removed",
            message=f"{request.user.email} removed {user.email}"
        )

        return Response(
            {"detail": "Member removed successfully."}
        )