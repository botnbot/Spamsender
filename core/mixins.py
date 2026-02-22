class OwnerQuerysetMixin():
    """
     Автоматическая фильтрация queryset по роли.
    """

    def is_manager(self, user):
        return user.groups.filter(name="Managers").exists()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff or self.is_manager(user):
            return qs

        return qs.filter(owner=user)


class OwnerEditMixin:

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)
