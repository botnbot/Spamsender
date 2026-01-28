from django.core.mail import send_mail
from django.utils import timezone
from core.models import SendAttempt

def send_newsletter_now(newsletter):
    message = newsletter.message

    for recipient in newsletter.recipients.all():
        try:
            send_mail(
                subject=message.subject,
                message=message.text,
                from_email="noreply@example.com",
                recipient_list=[recipient.email],
                fail_silently=False
            )

            SendAttempt.objects.create(
                newsletter=newsletter,
                status="success",
                recipient=recipient,
                smtp_answer="OK"
            )

        except Exception as e:
            SendAttempt.objects.create(
                newsletter=newsletter,
                status="fail",
                recipient=recipient,
                smtp_answer=str(e)
            )

    now = timezone.now()

    if newsletter.status == "created":
        newsletter.status = "active"

    if now > newsletter.last_send_time:
        newsletter.status = "completed"

    newsletter.save()
    return True
