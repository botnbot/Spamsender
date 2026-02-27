from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LogoutView
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, TemplateView, ListView

from config import settings
from users.forms import RegisterForm

User = get_user_model()


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Вы вышли из системы")
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy("users:register_done")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        activation_link = self.request.build_absolute_uri(
            reverse('users:activate', kwargs={
                'uidb64': uid,
                'token': token
            })
        )

        message = render_to_string('users/email/activation_email.html', {
            'user': user,
            'activation_link': activation_link,
        })

        send_mail(
            subject='Подтверждение регистрации',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.success(
            self.request,
            "Пожалуйста, проверьте email для подтверждения регистрации."
        )

        return redirect(self.success_url)


class ActivateUserView(View):
    def get(self, request, uidb64, token):
        user = None
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            pass

        if user and not user.is_active and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(update_fields=["is_active"])

            messages.success(request, "Аккаунт активирован. Теперь вы можете войти.")
            return redirect("users:login")

        messages.error(request, "Ссылка подтверждения недействительна или истекла.")
        return redirect("users:login")


class RegisterDoneView(TemplateView):
    template_name = "users/register_done.html"


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    permission_required = "users.view_user"


class ToggleUserActiveView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.change_user"

    def handle_no_permission(self):
        messages.error(self.request, "Запрещено")
        return redirect("users:user_list")

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if user == request.user:
            messages.error(request, "Нельзя заблокировать самого себя.")
            return redirect("users:user_list")
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        status = "разблокирован" if user.is_active else "заблокирован"
        messages.success(request, f"Пользователь {user.email} {status}.")
        return redirect("users:user_list")
