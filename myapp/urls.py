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

    # Auth
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="acceuil/connex.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

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
    
    # API endpoints
    path("api/profil-nutritionnel/creer/", views.CreerProfilNutritionnelView.as_view(), name="creer_profil_nutritionnel"),
    path("api/profil-nutritionnel/obtenir/", views.ObtenirProfilNutritionnelView.as_view(), name="obtenir_profil_nutritionnel"),
    path("api/profil-nutritionnel/supprimer/", views.SupprimerProfilNutritionnelView.as_view(), name="supprimer_profil_nutritionnel"),
    path("api/", include(router.urls)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
