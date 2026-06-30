from django.db import models
from apps.common.models import WorkspaceBaseModel
from apps.common.managers import WorkspaceManager


class Task(WorkspaceBaseModel):
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)

    objects = WorkspaceManager()

    def __str__(self):
        return self.title