from django.urls import path
from myapp.monitoring import views_monitoring


urlpatterns = [
    # Dashboard de monitoring des scores (staff uniquement)
    path("scores/", views_monitoring.score_dashboard, name="monitoring_dashboard"),
    path("scores/api/", views_monitoring.score_dashboard_api, name="monitoring_api"),
    path("scores/filters-data/", views_monitoring.score_dashboard_filters_data, name="monitoring_filters_data"),
    path("scores/reset/", views_monitoring.score_dashboard_reset, name="monitoring_reset"),

]
