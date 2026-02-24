from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_control
from django.views.generic import ListView, CreateView, DeleteView, DetailView, UpdateView
from django.views.generic import TemplateView
from django.views.generic.detail import SingleObjectMixin
from core.services.send_newsletter import send_newsletter_now
from .forms import NewsletterForm
from .mixins import OwnerOrManagerMixin
from .models import Newsletter, Recipient, SendAttempt, Message


class MessageListView(LoginRequiredMixin, OwnerOrManagerMixin, ListView):
    manager_permission = "core.view_all_messages"
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


class MessageDeleteView(LoginRequiredMixin, OwnerOrManagerMixin, DeleteView):
    manager_permission = "core.view_all_messages"
    model = Message
    template_name = 'core/message/message_confirm_delete.html'
    success_url = reverse_lazy('core:message_list')
    context_object_name = 'message'


class MessageDetailView(LoginRequiredMixin, OwnerOrManagerMixin, DetailView):
    manager_permission = "core.view_all_messages"
    model = Message
    template_name = 'core/message/message_detail.html'
    context_object_name = 'message'


class MessageUpdateView(LoginRequiredMixin, OwnerOrManagerMixin, UpdateView):
    manager_permission = "core.view_all_messages"
    model = Message
    fields = ['subject', 'text']
    template_name = 'core/message/message_update.html'
    context_object_name = 'message'

    def get_success_url(self):
        return reverse_lazy('core:message_detail', kwargs={'pk': self.object.pk})


class RecipientUpdateView(LoginRequiredMixin, OwnerOrManagerMixin, UpdateView):
    manager_permission = "core.view_all_recipients"
    model = Recipient
    fields = ['email', 'name', 'comment']
    template_name = 'core/recipient/recipient_update.html'
    context_object_name = 'recipient'

    def get_success_url(self):
        return reverse_lazy('core:recipient_detail', kwargs={'pk': self.object.pk})


class RecipientListView(LoginRequiredMixin, OwnerOrManagerMixin, ListView):
    manager_permission = "core.view_all_recipients"
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


class RecipientDetailView(LoginRequiredMixin, OwnerOrManagerMixin, DetailView):
    manager_permission = "core.view_all_recipients"
    model = Recipient
    template_name = 'core/recipient/recipient_detail.html'
    context_object_name = 'recipient'


class RecipientDeleteView(LoginRequiredMixin, OwnerOrManagerMixin, DeleteView):
    manager_permission = "core.view_all_recipients"
    model = Recipient
    template_name = 'core/recipient/recipient_confirm_delete.html'
    success_url = reverse_lazy('core:recipient_list')
    context_object_name = 'recipient'

class NewsletterListView(LoginRequiredMixin, OwnerOrManagerMixin, ListView):
    model = Newsletter
    manager_permission = "core.view_all_newsletters"
    template_name = 'core/newsletter/newsletter_list.html'
    context_object_name = 'newsletters'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.with_updated_status()


class ActiveNewsletterListView(LoginRequiredMixin, OwnerOrManagerMixin, ListView):
    model = Newsletter
    template_name = 'core/newsletter/newsletter_active_list.html'
    context_object_name = "newsletters"
    manager_permission = "core.view_all_newsletters"

    def get_queryset(self):
        qs = super().get_queryset()
        now = timezone.now()
        return qs.filter(
            status=Newsletter.STATUS_STARTED,
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
        response = super().form_valid(form)
        cache.delete(f"newsletter_list_{self.request.user.id}")
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

class NewsletterDeleteView(LoginRequiredMixin, OwnerOrManagerMixin, DeleteView):
    manager_permission = "core.view_all_newsletters"
    model = Newsletter
    template_name = 'core/newsletter/newsletter_confirm_delete.html'
    success_url = reverse_lazy('core:newsletter_list')
    context_object_name = 'newsletter'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)

        cache.delete(f"newsletter_list_{request.user.id}")
        cache.delete(f"attempt_list_{request.user.id}")

        return response


class NewsletterUpdateView(LoginRequiredMixin, OwnerOrManagerMixin, UpdateView):
    manager_permission = "core.view_all_newsletters"
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'core/newsletter/newsletter_update.html'
    context_object_name = 'newsletter'

    def get_success_url(self):
        return reverse_lazy('core:newsletter_detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        cache.delete(f"newsletter_list_{self.request.user.id}")
        cache.delete(f"attempt_list_{self.request.user.id}")
        return response

class NewsletterDetailView(LoginRequiredMixin, OwnerOrManagerMixin, DetailView):
    manager_permission = "core.view_all_newsletters"
    model = Newsletter
    template_name = 'core/newsletter/newsletter_detail.html'
    context_object_name = 'newsletter'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class NewsletterManualSendView(
    LoginRequiredMixin,
    OwnerOrManagerMixin,
    SingleObjectMixin,
    View,
):
    model = Newsletter
    manager_permission = "core.view_all_newsletters"
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        newsletter = self.object
        now = timezone.now()
        if not (newsletter.start_time <= now <= newsletter.last_send_time):
            messages.error(
                request,
                "Рассылка вне разрешенного периода отправки."
            )
            return redirect("core:newsletter_detail", pk=newsletter.pk)
        success_count, fail_count = send_newsletter_now(newsletter)
        messages.success(
            request,
            f"Рассылка выполнена. Успешно: {success_count}, Неудачно: {fail_count}"
        )
        cache.delete(f"attempt_list_{request.user.id}")
        return redirect("core:newsletter_detail", pk=newsletter.pk)


class SendAttemptListView(LoginRequiredMixin, OwnerOrManagerMixin, ListView):
    model = SendAttempt
    template_name = "core/attempt/attempt_list.html"
    context_object_name = "attempts"
    manager_permission = "core.view_all_newsletters"


class SendAttemptDetailView(LoginRequiredMixin, OwnerOrManagerMixin, DetailView):
    manager_permission = "core.view_all_newsletters"
    model = SendAttempt
    template_name = "core/attempt/attempt_detail.html"
    context_object_name = "attempt"



class SuccessfulSendAttemptListView(LoginRequiredMixin, ListView):
    model = SendAttempt
    template_name = "core/attempt/success_attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        qs = super().get_queryset().filter(status="success")
        user = self.request.user
        if user.has_perm("core.view_all_newsletters"):
            return qs
        return qs.filter(newsletter__owner=self.request.user)


class FailedSendAttemptListView(LoginRequiredMixin, ListView):
    model = SendAttempt
    template_name = "core/attempt/failed_attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        qs = super().get_queryset().filter(status="fail")
        user = self.request.user

        if user.has_perm("core.view_all_newsletters"):
            return qs

        return qs.filter(newsletter__owner=user)

@method_decorator(cache_control(private=True, max_age=60), name='dispatch')
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
        context["success_send_attempt_count"] = SendAttempt.objects.filter(status='success',
                                                                           newsletter__owner=user).count()
        context["fail_send_attempt_count"] = SendAttempt.objects.filter(status='fail', newsletter__owner=user).count()
        context["all_messages"] = Message.objects.filter(owner=user)

        return context
