from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q

from core.models import Message, Recipient, Newsletter, SendAttempt
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, DeleteView, DetailView, UpdateView, TemplateView


from core.services.send_newsletter import send_newsletter_now



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
    template_name = 'core/message_confirm_delete.html'
    success_url = reverse_lazy('core:message_list')
    context_object_name = 'message'


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'core/message_detail.html'
    context_object_name = 'message'


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ['subject', 'text']
    template_name = 'core/message_update.html'
    context_object_name = 'message'

    def get_success_url(self):
        return reverse_lazy('core:message_detail', kwargs={'pk': self.object.pk})


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    fields = ['email', 'name', 'comment']
    template_name = 'core/recipient_update.html'
    context_object_name = 'recipient'

    def get_success_url(self):
        return reverse_lazy('core:recipient_detail', kwargs={'pk': self.object.pk})


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'core/recipient/recipient_list.html'
    context_object_name = 'recipients'


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    template_name = 'core/recipient_create.html'
    fields = ['email', 'name', 'comment']
    success_url = reverse_lazy('core:recipient_list')
    context_object_name = 'recipient'


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = 'core/recipient_detail.html'
    context_object_name = 'recipient'


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'core/recipient_confirm_delete.html'
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
        # фильтруем рассылки, которые активны на текущий момент
        return Newsletter.objects.filter(
            first_send_time__lte=now,
            last_send_time__gte=now,
            status='active'
        )

class NewsletterCreateView(LoginRequiredMixin, CreateView):
    model = Newsletter
    fields = ['message', 'recipients', 'first_send_time', 'last_send_time']
    template_name = 'core/newsletter_create.html'
    success_url = reverse_lazy('core:newsletter_list')
    context_object_name = 'newsletter'


class NewsletterDeleteView(LoginRequiredMixin, DeleteView):
    model = Newsletter
    template_name = 'core/newsletter_confirm_delete.html'
    success_url = reverse_lazy('core:newsletter_list')
    context_object_name = 'newsletter'


class NewsletterUpdateView(LoginRequiredMixin, UpdateView):
    model = Newsletter
    fields = ['message', 'recipients', 'first_send_time', 'last_send_time']
    template_name = 'core/newsletter_update.html'
    success_url = reverse_lazy('core:newsletter_list')
    context_object_name = 'newsletter'

    def get_success_url(self):
        return reverse_lazy('core:newsletter_detail', kwargs={'pk': self.object.pk})


class NewsletterDetailView(LoginRequiredMixin, DetailView):
    model = Newsletter
    template_name = 'core/newsletter_detail.html'
    context_object_name = 'newsletter'


class SendAttemptListView(LoginRequiredMixin, ListView):
    model = SendAttempt
    template_name = "core/attempt_list.html"
    context_object_name = "attempts"


class SendAttemptDetailView(LoginRequiredMixin, DetailView):
    model = SendAttempt
    template_name = "core/attempt_detail.html"
    context_object_name = "attempt"


from django.utils.timezone import now
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Q
from .models import Newsletter, Recipient, SendAttempt, Message  # добавляем модель Message

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["total_newsletters"] = Newsletter.objects.count()
        active_filter = (
            (Q(status='active') | Q(status='started')) &
            Q(first_send_time__lte=now()) &
            Q(last_send_time__gte=now())
        )
        context["active_newsletters"] = Newsletter.objects.filter(active_filter).count()
        context["unique_recipients"] = Recipient.objects.count()
        context["success_send_attempt_count"] = SendAttempt.objects.filter(status='success').count()
        context["fail_send_attempt_count"] = SendAttempt.objects.filter(status='fail').count()

        context["all_messages"] = Message.objects.all()

        return context

class NewsletterManualSendView(LoginRequiredMixin, View):
    def post(self, request, pk, success_count, fail_count):
        newsletter = get_object_or_404(Newsletter, pk=pk)
        try:
            send_newsletter_now(newsletter)
            messages.success(request, "Рассылка успешно отправлена вручную.")
            success_count += 1
        except Exception as e:
            messages.error(request,f'Ошибка отправки {e}')
            fail_count += 1

        return redirect("core:newsletter_detail", pk=newsletter.pk)


def login_view(request):
    return HttpResponse("Заглушка: страница входа")


def logout_view(request):
    return HttpResponse("Заглушка: страница выхода")


