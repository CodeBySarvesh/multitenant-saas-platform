from django.db import models
from apps.common.models import SoftDeleteModel
from apps.projects.models import Project
from django.conf import settings

from apps.tasks.managers import AllTaskAttachmentManager, AllTaskCommentManager, AllTaskManager, TaskAttachmentManager, TaskCommentManager, TaskManager

class Task(SoftDeleteModel):

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
    objects = TaskManager()
    all_objects = AllTaskManager()

    def __str__(self):
        return self.title



class TaskComment(SoftDeleteModel):
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

    objects = TaskCommentManager()
    all_objects = AllTaskCommentManager()


class TaskAttachment(SoftDeleteModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="attachments"
    )

    file = models.FileField(upload_to="task_attachments/")

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    objects = TaskAttachmentManager()
    all_objects = AllTaskAttachmentManager()
