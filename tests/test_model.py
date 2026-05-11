"""
tests/test_model.py

Tests for app.utils.model — loading, prediction output shape/types,
and edge case handling.

Requires the pipeline artifacts to be present at app/model/artifacts/.
"""

import pytest
from app.utils.model import load_model, predict, PredictResult


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def loaded_model():
    """Load SVM artifacts once for the whole module."""
    load_model()


def _valid_inputs(**overrides) -> dict:
    """Return a valid cleaned input dict as produced by validation.py."""
    base = {
        "general_health":        3.0,
        "any_physical_activity": 1.0,
        "sex":                   1.0,
        "age_imputed":           45.0,
        "bmi":                   27.5,   # raw BMI, not bmi_x100
        "education_level":       4.0,
        "income_level":          5.0,
        "smoking_status":        4.0,
        "any_alcohol_past_30d":  1.0,
    }
    base.update(overrides)
    return base


# ── Return type and shape ─────────────────────────────────────────────────────

def test_predict_returns_predict_result():
    result = predict(_valid_inputs())
    assert isinstance(result, PredictResult)


def test_predict_result_has_all_fields():
    result = predict(_valid_inputs())
    assert hasattr(result, "probability")
    assert hasattr(result, "probability_pct")
    assert hasattr(result, "risk_category")
    assert hasattr(result, "suggestions")
    assert hasattr(result, "input_features")


def test_probability_in_unit_interval():
    result = predict(_valid_inputs())
    assert 0.0 <= result.probability <= 1.0


def test_probability_pct_in_percentage_range():
    result = predict(_valid_inputs())
    assert 0.0 <= result.probability_pct <= 100.0


def test_probability_pct_matches_probability():
    result = predict(_valid_inputs())
    assert result.probability_pct == pytest.approx(result.probability * 100, abs=0.1)


def test_risk_category_is_valid_string():
    result = predict(_valid_inputs())
    assert result.risk_category in {"low", "moderate", "high"}


def test_suggestions_is_list():
    result = predict(_valid_inputs())
    assert isinstance(result.suggestions, list)


def test_suggestions_always_has_diet_tip():
    """Diet tip is always appended regardless of user inputs."""
    result = predict(_valid_inputs())
    static_tips = [s for s in result.suggestions if s.get("static")]
    assert len(static_tips) >= 1


def test_input_features_contains_user_inputs():
    inputs = _valid_inputs()
    result = predict(inputs)
    for key in inputs:
        assert key in result.input_features


# ── Risk category thresholds ──────────────────────────────────────────────────

def test_low_risk_category():
    """Young, healthy profile should tend toward low risk."""
    result = predict(_valid_inputs(
        age_imputed=25.0, bmi=20.0,
        general_health=1.0, any_physical_activity=1.0,
        smoking_status=4.0, income_level=7.0,
    ))
    assert result.risk_category in {"low", "moderate"}


def test_high_risk_category():
    """Older, high-risk profile should tend toward high risk."""
    result = predict(_valid_inputs(
        age_imputed=75.0, bmi=40.0,
        general_health=5.0, any_physical_activity=2.0,
        smoking_status=1.0, income_level=1.0,
    ))
    assert result.risk_category in {"moderate", "high"}


# ── Actionable suggestions ────────────────────────────────────────────────────

def test_inactive_user_gets_activity_suggestion():
    result = predict(_valid_inputs(any_physical_activity=2.0))
    non_static = [s for s in result.suggestions if not s.get("static")]
    labels = [s["label"] for s in non_static]
    assert any("activ" in l.lower() for l in labels)


def test_active_user_gets_no_activity_suggestion():
    result = predict(_valid_inputs(any_physical_activity=1.0))
    non_static = [s for s in result.suggestions if not s.get("static")]
    labels = [s["label"] for s in non_static]
    assert not any("activ" in l.lower() for l in labels)


def test_smoker_always_gets_quit_suggestion():
    """
    Quit smoking suggestion must always appear for current smokers (codes 1 and 2).
    It is treated as static (no delta shown) since the model signal is unreliable
    for this feature — but it must still appear in the suggestions list.
    """
    for code in [1.0, 2.0]:
        result = predict(_valid_inputs(smoking_status=code))
        # Check all suggestions including static ones
        labels = [s["label"].lower() for s in result.suggestions]
        assert any("smok" in l for l in labels), (
            f"Expected quit-smoking suggestion for smoking_status={code}, got: {labels}"
        )


def test_suggestion_delta_is_positive():
    """Counterfactual improvement should always reduce risk."""
    result = predict(_valid_inputs(any_physical_activity=2.0))
    for s in result.suggestions:
        if not s.get("static") and "delta_pct" in s:
            assert s["delta_pct"] > 0


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_boundary_age_min():
    result = predict(_valid_inputs(age_imputed=18.0))
    assert isinstance(result, PredictResult)


def test_boundary_age_max():
    result = predict(_valid_inputs(age_imputed=99.0))
    assert isinstance(result, PredictResult)


def test_boundary_bmi_min():
    result = predict(_valid_inputs(bmi=10.0))
    assert isinstance(result, PredictResult)


def test_boundary_bmi_max():
    result = predict(_valid_inputs(bmi=70.0))
    assert isinstance(result, PredictResult)


def test_predict_is_deterministic():
    """Same inputs should always return the same probability."""
    inputs = _valid_inputs()
    r1 = predict(inputs)
    r2 = predict(inputs)
    assert r1.probability == r2.probability