import mimetypes
import os

from celery import shared_task

from .models import TaskAttachment


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_attachment(self, attachment_id):

    attachment = TaskAttachment.objects.get(pk=attachment_id)

    file_path = attachment.file.path

    file_size = os.path.getsize(file_path)

    mime_type, _ = mimetypes.guess_type(file_path)

    print(
        f"""
        Processing attachment

        ID: {attachment.id}

        Name: {attachment.file.name}

        Size: {file_size}

        MIME: {mime_type}
        """
    )