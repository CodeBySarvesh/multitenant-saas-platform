from django.db import models


class WorkspaceBaseModel(models.Model):
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True