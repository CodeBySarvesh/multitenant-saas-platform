from django.http import HttpResponseForbidden
from .models import Workspace, Membership


# class WorkspaceMiddleware:

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):

#         # Default
#         request.workspace = None

#         workspace_id = request.headers.get('X-Workspace-ID')

#         if workspace_id:
#             try:
#                 workspace = Workspace.objects.get(id=workspace_id)

#                 # If user is logged in → validate membership
#                 if request.user.is_authenticated:
#                     is_member = Membership.objects.filter(
#                         user=request.user,
#                         workspace=workspace
#                     ).exists()

#                     if not is_member:
#                         return HttpResponseForbidden("Not a workspace member")

#                 # Attach workspace to request
#                 request.workspace = workspace

#             except Workspace.DoesNotExist:
#                 return HttpResponseForbidden("Invalid workspace")

#         return self.get_response(request)


# ------ after adding Redis cache -------
from django.core.cache import cache
from django.http import HttpResponseForbidden

from .models import Workspace, Membership


class WorkspaceMiddleware:

    WORKSPACE_CACHE_TIMEOUT = 600      # 10 minutes
    MEMBERSHIP_CACHE_TIMEOUT = 300     # 5 minutes

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.workspace = None

        workspace_id = request.headers.get("X-Workspace-ID")

        if not workspace_id:
            return self.get_response(request)

        workspace_cache_key = f"workspace:{workspace_id}"

        workspace = cache.get(workspace_cache_key)
        print("Redis cache",workspace)
        if workspace is None:
            print("CACHE MISS - querying database")
            try:
                workspace = Workspace.objects.get(pk=workspace_id)

                cache.set(
                    workspace_cache_key,
                    workspace,
                    timeout=self.WORKSPACE_CACHE_TIMEOUT
                )

            except Workspace.DoesNotExist:
                return HttpResponseForbidden("Invalid workspace.")
        else:
            print("CACHE HIT - using Redis")

        if request.user.is_authenticated:

            membership_cache_key = (
                f"membership:{request.user.id}:{workspace.id}"
            )

            is_member = cache.get(membership_cache_key)

            if is_member is None:
                print("MEMBERSHIP CACHE MISS - querying database")

                is_member = Membership.objects.filter(
                    workspace=workspace,
                    user=request.user
                ).exists()

                cache.set(
                    membership_cache_key,
                    is_member,
                    timeout=self.MEMBERSHIP_CACHE_TIMEOUT
                )
            else:
                print("MEMBERSHIP CACHE HIT - using Redis")

            if not is_member:
                return HttpResponseForbidden(
                    "You are not a member of this workspace."
                )

        request.workspace = workspace

        return self.get_response(request)