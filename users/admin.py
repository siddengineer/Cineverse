from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'favorite_genres', 'date_joined']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('CineVerse Profile', {'fields': ('bio', 'avatar', 'favorite_genres', 'taste_profile')}),
    )
