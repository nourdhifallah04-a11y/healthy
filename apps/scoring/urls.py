"""
URLs pour l'app scoring
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'scoring'

router = DefaultRouter()
router.register(r'scores', views.ScoreViewSet, basename='score')
router.register(r'recommendations', views.RecommendationViewSet, basename='recommendation')

urlpatterns = [
    path('', include(router.urls)),
]
