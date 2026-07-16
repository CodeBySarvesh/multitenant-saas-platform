from django.http import HttpResponseForbidden
from .models import Workspace, Membership
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden

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
class WorkspaceMiddleware:

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
                    timeout=settings.WORKSPACE_CACHE_TIMEOUT,
                )

            except Workspace.DoesNotExist:
                return HttpResponseForbidden("Invalid workspace.")
        else:
            print("CACHE HIT - using Redis")

        request.workspace = workspace

        return self.get_response(request)