from django.db import models
from apps.common.models import SoftDeleteModel
from apps.common.managers import AllWorkspaceManager, WorkspaceManager


class Project(SoftDeleteModel):
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE, related_name='projects'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    objects = WorkspaceManager()
    all_objects = AllWorkspaceManager()

    def __str__(self):
        return self.name