
from django.contrib import admin

from core.models import Message, Newsletter, Recipient


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

