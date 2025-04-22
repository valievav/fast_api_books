from celery import Celery
from src.mail import mail, create_message
from typing import List
from asgiref.sync import async_to_sync

# celery tasks are synchronous! so need to convert async to sync
celery_app = Celery()
celery_app.config_from_object('src.config')


@celery_app.task()
def send_email_task(recipients: List[str], subject: str, body: str):
    """
    Send email task
    """
    message = create_message(
        recipients=recipients,
        subject=subject,
        body=body
    )

    async_to_sync(mail.send_message)(message)
