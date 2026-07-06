from rest_framework.permissions import BasePermission
from .models import Membership
from .utils import get_user_membership

class IsWorkspaceMember(BasePermission):

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        if not hasattr(request, "workspace") or not request.workspace:
            return False

        return Membership.objects.filter(
            workspace=request.workspace,
            user=request.user
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

class HasWorkspaceRole(BasePermission):

    allowed_roles = [] 

    def has_permission(self, request, view):

        membership = get_user_membership(request.user, request.workspace)

        if not membership:
            return False

        return membership.role in self.allowed_roles


class IsOwner(HasWorkspaceRole):
    allowed_roles = ['owner']

class IsAdmin(HasWorkspaceRole):
    allowed_roles = ['owner', 'admin']

class IsMember(HasWorkspaceRole):
    allowed_roles = ['owner', 'admin', 'member']