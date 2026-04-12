from django.urls import path, include
from . import views

urlpatterns = [
        path("profil/", views.profil_list, name="profil_list"),
    
]