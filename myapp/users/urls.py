from django.urls import include, path
from myapp.users import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'clients', views.ClientViewSet)


urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    # Auth
    path(
        "login/",
        views.connex,
        name="login",
    ),
    path("administrateur/", views.login_admin, name="administrateur"),
    path("profil-nutritionnel/", views.profilNutritionnel, name="profilNutritionnel"),
    path("", views.accueil, name="accueil"),
    path("", include(router.urls))
]

