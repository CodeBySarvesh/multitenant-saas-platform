from django.db import models
from django.utils import timezone

class SoftDeleteQuerySet(models.QuerySet):

    def active(self):
        return self.filter(
            deleted_at__isnull=True
        )

    def deleted(self):
        return self.filter(
            deleted_at__isnull=False
        )

    def soft_delete(self):
        return self.update(
            deleted_at=timezone.now()
        )

    def restore(self):
        return self.update(
            deleted_at=None
        )


class SoftDeleteManager(models.Manager):

    def get_queryset(self):
        return SoftDeleteQuerySet(
            self.model,
            using=self._db
        ).active()

class AllObjectsManager(models.Manager):

    def get_queryset(self):
        return SoftDeleteQuerySet(
            self.model,
            using=self._db
        )

class WorkspaceQuerySet(SoftDeleteQuerySet):

    def for_workspace(self, workspace):
        if workspace is None:
            return self.none()
        return self.filter(workspace=workspace)


class WorkspaceManager(SoftDeleteManager):

    def get_queryset(self):
        return WorkspaceQuerySet(
            self.model,
            using=self._db
        ).active()

    def for_workspace(self, workspace):
        return self.get_queryset().for_workspace(workspace)
    

class AllWorkspaceManager(AllObjectsManager):

    def get_queryset(self):
        return WorkspaceQuerySet(
            self.model,
            using=self._db
        )

    def for_workspace(self, workspace):
        return self.get_queryset().for_workspace(workspace)
    
# class WorkspaceManager(models.Manager.from_queryset(WorkspaceQuerySet)):
#     pass