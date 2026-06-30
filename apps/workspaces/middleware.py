from django.http import HttpResponseForbidden
from .models import Workspace, Membership


class WorkspaceMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Default
        request.workspace = None

        workspace_id = request.headers.get('X-Workspace-ID')

        if workspace_id:
            try:
                workspace = Workspace.objects.get(id=workspace_id)

                # If user is logged in → validate membership
                if request.user.is_authenticated:
                    is_member = Membership.objects.filter(
                        user=request.user,
                        workspace=workspace
                    ).exists()

                    if not is_member:
                        return HttpResponseForbidden("Not a workspace member")

                # Attach workspace to request
                request.workspace = workspace

            except Workspace.DoesNotExist:
                return HttpResponseForbidden("Invalid workspace")

        return self.get_response(request)