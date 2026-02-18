from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, DeleteView, DetailView, UpdateView
from django.views.generic import TemplateView

from core.services.send_newsletter import send_newsletter_now
from .forms import NewsletterForm
from .models import Newsletter, Recipient, SendAttempt, Message


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "core/message/message_list.html"
    context_object_name = "message_list"

    def get_queryset(self):
        return Message.objects.annotate(
            total_attempts=Count("newsletters__attempts"),
            success_attempts=Count(
                "newsletters__attempts",
                filter=Q(newsletters__attempts__status="success")
            ),
            fail_attempts=Count(
                "newsletters__attempts",
                filter=Q(newsletters__attempts__status="fail")
            ),
        )



class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['subject', 'text']
    template_name = 'core/message/message_create.html'
    context_object_name = 'message'
    success_url = reverse_lazy('core:message_list')


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'core/message/message_confirm_delete.html'
    success_url = reverse_lazy('core:message_list')
    context_object_name = 'message'


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'core/message/message_detail.html'
    context_object_name = 'message'


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ['subject', 'text']
    template_name = 'core/message/message_update.html'
    context_object_name = 'message'

    def get_success_url(self):
        return reverse_lazy('core:message_detail', kwargs={'pk': self.object.pk})


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    fields = ['email', 'name', 'comment']
    template_name = 'core/recipient/recipient_update.html'
    context_object_name = 'recipient'

    def get_success_url(self):
        return reverse_lazy('core:recipient_detail', kwargs={'pk': self.object.pk})


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'core/recipient/recipient_list.html'
    context_object_name = 'recipients'


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    template_name = 'core/recipient/recipient_create.html'
    fields = ['email', 'name', 'comment']
    success_url = reverse_lazy('core:recipient_list')
    context_object_name = 'recipient'


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = 'core/recipient/recipient_detail.html'
    context_object_name = 'recipient'


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'core/recipient/recipient_confirm_delete.html'
    success_url = reverse_lazy('core:recipient_list')
    context_object_name = 'recipient'


class NewsletterListView(LoginRequiredMixin, ListView):
    model = Newsletter
    template_name = 'core/newsletter/newsletter_list.html'
    context_object_name = 'newsletters'

class ActiveNewsletterListView(LoginRequiredMixin, ListView):
    template_name = 'core/newsletter/newsletter_active_list.html'
    model = Newsletter
    context_object_name = "newsletters"

    def get_queryset(self):
        now = timezone.now()
        queryset = Newsletter.objects.filter(
            (Q(status='started')) &
            Q(start_time__lte=now) &
            Q(last_send_time__gte=now)
        )
        return queryset


class NewsletterCreateView(LoginRequiredMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'core/newsletter/newsletter_create.html'
    success_url = reverse_lazy('core:newsletter_list')
    context_object_name = 'newsletter'


class NewsletterDeleteView(LoginRequiredMixin, DeleteView):
    model = Newsletter
    template_name = 'core/newsletter/newsletter_confirm_delete.html'
    success_url = reverse_lazy('core:newsletter_list')
    context_object_name = 'newsletter'


class NewsletterUpdateView(LoginRequiredMixin, UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'core/newsletter/newsletter_update.html'
    success_url = reverse_lazy('core:newsletter_list')
    context_object_name = 'newsletter'

    def get_success_url(self):
        return reverse_lazy('core:newsletter_detail', kwargs={'pk': self.object.pk})


class NewsletterDetailView(LoginRequiredMixin, DetailView):
    model = Newsletter
    template_name = 'core/newsletter/newsletter_detail.html'
    context_object_name = 'newsletter'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class NewsletterManualSendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        newsletter = get_object_or_404(Newsletter, pk=pk)

        # Отправляем рассылку через сервис
        success_count, fail_count = send_newsletter_now(newsletter)

        messages.success(
            request,
            f"Рассылка выполнена. Успешно: {success_count}, Неудачно: {fail_count}"
        )
        return redirect("core:newsletter_detail", pk=newsletter.pk)


class SendAttemptListView(LoginRequiredMixin, ListView):
    model = SendAttempt
    template_name = "core/attempt/attempt_list.html"
    context_object_name = "attempts"


class SendAttemptDetailView(LoginRequiredMixin, DetailView):
    model = SendAttempt
    template_name = "core/attempt/attempt_detail.html"
    context_object_name = "attempt"


class SuccessfulSendAttemptListView(LoginRequiredMixin, ListView):
    model = SendAttempt
    template_name = "core/attempt/success_attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        return SendAttempt.objects.filter(status="success")


class FailedSendAttemptListView(LoginRequiredMixin, ListView):
    model = SendAttempt
    template_name = "core/attempt/failed_attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        return SendAttempt.objects.filter(status="fail")


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        context["total_newsletters"] = Newsletter.objects.count()

        context["active_newsletters"] = (
            Newsletter.objects
            .all()
            .with_updated_status()
            .filter(status=Newsletter.STATUS_STARTED)
            .count()
        )

        context["unique_recipients"] = Recipient.objects.count()
        context["success_send_attempt_count"] = SendAttempt.objects.filter(status='success').count()
        context["fail_send_attempt_count"] = SendAttempt.objects.filter(status='fail').count()

        context["all_messages"] = Message.objects.all()

        return context


# class NewsletterManualSendView(LoginRequiredMixin, View):
#     def post(self, request, pk, success_count, fail_count):
#         newsletter = get_object_or_404(Newsletter, pk=pk)
#         try:
#             send_newsletter_now(newsletter)
#             messages.success(request, "Рассылка успешно отправлена вручную.")
#             success_count += 1
#         except Exception as e:
#             messages.error(request,f'Ошибка отправки {e}')
#             fail_count += 1
#
#         return redirect("core:newsletter_detail", pk=newsletter.pk)




