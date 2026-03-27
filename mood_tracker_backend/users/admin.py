from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'spotify_id', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'spotify_id')
    fieldsets = UserAdmin.fieldsets + (
        ('Spotify', {'fields': ('spotify_id', 'spotify_access_token', 'spotify_refresh_token', 'spotify_token_expires_at')}),
    )
