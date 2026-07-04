from django.db import models
from apps.common.models import WorkspaceBaseModel
from apps.common.managers import WorkspaceManager


class Project(WorkspaceBaseModel):
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE, related_name='projects'
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    objects = WorkspaceManager()

    def __str__(self):
        return self.name