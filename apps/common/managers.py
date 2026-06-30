from django.db import models


class WorkspaceQuerySet(models.QuerySet):

    def for_workspace(self, workspace):
        if workspace is None:
            return self.none()
        return self.filter(workspace=workspace)


class WorkspaceManager(models.Manager):

    def get_queryset(self):
        return WorkspaceQuerySet(self.model, using=self._db)

    def for_workspace(self, workspace):
        return self.get_queryset().for_workspace(workspace)
    
# class WorkspaceManager(models.Manager.from_queryset(WorkspaceQuerySet)):
#     pass