from rest_framework import serializers


class PlaceSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=255)
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lon = serializers.FloatField(min_value=-180, max_value=180)


class AnalyzeSerializer(serializers.Serializer):
    origin = PlaceSerializer()
    destination = PlaceSerializer()
    departure_time = serializers.DateTimeField()
    load_weight_lb = serializers.IntegerField(min_value=0, max_value=80_000)
    sample_interval_miles = serializers.ChoiceField(choices=(10, 25, 50), default=25)

    def validate(self, attrs):
        origin, destination = attrs["origin"], attrs["destination"]
        if origin["lat"] == destination["lat"] and origin["lon"] == destination["lon"]:
            raise serializers.ValidationError({"destination": ["Origin and destination must differ."]})
        return attrs

