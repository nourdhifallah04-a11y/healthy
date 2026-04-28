from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from myapp import views

router = DefaultRouter()


urlpatterns = [
 
    # Commande URLs
    path("panier/", views.panier, name="panier"),
    path("checkout/", views.checkout, name="checkout"),
    path("commande/confirmation/<int:commande_id>/", views.commande_confirmation, name="commande_confirmation"),
    path("mes-commandes/", views.mes_commandes, name="mes_commandes"),
    path("commande/<int:commande_id>/", views.commande_detail, name="commande_detail"),
    path('', include(router.urls))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
