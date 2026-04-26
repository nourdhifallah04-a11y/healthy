"""
Admin pour l'app users
"""
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_verified', 'created_at']
    list_filter = ['role', 'is_verified', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = (
        ('Identité', {'fields': ('username', 'email', 'first_name', 'last_name')}),
        ('Sécurité', {'fields': ('password', 'is_active', 'is_staff', 'is_superuser')}),
        ('Profil', {'fields': ('role', 'bio', 'avatar', 'is_verified')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ['created_at', 'updated_at']
