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