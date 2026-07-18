from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_task_assignment_email(task):

    assignee = task.assigned_to

    if assignee is None:
        return

    context = {
    "assignee_name": assignee.email,
    "workspace": task.project.workspace.name,
    "project": task.project.name,
    "task": task.title,
    "status": task.get_status_display(),
}

    html_content = render_to_string(
        "emails/task_assignment.html",
        context,
    )

    text_content = render_to_string(
        "emails/task_assignment.txt",
        context,
    )

    email = EmailMultiAlternatives(
        subject = (
            f"[{task.project.workspace.name}]"
            f"Task Assigned - {task.title}"
        ),
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[assignee.email],
    )

    email.attach_alternative(
        html_content,
        "text/html",
    )

    email.send()