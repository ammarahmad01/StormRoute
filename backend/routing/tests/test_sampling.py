from datetime import datetime, timezone

from routing.services.sampling import sample_route


def test_sampling_includes_interval_points_and_final_point():
    checkpoints = sample_route([(0, 0), (0, 1)], 100, 120, 25, datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert [point.distance_miles for point in checkpoints] == [0, 25, 50, 75, 100]
    assert sum(point.segment_miles for point in checkpoints) == 100
    assert checkpoints[-1].eta.isoformat() == "2026-01-01T02:00:00+00:00"


def test_short_route_has_start_and_end():
    checkpoints = sample_route([(0, 0), (0, 1)], 5, 10, 25, datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert len(checkpoints) == 2
    assert sum(point.segment_miles for point in checkpoints) == 5

