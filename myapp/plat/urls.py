from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from myapp.plat import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'plats', views.PlatViewSet)


urlpatterns = [
    path("specialdiet/", views.specialdiet, name="specialdiet"),
    path("list_plats/", views.list_plats, name="list_plats"),
    path("ajouter-plat/", views.ajouter_plat, name="ajouter_plat"),
    path("modifier-plat/", views.modifier_plat, name="modifier_plat"),

    path("api/profil-nutritionnel/recommander-menu/", views.RecommenderPlatsView.as_view(), name="recommander_plats"),
    path("api/profil-nutritionnel/recommander-plats/", views.RecommenderPlatsDirectView.as_view(), name="recommander_plats_direct"),
    path("api/profil-nutritionnel/recommander-n8n/job-status/", views.JobStatusView.as_view(), name="recommander_n8n_job_status"),
    path("api/profil-nutritionnel/recommander-n8n/", views.RecommenderIAProfilNutritionnelWebhookView.as_view(), name="recommander_n8n_webhook"),
    path("api/", include(router.urls))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
