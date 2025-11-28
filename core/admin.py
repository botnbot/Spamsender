
from django.contrib import admin

from core.models import Message, Newsletter, Recipient, SendAttempt


# Register your models here.
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject')
    search_fields = ('subject', )

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email")
    search_fields = ("name", "email")
    list_filter = ("email",)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_send_time', 'last_send_time', 'status', 'message', 'get_recipients')
    search_fields = ('status',)
    list_filter = ("status", 'first_send_time', 'last_send_time',)
    filter_horizontal = ("recipients",)

    def get_recipients(self, obj):
        return ", ".join(r.email for r in obj.recipients.all())

    get_recipients.short_description = "Получатели"

@admin.register(SendAttempt)
class SendAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt_time', 'status', 'smtp_answer', 'newsletter')
    search_fields = ('status', 'newsletter__message__subject')
    list_filter = ("status", 'attempt_time', 'smtp_answer', 'newsletter')

