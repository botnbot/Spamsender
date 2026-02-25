from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden


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


class OwnerEditMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if request.user.groups.filter(name="Managers").exists():
            if obj.owner != request.user:
                return HttpResponseForbidden()

        if obj.owner != request.user:
            return HttpResponseForbidden()

        return super().dispatch(request, *args, **kwargs)


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