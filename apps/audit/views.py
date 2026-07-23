from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.audit.models import ActivityLog
from apps.audit.serializers import ActivityLogSerializer
from apps.common.docs import WORKSPACE_HEADER
from apps.workspaces.permissions import IsAdmin, IsMember
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema

@extend_schema(
    parameters=[WORKSPACE_HEADER],
    responses={200: ActivityLogSerializer(many=True)},
    summary="List activity logs",
    description="Retrieve activity logs for the current workspace.",
)
class ActivityLogAPIView(ListAPIView):
    queryset = ActivityLog.objects.none()
    permission_classes = [IsAuthenticated, IsMember]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = ["action", "user"]
    search_fields = ["message", "action"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset

        return (
            ActivityLog.objects.filter(
                workspace=self.request.workspace
            )
            .select_related("user")
        )

    def get_serializer_class(self):
        return ActivityLogSerializer