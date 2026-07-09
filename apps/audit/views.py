from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.audit.models import ActivityLog
from apps.workspaces.permissions import IsAdmin, IsMember, IsWorkspaceMember

class ActivityLogAPIView(APIView):

    def get_permissions(self):
        return [IsAuthenticated(), IsMember()]

    def get(self, request):
        logs = ActivityLog.objects.filter(
            workspace=request.workspace
        ).select_related("user").order_by("-created_at")

        data = [
            {
                "user": log.user.email if log.user else None,
                "action": log.action,
                "message": log.message,
                "time": log.created_at
            }
            for log in logs
        ]

        return Response(data)