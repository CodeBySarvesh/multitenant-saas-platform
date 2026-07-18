from celery import shared_task

from apps.tasks.models import Task
from .services import send_task_assignment_email


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_task_assignment_email_task(self, task_id):

    task = (
        Task.objects
        .select_related(
            "assigned_to",
            "created_by",
            "project",
            "project__workspace",
        )
        .get(pk=task_id)
    )

    send_task_assignment_email(task)