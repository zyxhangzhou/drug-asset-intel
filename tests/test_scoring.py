import pytest

from intel import scoring
from intel.enums import EventCertainty, EventImportance, RightsStatus, Stage

CFG = scoring.ScoringConfig.load()
FULL = dict.fromkeys(scoring.DIMENSIONS, 4)


def test_missing_dimension_widens_range():
    scores = FULL | {"clinical": None}
    assert scoring.conservative(scores, CFG.weights) == 80.0
    assert scoring.optimistic(scores, CFG.weights) == 100.0


def test_weights_are_normalized():
    raw = {"buyer_fit": 3, "stage_match": 2, "clinical": 2, "catalyst": 1.5, "dealability": 1.5}
    assert scoring.normalize_weights(raw) == CFG.weights
    with pytest.raises(ValueError):
        scoring.normalize_weights(dict.fromkeys(scoring.DIMENSIONS, 0))


def test_later_stage_is_not_better_by_default():
    assert scoring.stage_match(Stage.approved, Stage.phase2, Stage.phase3) == 0
    assert scoring.stage_match(Stage.filed, Stage.phase2, Stage.phase3) == 2
    assert scoring.stage_match(Stage.phase2_3, Stage.phase2, Stage.phase3) == 4
    assert scoring.stage_match(Stage.phase1_2, Stage.phase2, Stage.phase3) == 2
    assert scoring.stage_match(Stage.unknown, Stage.phase2, Stage.phase3) is None


def test_ev_tier_and_rights_cap():
    assert scoring.dealability(2.5e9, None, CFG.ev_tiers) == 3
    assert scoring.dealability(1e9, RightsStatus.partial, CFG.ev_tiers) == 3
    assert scoring.dealability(1e9, RightsStatus.restricted, CFG.ev_tiers) == 1
    assert scoring.dealability(5e10, None, CFG.ev_tiers) == 0
    assert scoring.dealability(None, None, CFG.ev_tiers) is None


def test_catalyst_matrix():
    assert scoring.catalyst_score(EventImportance.high, EventCertainty.estimated) == 3
    assert scoring.catalyst_score(EventImportance.medium, EventCertainty.disclosed) == 3
    assert scoring.catalyst_score(None, None) == 0


def test_ties_compare_dimensions_by_weight():
    # Same conservative score: the heavier dimension decides before the ticker does.
    a = {"buyer_fit": 3, "stage_match": 4, "clinical": 2, "catalyst": 4, "dealability": 2}
    b = {"buyer_fit": 3, "stage_match": 4, "clinical": 2, "catalyst": 3, "dealability": 3}
    total = scoring.conservative(a, CFG.weights)
    assert total == scoring.conservative(b, CFG.weights)
    keys = [
        scoring.rank_key(total, a, CFG.weights, "ZZZ"),
        scoring.rank_key(total, b, CFG.weights, "AAA"),
    ]
    assert keys[0] < keys[1]
    # A missing dimension ranks below a scored 0.
    assert scoring.rank_key(50, {"buyer_fit": 0}, CFG.weights, "B") < scoring.rank_key(
        50, {"buyer_fit": None}, CFG.weights, "A"
    )
