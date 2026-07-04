from rest_framework.permissions import BasePermission
from .models import Membership


class IsWorkspaceMember(BasePermission):

    def has_permission(self, request, view):
        if not request.workspace:
            return False

        return Membership.objects.filter(
            user=request.user,
            workspace=request.workspace
        ).exists()
    
class IsWorkspaceAdmin(BasePermission):

    def has_permission(self, request, view):
        if not request.workspace:
            return False

        return Membership.objects.filter(
            user=request.user,
            workspace=request.workspace,
            role__in=['owner', 'admin']
        ).exists()