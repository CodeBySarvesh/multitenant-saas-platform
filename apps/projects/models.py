from django.db import models
from apps.common.models import WorkspaceBaseModel
from apps.common.managers import WorkspaceManager


class Project(WorkspaceBaseModel):
    name = models.CharField(max_length=255)

    objects = WorkspaceManager()

    def __str__(self):
        return self.name