from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, DetailView, UpdateView

from core.models import Message, Recipient, Newsletter


# Create your views here.


class MessageListView(ListView):
    model = Message
    template_name = 'core/message_list.html'
    context_object_name = 'messages'


class MessageCreateView(CreateView):
    model = Message
    fields = ['subject', 'text']
    template_name = 'core/message_create.html'
    context_object_name = 'message'
    success_url = reverse_lazy('core:message_list')


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'core/message_confirm_delete.html'
    success_url = reverse_lazy('core:message_list')
    context_object_name = 'message'


class MessageDetailView(DetailView):
    model = Message
    template_name = 'core/message_detail.html'
    context_object_name = 'message'

    def get_success_url(self):
        return reverse_lazy('core:message_detail', kwargs={'pk': self.object.pk})


class MessageUpdateView(UpdateView):
    model = Message
    fields = ['subject', 'text']
    template_name = 'core/message_update.html'
    context_object_name = 'message'

    def get_success_url(self):
        return reverse_lazy('core:message_detail', kwargs={'pk': self.object.pk})


class RecipientUpdateView(UpdateView):
    model = Recipient
    fields = ['email', 'name', 'comment']
    template_name = 'core/recipient_update.html'
    context_object_name = 'recipient'

    def get_success_url(self):
        return reverse_lazy('core:recipient_detail', kwargs={'pk': self.object.pk})


class RecipientListView(ListView):
    model = Recipient
    template_name = 'core/recipient_list.html'
    context_object_name = 'recipients'


class RecipientCreateView(CreateView):
    model = Recipient
    template_name = 'core/recipient_create.html'
    fields = ['email', 'name', 'comment']
    success_url = reverse_lazy('core:recipient_list')
    context_object_name = 'recipient'


class RecipientDetailView(DetailView):
    model = Recipient
    template_name = 'core/recipient_detail.html'
    context_object_name = 'recipient'

    def get_success_url(self):
        return reverse_lazy('core:recipient_detail', kwargs={'pk': self.object.pk})


class RecipientDeleteView(DeleteView):
    model = Recipient
    template_name = 'core/recipient_confirm_delete.html'
    success_url = reverse_lazy('core:recipient_list')
    context_object_name = 'recipient'


class NewsletterListView(ListView):
    model = Newsletter
    template_name = 'core/newsletter_list.html'
    context_object_name = 'newsletters'


class NewsletterCreateView(CreateView):
    model = Newsletter
    fields = ['first_send_time', 'last_send_time', 'status', 'message', 'recipients']
    template_name = 'core/newsletter_create.html'
    success_url = reverse_lazy('core:newsletter_list')
    context_object_name = 'newsletter'


class NewsletterDeleteView(DeleteView):
    model = Newsletter
    template_name = 'core/newsletter_confirm_delete.html'
    success_url = reverse_lazy('core:newsletter_list')
    context_object_name = 'newsletter'


class NewsletterUpdateView(UpdateView):
    model = Newsletter
    fields = ['first_send_time', 'last_send_time', 'status', 'message', 'recipients']
    template_name = 'core/newsletter_update.html'
    success_url = reverse_lazy('core:newsletter_list')
    context_object_name = 'newsletter'

    def get_success_url(self):
        return reverse_lazy('core:newsletter_detail', kwargs={'pk': self.object.pk})


class NewsletterDetailView(DetailView):
    model = Newsletter
    template_name = 'core/newsletter_detail.html'
    context_object_name = 'newsletter'


def login_view(request):
    return HttpResponse("Заглушка: страница входа")

def logout_view(request):
    return HttpResponse("Заглушка: страница выхода")