from django import forms
from django.utils import timezone

from .models import Newsletter, Recipient, Message


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        exclude = ("owner",)
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "last_send_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        for field in ["start_time", "last_send_time"]:
            self.fields[field].input_formats = ["%Y-%m-%dT%H:%M"]
        if self.user and not self.user.is_staff:
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=self.user)
            self.fields["message"].queryset = Message.objects.filter(owner=self.user)


    def clean_start_time(self):
        start_time = self.cleaned_data.get("start_time")
        if start_time and timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time, timezone.get_current_timezone())
        return start_time


    def clean_last_send_time(self):
        last_send_time = self.cleaned_data.get("last_send_time")
        if last_send_time and timezone.is_naive(last_send_time):
            last_send_time = timezone.make_aware(last_send_time, timezone.get_current_timezone())
        return last_send_time


    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("last_send_time")

        if start and end:
            if end <= start:
                self.add_error("last_send_time", "Дата окончания должна быть позже даты начала.")

            now = timezone.now()
            if start < now:
                self.add_error("start_time", "Дата начала не может быть в прошлом.")

        return cleaned_data
