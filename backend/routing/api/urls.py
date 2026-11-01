from django.urls import path

from .views import analyze, geocode, health, heatmap

urlpatterns = [
    path("health", health),
    path("geocode", geocode),
    path("routes/analyze", analyze),
    path("analyses/<uuid:analysis_id>/heatmap", heatmap),
]
