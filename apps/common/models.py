from django.db import models
from django.utils import timezone
from .managers import (
    SoftDeleteManager,
    AllObjectsManager,
)


class DateTimeBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(DateTimeBaseModel):

    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    objects = SoftDeleteManager()

    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])