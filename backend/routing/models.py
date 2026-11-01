import uuid

from django.db import models


class Analysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    origin_label = models.CharField(max_length=255)
    origin_lat = models.FloatField()
    origin_lon = models.FloatField()
    dest_label = models.CharField(max_length=255)
    dest_lat = models.FloatField()
    dest_lon = models.FloatField()
    departure_utc = models.DateTimeField()
    load_weight_lb = models.PositiveIntegerField()
    interval_miles = models.PositiveSmallIntegerField()
    result_json = models.JSONField()
    heatmap_json = models.JSONField(null=True, blank=True)

