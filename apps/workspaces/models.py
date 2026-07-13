from django.db import models
from django.contrib.auth import get_user_model
from apps.common.models import DateTimeBaseModel,SoftDeleteModel
# User = get_user_model()
from django.conf import settings

class Workspace(SoftDeleteModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Membership(DateTimeBaseModel):
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