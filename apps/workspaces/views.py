from rest_framework.views import APIView
from rest_framework.response import Response

from apps.projects.models import Project

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


class TestWorkspaceDataView(APIView):

    def get(self, request):
        projects = Project.objects.for_workspace(request.workspace)

        data = [p.name for p in projects]

        return Response({
            "projects": data
        })