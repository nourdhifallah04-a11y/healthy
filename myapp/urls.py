from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from myapp import views
from myapp.monitoring import views_monitoring

router = DefaultRouter()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name="password_reset_confirm"),
    path("password-reset-complete/", auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name="password_reset_complete"),

    # App healthy
    path("", include("myapp.users.urls")),
    path("plat/", include("myapp.plat.urls")),
    path("menu/", include("myapp.menu.urls")),
    path("commande/", include("myapp.commande.urls")),
    path("profilNutritionnel/", include("myapp.profilNutritionnel.urls")),
    path("systemeIA/", include("myapp.systemeIA.urls")),
    path("monitoring/", include("myapp.monitoring.urls")),
    path("browse/", views.unified_browse, name="unified_browse"),
    #path('', include(router.urls)),
    #path('', include(router.urls)),
    path("contact/", views.contact, name="contact"),





    path("api/", include(router.urls)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
