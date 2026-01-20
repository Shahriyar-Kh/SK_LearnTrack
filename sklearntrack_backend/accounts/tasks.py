from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={'max_retries': 3},
    retry_jitter=True
)
def send_password_reset_email(self, subject, message, to_email):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False
    )
