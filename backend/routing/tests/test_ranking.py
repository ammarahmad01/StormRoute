from routing.services.ranking import RiskPoint, rank_summaries, summarize
from routing.services.risk import RiskLevel, overall_risk


def summary(level, miles, duration=100):
    return summarize([RiskPoint(level, miles)], duration, miles)


def test_lexicographic_ranking_and_no_travel_tier():
    summaries = [
        summary(RiskLevel.SEVERE, 10, 50),
        summary(RiskLevel.HIGH, 10, 500),
        summary(RiskLevel.NO_TRAVEL, 1, 1),
    ]
    assert rank_summaries(summaries) == [1, 0, 2]


def test_heavy_load_flips_recommendation():
    route_b = summarize([RiskPoint(RiskLevel.SEVERE, 10), RiskPoint(RiskLevel.LOW, 90)], 80, 100)
    route_a_light_risk = overall_risk(40, 0, 0, 20_000)
    route_a_heavy_risk = overall_risk(40, 0, 0, 45_000)
    route_a_light = summarize([RiskPoint(route_a_light_risk.overall, 100)], 100, 100)
    route_a_heavy = summarize([RiskPoint(route_a_heavy_risk.overall, 100)], 100, 100)

    assert rank_summaries([route_a_light, route_b])[0] == 0
    assert rank_summaries([route_a_heavy, route_b])[0] == 1
