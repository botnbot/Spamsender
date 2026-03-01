from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect


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


class OwnerOrManagerMixin:
    """
    - superuser видит всё
    - пользователь с manager_permission видит всё
    - обычный пользователь видит только свои объекты
    При отсутствии доступа - редирект с сообщением.
    """

    manager_permission = None
    owner_field = "owner"
    no_access_redirect = "core:home"

    def _has_full_access(self):
        user = self.request.user
        if user.is_superuser:
            return True
        if self.manager_permission and user.has_perm(self.manager_permission):
            return True
        return False

    def get_queryset(self):
        qs = super().get_queryset()

        if self._has_full_access():
            return qs

        return qs.filter(**{self.owner_field: self.request.user})

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if self._has_full_access():
            return obj

        owner = getattr(obj, self.owner_field, None)
        if owner != self.request.user:
            raise PermissionDenied

        return obj

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            messages.error(request, "Нет доступа.")
            return redirect(self.no_access_redirect)
