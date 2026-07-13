from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("task_created", "Task Created"),
        ("task_updated", "Task Updated"),
        ("task_archived", "Task Archived"),
        ("task_restored", "Task Restored"),
        ("project_created", "Project Created"),
        ("project_updated", "Project Updated"),
        ("project_archived", "Project Archived"),
        ("project_restored", "Project Restored"),
        ("comment_added", "Comment Added"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.CASCADE)

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)