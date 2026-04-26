"""
URL Configuration pour Healthy IA
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/v1/users/', include('apps.users.urls', namespace='users')),
    path('api/v1/nutrition/', include('apps.nutrition.urls', namespace='nutrition')),
    path('api/v1/scoring/', include('apps.scoring.urls', namespace='scoring')),
    path('api/v1/orders/', include('apps.orders.urls', namespace='orders')),
    path('api/v1/', include('apps.core.urls', namespace='core')),
]

# Servir les fichiers media et static en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        urlpatterns = [path('__debug__/', include('debug_toolbar.urls'))] + urlpatterns
