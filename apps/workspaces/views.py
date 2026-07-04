from rest_framework.views import APIView
from rest_framework.response import Response
from apps.projects.models import Project
from rest_framework.permissions import IsAuthenticated

from apps.workspaces.permissions import IsWorkspaceAdmin, IsWorkspaceMember

from .models import Workspace, Membership

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

# with custom_queryset
class WorkspaceListView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceAdmin]
    def get(self, request):
        projects = Project.objects.for_workspace(request.workspace)

        data = [p.name for p in projects]

        return Response({
            "projects": data
        })
    

class CreateWorkspaceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get("name")

        if not name:
            return Response({"error": "Name required"}, status=400)

        workspace = Workspace.objects.create(name=name)

        # 🔥 Auto add creator as OWNER
        Membership.objects.create(
            user=request.user,
            workspace=workspace,
            role='owner'
        )

        return Response({
            "workspace_id": workspace.id,
            "name": workspace.name
        })
    
class MyWorkspacesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = Membership.objects.filter(user=request.user)

        data = [
            {
                "workspace_id": m.workspace.id,
                "name": m.workspace.name,
                "role": m.role
            }
            for m in memberships
        ]

        return Response(data)