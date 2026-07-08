from django.db import models
from apps.common.models import WorkspaceBaseModel
from apps.common.managers import WorkspaceManager
from apps.projects.models import Project
from django.conf import settings

class Task(WorkspaceBaseModel):

    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    project = models.ForeignKey(Project,on_delete=models.CASCADE,related_name='tasks')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='todo')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks"
    )

    def __str__(self):
        return self.title



class TaskComment(models.Model):
    task = models.ForeignKey(
        "Task",
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)