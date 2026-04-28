from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from myapp import views
from myapp import views_monitoring

router = DefaultRouter()
router.register(r'clients', views.ClientViewSet)
router.register(r'plats', views.PlatViewSet)
router.register(r'menus-and-plats', views.UnifiedMenuItemViewSet, basename='unified-menu-item')
router.register(r'commandes', views.CommandeViewSet)
router.register(r'ia', views.SystemeIAViewSet)

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

    path("browse/", views.unified_browse, name="unified_browse"),
    #path('', include(router.urls)),
    #path('', include(router.urls)),
    path("contact/", views.contact, name="contact"),

    # Commande URLs
    path("panier/", views.panier, name="panier"),
    path("checkout/", views.checkout, name="checkout"),
    path("commande/confirmation/<int:commande_id>/", views.commande_confirmation, name="commande_confirmation"),
    path("mes-commandes/", views.mes_commandes, name="mes_commandes"),
    path("commande/<int:commande_id>/", views.commande_detail, name="commande_detail"),


    # Dashboard de monitoring des scores (staff uniquement)
    path("monitoring/scores/", views_monitoring.score_dashboard, name="monitoring_dashboard"),
    path("monitoring/scores/api/", views_monitoring.score_dashboard_api, name="monitoring_api"),
    path("monitoring/scores/filters-data/", views_monitoring.score_dashboard_filters_data, name="monitoring_filters_data"),
    path("monitoring/scores/reset/", views_monitoring.score_dashboard_reset, name="monitoring_reset"),

    path("api/", include(router.urls)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
