from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path("api/profil-nutritionnel/creer/", views.CreerProfilNutritionnelView.as_view(), name="creer_profil_nutritionnel"),
    path("api/profil-nutritionnel/obtenir/", views.ObtenirProfilNutritionnelView.as_view(), name="obtenir_profil_nutritionnel"),
    path("api/profil-nutritionnel/supprimer/", views.SupprimerProfilNutritionnelView.as_view(), name="supprimer_profil_nutritionnel"),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
