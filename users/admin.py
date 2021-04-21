from django.contrib import admin  # noqa:F401
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


class AuthorAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'is_staff', 'is_active',)
    list_filter = ('username', 'email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Description', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)


admin.site.unregister(User)
admin.site.register(User, AuthorAdmin)
