from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DeleteView, DetailView, UpdateView, TemplateView

from core.models import Message, Recipient, Newsletter, SendAttempt
from core.services.send_newsletter import send_newsletter_now


# Create your views here.


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'core/message_list.html'
    context_object_name = 'messages'


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['subject', 'text']
    template_name = 'core/message_create.html'
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
    template_name = 'core/recipient_list.html'
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
    template_name = 'core/newsletter_list.html'
    context_object_name = 'newsletters'


class NewsletterCreateView(LoginRequiredMixin, CreateView):
    model = Newsletter
    fields = ['message', 'recipients']
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
    fields = ['message', 'recipients']
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


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["total_newsletters"] = Newsletter.objects.count()
        context["active_newsletters"] = Newsletter.objects.filter(status='active').count()
        context["unique_recipients"] = Recipient.objects.count()

        return context


class NewsletterManualSendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        newsletter = get_object_or_404(Newsletter, pk=pk)

        send_newsletter_now(newsletter)
        messages.success(request, "Рассылка успешно отправлена вручную.")

        return redirect("core:newsletter_detail", pk=newsletter.pk)


def login_view(request):
    return HttpResponse("Заглушка: страница входа")


def logout_view(request):
    return HttpResponse("Заглушка: страница выхода")
