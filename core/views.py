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
from .mixins import OwnerQuerysetMixin
from .models import Newsletter, Recipient, SendAttempt, Message


class MessageListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Message
    template_name = "core/message/message_list.html"
    context_object_name = "message_list"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(
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

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, OwnerQuerysetMixin, DeleteView):
    model = Message
    template_name = 'core/message/message_confirm_delete.html'
    success_url = reverse_lazy('core:message_list')
    context_object_name = 'message'


class MessageDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = Message
    template_name = 'core/message/message_detail.html'
    context_object_name = 'message'


class MessageUpdateView(LoginRequiredMixin, OwnerQuerysetMixin, UpdateView):
    model = Message
    fields = ['subject', 'text']
    template_name = 'core/message/message_update.html'
    context_object_name = 'message'

    def get_success_url(self):
        return reverse_lazy('core:message_detail', kwargs={'pk': self.object.pk})


class RecipientUpdateView(LoginRequiredMixin, OwnerQuerysetMixin, UpdateView):
    model = Recipient
    fields = ['email', 'name', 'comment']
    template_name = 'core/recipient/recipient_update.html'
    context_object_name = 'recipient'

    def get_success_url(self):
        return reverse_lazy('core:recipient_detail', kwargs={'pk': self.object.pk})


class RecipientListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Recipient
    template_name = 'core/recipient/recipient_list.html'
    context_object_name = 'recipients'


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    template_name = 'core/recipient/recipient_create.html'
    fields = ['email', 'name', 'comment']
    success_url = reverse_lazy('core:recipient_list')
    context_object_name = 'recipient'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = Recipient
    template_name = 'core/recipient/recipient_detail.html'
    context_object_name = 'recipient'


class RecipientDeleteView(LoginRequiredMixin, OwnerQuerysetMixin, DeleteView):
    model = Recipient
    template_name = 'core/recipient/recipient_confirm_delete.html'
    success_url = reverse_lazy('core:recipient_list')
    context_object_name = 'recipient'


class NewsletterListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Newsletter
    template_name = 'core/newsletter/newsletter_list.html'
    context_object_name = 'newsletters'


class ActiveNewsletterListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    template_name = 'core/newsletter/newsletter_active_list.html'
    model = Newsletter
    context_object_name = "newsletters"

    def get_queryset(self):
        qs = super().get_queryset()
        now = timezone.now()
        return qs.filter(
            status='started',
            start_time__lte=now,
            last_send_time__gte=now
        )


class NewsletterCreateView(LoginRequiredMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'core/newsletter/newsletter_create.html'
    success_url = reverse_lazy('core:newsletter_list')
    context_object_name = 'newsletter'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class NewsletterDeleteView(LoginRequiredMixin, OwnerQuerysetMixin, DeleteView):
    model = Newsletter
    template_name = 'core/newsletter/newsletter_confirm_delete.html'
    success_url = reverse_lazy('core:newsletter_list')
    context_object_name = 'newsletter'


class NewsletterUpdateView(LoginRequiredMixin, OwnerQuerysetMixin, UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'core/newsletter/newsletter_update.html'
    success_url = reverse_lazy('core:newsletter_list')
    context_object_name = 'newsletter'

    def get_success_url(self):
        return reverse_lazy('core:newsletter_detail', kwargs={'pk': self.object.pk})


class NewsletterDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = Newsletter
    template_name = 'core/newsletter/newsletter_detail.html'
    context_object_name = 'newsletter'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class NewsletterManualSendView(LoginRequiredMixin, OwnerQuerysetMixin, View):
    def post(self, request, pk):
        newsletter = get_object_or_404(
            Newsletter,
            pk=pk,
        )

        if not request.user.is_staff and newsletter.owner != request.user:
            return redirect("core:newsletter_list")

        # Отправляем рассылку через сервис
        success_count, fail_count = send_newsletter_now(newsletter)

        messages.success(
            request,
            f"Рассылка выполнена. Успешно: {success_count}, Неудачно: {fail_count}"
        )
        return redirect("core:newsletter_detail", pk=newsletter.pk)


class SendAttemptListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = SendAttempt
    template_name = "core/attempt/attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        qs = super.get_queryset()
        user=self.request.user

        if user.is_staff:
            return qs

        return qs.filter(newsletter_owner=user)



class SendAttemptDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = SendAttempt
    template_name = "core/attempt/attempt_detail.html"
    context_object_name = "attempt"


class SuccessfulSendAttemptListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = SendAttempt
    template_name = "core/attempt/success_attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        qs = super.get_queryset().filter("success")
        if self.request.user.is_staff:
            return qs
        return qs.filter(newsletter__owner=self.request.user)


class FailedSendAttemptListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = SendAttempt
    template_name = "core/attempt/failed_attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        qs = super.get_queryset().filter("fail")
        if self.request.user.is_staff:
            return qs
        return qs.filter(newsletter__owner=self.request.user)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["total_newsletters"] = Newsletter.objects.filter(owner=user).count()

        context["active_newsletters"] = (
            Newsletter.objects
            .filter(owner=user)
            .with_updated_status()
            .filter(status=Newsletter.STATUS_STARTED)
            .count()
        )

        context["unique_recipients"] = Recipient.objects.filter(owner=user).count()
        context["success_send_attempt_count"] = SendAttempt.objects.filter(status='success', newsletter__owner=user).count()
        context["fail_send_attempt_count"] = SendAttempt.objects.filter(status='fail', newsletter__owner=user).count()

        context["all_messages"] = Message.objects.filter(owner=user)

        return context
