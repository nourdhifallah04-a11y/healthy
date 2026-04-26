from django.contrib import admin
from .models import SystemeIA


@admin.register(SystemeIA)
class SystemeIAAdmin(admin.ModelAdmin):
    list_display = ('nom', 'version', 'est_actif', 'created_at')
    list_filter = ('est_actif', 'created_at')
    search_fields = ('nom', 'version')
    readonly_fields = ('created_at',)
