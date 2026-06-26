from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Livro, User


class CustomUserAdmin(UserAdmin):
    """Admin do usuário customizado (login por e-mail)."""

    list_display = ('email', 'username', 'is_staff', 'is_active')
    ordering = ('email',)


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'user', 'date_added')
    list_filter = ('user',)
    search_fields = ('title', 'author')


admin.site.register(User, CustomUserAdmin)
