from django.db import models
from django.contrib.auth import get_user_model

from apps.common.models import WorkspaceBaseModel

User = get_user_model()
from django.conf import settings

class Workspace(WorkspaceBaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Membership(WorkspaceBaseModel):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,default='member')

    class Meta:
        unique_together = ('user', 'workspace')