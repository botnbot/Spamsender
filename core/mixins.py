from django.contrib import messages
from django.core.exceptions import PermissionDenied
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


# class RoleAccessMixin:
#     owner_field = "owner"
#     manager_group = "Managers"
#     no_access_redirect = "core:home"  # куда редиректим
#
#     def is_manager(self, user):
#         return user.groups.filter(name=self.manager_group).exists()
#
#     def is_admin(self, user):
#         return user.is_superuser
#
#     def get_object(self, queryset=None):
#         try:
#             obj = super().get_object(queryset)
#         except Http404:
#             # Если объекта нет — редирект с сообщением
#             messages.error(self.request, "Нет доступа к объекту или он не существует.")
#             return redirect(self.no_access_redirect)
#
#         user = self.request.user
#
#         if self.is_admin(user):
#             return obj
#
#         if self.is_manager(user):
#             if self.request.method in ("GET",):
#                 return obj
#             if getattr(obj, self.owner_field) != user:
#                 messages.error(self.request, "Нет доступа к редактированию чужого объекта.")
#                 return redirect(self.no_access_redirect)
#             return obj
#
#         if getattr(obj, self.owner_field) != user:
#             messages.error(self.request, "Нет доступа к этому объекту.")
#             return redirect(self.no_access_redirect)
#
#         return obj


# class RedirectOnNoAccessMixin:
#     """
#     Редирект с сообщением при отсутствии доступа или при 404.
#     """
#     no_access_redirect = "core:home"  # куда редиректить
#
#     def dispatch(self, request, *args, **kwargs):
#         try:
#             return super().dispatch(request, *args, **kwargs)
#         except (PermissionDenied, Http404):
#             messages.error(request, "Нет доступа к объекту или он не существует.")
#             return redirect(self.no_access_redirect)


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

    # --- Проверка полного доступа ---
    def _has_full_access(self):
        user = self.request.user
        if user.is_superuser:
            return True
        if self.manager_permission and user.has_perm(self.manager_permission):
            return True
        return False

    # --- НЕ фильтруем queryset для DetailView ---
    def get_queryset(self):
        return super().get_queryset()

    # --- Проверяем доступ вручную ---
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if self._has_full_access():
            return obj

        owner = getattr(obj, self.owner_field, None)
        if owner != self.request.user:
            raise PermissionDenied

        return obj

    # --- Ловим PermissionDenied и делаем редирект ---
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            messages.error(request, "Нет доступа.")
            return redirect(self.no_access_redirect)
