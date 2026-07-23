from rest_framework.views import APIView
from rest_framework.response import Response
from apps.audit.models import ActivityLog
from apps.common.docs import WORKSPACE_HEADER
from apps.projects.models import Project
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from apps.projects.serializers import ProjectSerializer
from apps.workspaces.permissions import IsAdmin, IsMember, IsOwner
from apps.workspaces.serializers import MembershipReadSerializer, MembershipSerializer, WorkspaceSerializer
from apps.common.serializers import MessageSerializer
from rest_framework import status
from .models import Workspace, Membership
from django.core.cache import cache
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

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


@extend_schema(
    summary="Create workspace",
    description="Create a new workspace and assign the authenticated user as its owner.",
    request=WorkspaceSerializer,
    responses={
        201: WorkspaceSerializer,
    },
)
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

@extend_schema(
    summary="Update workspace",
    description="Update the current workspace.",
    parameters=[WORKSPACE_HEADER],
    request=WorkspaceSerializer,
    responses={
        200: WorkspaceSerializer,
    },
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

@extend_schema(
    responses={200: MembershipReadSerializer(many=True)},
    summary="list workspaces",
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

        serializer = MembershipReadSerializer(
            memberships,
            many=True
        )

        return Response(serializer.data)

@extend_schema(
    parameters=[WORKSPACE_HEADER],
    responses={200: WorkspaceSerializer},
    summary="Get workspace details",
)
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
    
@extend_schema(
    parameters=[WORKSPACE_HEADER],
    responses={200: ProjectSerializer(many=True)},
    summary="List workspace projects",
)
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
@extend_schema(
    parameters=[WORKSPACE_HEADER]
)
class MembershipListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsMember]
    serializer_class = MembershipSerializer

    def get_queryset(self):
        return (
            Membership.objects
            .filter(workspace=self.request.workspace)
            .select_related("user")
            .order_by("user__email")
        )
    
@extend_schema(
    parameters=[WORKSPACE_HEADER]
)
class MembershipCreateAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = MembershipSerializer

    def perform_create(self, serializer):
        user = serializer.validated_data["user"]

        if Membership.objects.filter(
            workspace=self.request.workspace,
            user=user,
        ).exists():
            raise serializers.ValidationError(
                {"detail": "User is already a member."}
            )

        membership = serializer.save(workspace=self.request.workspace)

        cache.delete(
            f"membership:{user.id}:{self.request.workspace.id}"
        )

        ActivityLog.objects.create(
            workspace=self.request.workspace,
            user=self.request.user,
            action="member_assigned",
            message=(
                f"{self.request.user.email} added "
                f"{user.email} as {membership.role}"
            )
        )

@extend_schema(
    parameters=[WORKSPACE_HEADER]
)    
class MembershipUpdateAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = MembershipSerializer
    http_method_names = ["patch"]

    def get_queryset(self):
        return Membership.objects.filter(
            workspace=self.request.workspace
        )

    def perform_update(self, serializer):
        role = serializer.validated_data["role"]
        membership = serializer.save()

        cache.delete(
            f"membership:{membership.user.id}:{self.request.workspace.id}"
        )

        ActivityLog.objects.create(
            workspace=self.request.workspace,
            user=self.request.user,
            action="member_role_updated",
            message=(
                f"{self.request.user.email} changed "
                f"{membership.user.email}'s role to {role}"
            )
        )
         
class MembershipDeleteAPIView(APIView):

    permission_classes = [IsAuthenticated, IsOwner]
    @extend_schema(
        summary="Remove workspace member",
        description="Remove a member from the current workspace. The workspace owner cannot be removed.",
        parameters=[
            WORKSPACE_HEADER
        ],
        request=None,
        responses={
            200: MessageSerializer,
            400: MessageSerializer,
            404: MessageSerializer,
        },
    )
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