from django.db import models
from apps.common.models import WorkspaceBaseModel
from apps.common.managers import WorkspaceManager
from apps.projects.models import Project


class Task(WorkspaceBaseModel):

    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo'
    )

    def __str__(self):
        return self.title