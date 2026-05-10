from django.urls import include, path
from myapp.menu import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'menus', views.MenuViewSet)


urlpatterns = [

    path("", views.menu, name="menu"),
    path("list-menus/", views.list_menus, name="list_menus"),path("list-menus/", views.list_menus, name="list_menus"),
    path("ajouter-menu/", views.ajouter_menu, name="ajouter_menu"),
    path("modifier-menu/", views.modifier_menu, name="modifier_menu"),
    path("browse/", views.unified_browse, name="unified_browse"),
    path("api/", include(router.urls)),   # <-- AJOUT ESSENTIEL
]