from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.audit.models import ActivityLog
from apps.audit.serializers import ActivityLogSerializer
from apps.workspaces.permissions import IsAdmin, IsMember, IsWorkspaceMember
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView

class ActivityLogAPIView(ListAPIView):
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
        return (
            ActivityLog.objects.filter(
                workspace=self.request.workspace
            )
            .select_related("user")
        )

    def get_serializer_class(self):
        return ActivityLogSerializer