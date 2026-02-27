from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import redirect

from core.models import Newsletter


class OwnerQuerysetMixin():
    """
     Автоматическая фильтрация queryset по роли.
    """

    def is_manager(self, user):
        return user.groups.filter(name="Managers").exists()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if self.is_manager(user):
            return qs

        return qs.filter(owner=user)


class OwnerOrManagerMixin:
    """
    - Обычный пользователь → только свои объекты
    - Менеджер (по permission) → все объекты
    """

    owner_field = "owner"
    manager_permission = None

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if self.manager_permission and user.has_perm(self.manager_permission):
            return queryset
        return queryset.filter(**{self.owner_field: user})

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if self.manager_permission and user.has_perm(self.manager_permission):
            return obj
        if getattr(obj, self.owner_field) != user:
            raise PermissionDenied("Нет доступа к объекту.")
        return obj


class OwnerEditMixin:
    """
    Пользователь может редактировать/удалять только свои объекты.
    Менеджер может редактировать/удалять только свои объекты.
    """
    owner_field = "owner"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if getattr(obj, self.owner_field) != request.user:
            return HttpResponseForbidden("Нет прав на редактирование этого объекта.")
        return super().dispatch(request, *args, **kwargs)


class DisableNewsletterMixin:
    """
    Позволяет менеджеру отключать только свои рассылки.
    """
    def disable_newsletter(self, newsletter):
        if newsletter.status != Newsletter.STATUS_DISABLED:
            newsletter.status = Newsletter.STATUS_DISABLED
            newsletter.save(update_fields=['status'])
            messages.warning(self.request, "Рассылка отключена.")


class UserBlockMixin:
    """
    Проверяет, что менеджер не может заблокировать суперпользователя или другого менеджера.
    Используется для блокировки обычных пользователей.
    """
    def block_user(self, user):
        if user.is_superuser:
            raise PermissionDenied("Суперпользователя нельзя заблокировать.")
        if user.groups.filter(name="Managers").exists():
            raise PermissionDenied("Менеджера нельзя заблокировать.")

        user.is_active = False
        user.save(update_fields=["is_active"])


class RoleAccessMixin:
    owner_field = "owner"
    manager_group = "Managers"
    no_access_redirect = "core:home"  # куда редиректим

    def is_manager(self, user):
        return user.groups.filter(name=self.manager_group).exists()

    def is_admin(self, user):
        return user.is_superuser

    def get_object(self, queryset=None):
        try:
            obj = super().get_object(queryset)
        except Http404:
            # Если объекта нет — редирект с сообщением
            messages.error(self.request, "Нет доступа к объекту или он не существует.")
            return redirect(self.no_access_redirect)

        user = self.request.user

        if self.is_admin(user):
            return obj

        if self.is_manager(user):
            if self.request.method in ("GET",):
                return obj
            if getattr(obj, self.owner_field) != user:
                messages.error(self.request, "Нет доступа к редактированию чужого объекта.")
                return redirect(self.no_access_redirect)
            return obj

        if getattr(obj, self.owner_field) != user:
            messages.error(self.request, "Нет доступа к этому объекту.")
            return redirect(self.no_access_redirect)

        return obj


class RedirectOnNoAccessMixin:
    """
    Редирект с сообщением при отсутствии доступа или при 404.
    """
    no_access_redirect = "core:home"  # куда редиректить

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except (PermissionDenied, Http404):
            messages.error(request, "Нет доступа к объекту или он не существует.")
            return redirect(self.no_access_redirect)
