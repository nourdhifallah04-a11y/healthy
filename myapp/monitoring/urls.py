from django.urls import path
from myapp.monitoring import views_monitoring


urlpatterns = [
    # Dashboard de monitoring des scores (staff uniquement)
    path("monitoring/scores/", views_monitoring.score_dashboard, name="monitoring_dashboard"),
    path("monitoring/scores/api/", views_monitoring.score_dashboard_api, name="monitoring_api"),
    path("monitoring/scores/filters-data/", views_monitoring.score_dashboard_filters_data, name="monitoring_filters_data"),
    path("monitoring/scores/reset/", views_monitoring.score_dashboard_reset, name="monitoring_reset"),

]
