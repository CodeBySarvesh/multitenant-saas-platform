from rest_framework.permissions import BasePermission
from .models import Membership
from .utils import get_user_membership

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