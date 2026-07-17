from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("workspace_created", "Workspace Created"),
        ("workspace_updated", "Workspace Updated"),
        ("task_created", "Task Created"),
        ("task_updated", "Task Updated"),
        ("task_archived", "Task Archived"),
        ("task_restored", "Task Restored"),
        ("member_assigned", "Member Assigned"),
        ("member_role_updated", "Member Role Updated"),
        ("member_removed", "Member Removed"),
        ("task_comment_created", "Task Comment Created"),
        ("task_comment_updated", "Task Comment Updated"),
        ("task_comment_archived", "Task Comment Archived"),
        ("task_comment_restored", "Task Comment Restored"),
        ("project_created", "Project Created"),
        ("project_updated", "Project Updated"),
        ("project_archived", "Project Archived"),
        ("project_restored", "Project Restored"),
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