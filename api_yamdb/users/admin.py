from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    search_fields = ('email', 'first_name', 'last_name')
    list_display = ('username', 'email', 'role', 'date_joined')
    list_editable = ('role',)
