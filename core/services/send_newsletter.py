from django.core.mail import send_mail
from django.utils import timezone
from core.models import SendAttempt

def send_newsletter_now(newsletter):
    """
    Отправляет рассылку всем получателям прямо сейчас.
    Создает SendAttempt для каждой попытки.
    """
    message = newsletter.message
    recipients = newsletter.recipients.all()

    for recipient in recipients:
        try:
            result = send_mail(
                subject=message.subject,
                message=message.text,
                from_email="admin@example.com",  # поменять при необходимости
                recipient_list=[recipient.email],
                fail_silently=False
            )

            SendAttempt.objects.create(
                newsletter=newsletter,
                status='success',
                smtp_answer=f"Message sent to {recipient.email}"
            )
        except Exception as e:
            SendAttempt.objects.create(
                newsletter=newsletter,
                status='fail',
                smtp_answer=str(e)
            )

    newsletter.status = "completed"
    newsletter.last_send_time = timezone.now()
    newsletter.save()

    return True
