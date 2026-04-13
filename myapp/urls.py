from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from myapp import views


router = DefaultRouter()
router.register(r'clients', views.ClientViewSet)
router.register(r'plats', views.PlatViewSet)
router.register(r'menus', views.MenuViewSet)
router.register(r'commandes', views.CommandeViewSet)
router.register(r'ia', views.SystemeIAViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
path('register/', views.register, name='register'),
    # Auth
    path(
        "login/",
        views.connex,
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name="password_reset_confirm"),
    path("password-reset-complete/", auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name="password_reset_complete"),

    # App healthy
    path("nutrition/", include("healthy.urls")),
    #path('', include(router.urls)),
    path("", views.acceuil, name="acceuil"),
     #path('', include(router.urls)),
    path("menu/", views.menu, name="menu"),
     #path('', include(router.urls)),
    path("specialdiet/", views.specialdiet, name="specialdiet"),
    #path('', include(router.urls)),
    path("contact/", views.contact, name="contact"),
    path("profil-nutritionnel/", views.profilNutritionnel, name="profilNutritionnel"),
    path("list_plats/", views.list_plats, name="list_plats"),
    path("ajouter-plat/", views.ajouter_plat, name="ajouter_plat"),
    path("modifier-plat/", views.modifier_plat, name="modifier_plat"),
    path("administrateur/", views.login_admin, name="administrateur"),

    # API endpoints
    path("api/profil-nutritionnel/creer/", views.CreerProfilNutritionnelView.as_view(), name="creer_profil_nutritionnel"),
    path("api/profil-nutritionnel/obtenir/", views.ObtenirProfilNutritionnelView.as_view(), name="obtenir_profil_nutritionnel"),
    path("api/profil-nutritionnel/supprimer/", views.SupprimerProfilNutritionnelView.as_view(), name="supprimer_profil_nutritionnel"),
    path("api/profil-nutritionnel/recommander-plats/", views.RecommenderPlatsView.as_view(), name="recommander_plats"),
    path("api/", include(router.urls)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
