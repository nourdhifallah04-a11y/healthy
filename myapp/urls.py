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
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # App healthy
    path("nutrition/", include("healthy.urls")),
    #path('', include(router.urls)),
    path("", views.acceuil, name="acceuil"),
     #path('', include(router.urls)),
    path("", views.Menu, name="menu"),
     #path('', include(router.urls)),
    path("", views.acceuil, name="specialdiet"),
    #path('', include(router.urls)),
    path("", views.acceuil, name="contact"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
