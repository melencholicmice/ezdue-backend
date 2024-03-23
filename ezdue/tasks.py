from celery import shared_task
from django.core.mail import send_mail

@shared_task
def reminder_email(email, message):
    send_mail(
        'Reminder',
        message,
        'from@example.com',
        [email],
        fail_silently=False,
    )
