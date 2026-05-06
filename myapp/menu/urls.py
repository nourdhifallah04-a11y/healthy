from django.urls import include, path
from myapp.menu import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'menus', views.MenuViewSet)


urlpatterns = [

    path("", views.menu, name="menu"),
    path("browse/", views.unified_browse, name="unified_browse"),
    path("api/", include(router.urls)),   # <-- AJOUT ESSENTIEL
]