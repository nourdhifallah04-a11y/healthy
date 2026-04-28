from django.urls import include, path
from rest_framework.routers import DefaultRouter
from myapp.systemeIA import views
router = DefaultRouter()
router.register(r'ia', views.SystemeIAViewSet)

urlpatterns = [

    path("api/", include(router.urls)),
]
