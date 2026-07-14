from django.db import models
from apps.common.models import SoftDeleteModel
from apps.projects.managers import AllProjectManager, ProjectManager


class Project(SoftDeleteModel):
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE, related_name='projects'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    objects = ProjectManager()
    all_objects = AllProjectManager()

    def __str__(self):
        return self.name