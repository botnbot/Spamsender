class StaffAccessMixin:
    """
        Сотрудник видит все.
        Пользователь — только свои объекты.
    """
    def filter_by_staff(self, queryset):
        user = self.request.user
        if user.is_staff:
            return queryset
        return queryset.filter(owner=user)


class OwnerQuerysetMixin(StaffAccessMixin):
    """
     Автоматическая фильтрация queryset по роли.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        return self.filter_by_staff(qs)

