from django.core.mail import send_mail
from django.utils import timezone

from config import settings
from core.models import SendAttempt

def send_newsletter_now(newsletter):
    message = newsletter.message

    success_count = 0
    fail_count = 0

    for recipient in newsletter.recipients.all():
        try:
            send_mail(
                subject=message.subject,
                message=message.text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False
            )

            SendAttempt.objects.create(
                newsletter=newsletter,
                status="success",
                recipient=recipient,
                smtp_answer="OK"
            )

            success_count += 1

        except Exception as e:
            SendAttempt.objects.create(
                newsletter=newsletter,
                status="fail",
                recipient=recipient,
                smtp_answer=str(e)
            )

            fail_count += 1

    now = timezone.now()

    if newsletter.status == "created":
        newsletter.status = "active"

    if newsletter.last_send_time and now > newsletter.last_send_time:
        newsletter.status = "completed"

    newsletter.save()

    return success_count, fail_count
