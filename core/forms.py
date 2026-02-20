from django import forms
from django.utils import timezone

from .models import Newsletter, Recipient, Message


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        exclude = ("owner",)
        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                }
            ),
            "last_send_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        for field in ["start_time", "last_send_time"]:
            self.fields[field].input_formats = ["%Y-%m-%dT%H:%M"]

        if self.user and not self.user.is_staff:
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=self.user)
            self.fields["message"].queryset = Message.objects.filter(owner=self.user)

    def clean(self):
        cleaned_data = super().clean()

        first = cleaned_data.get("start_time")
        last = cleaned_data.get("last_send_time")

        if first and last and last <= first:
            self.add_error("last_send_time", "Дата окончания должна быть позже даты начала.")

        if first and first < timezone.now():
            self.add_error(
                "start_time",
                "Дата начала не может быть в прошлом."
            )

        return cleaned_data
