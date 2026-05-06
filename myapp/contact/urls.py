from django.urls import path
from myapp.contact import views
urlpatterns = [
    path("", views.contact, name="contact"),

]
