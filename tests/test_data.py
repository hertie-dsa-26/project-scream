"""
tests/test_data.py

Tests for app.utils.data — benchmark and stats computation.
Requires a Flask app context since load_brfss uses current_app.config.
Tests that require the BRFSS parquet are skipped automatically on CI
where the data file is not present.
"""

import pytest
from pathlib import Path
from app import create_app
from app.utils.data import (
    get_benchmarks,
    get_overall_stats,
    load_references,
    FEATURE_LABELS,
    CATEGORICAL_LABELS,
    _BENCHMARK_FEATURES,
)


# ── Skip marker ───────────────────────────────────────────────────────────────

def _data_available() -> bool:
    """Check whether the BRFSS parquet exists on this machine."""
    from config import DevConfig
    path = Path(DevConfig.DATA_DIR) / "subsets" / "brfss2024_subset.parquet"
    return path.exists()


requires_data = pytest.mark.skipif(
    not _data_available(),
    reason="BRFSS parquet not present — skipping data-dependent tests",
)


# ── App context fixture ───────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture(scope="module")
def app_context(app):
    with app.app_context():
        yield


# ── get_benchmarks ────────────────────────────────────────────────────────────

@requires_data
def test_benchmarks_returns_dict(app_context):
    result = get_benchmarks()
    assert isinstance(result, dict)


@requires_data
def test_benchmarks_has_diabetic_and_non_diabetic_keys(app_context):
    result = get_benchmarks()
    assert "diabetic" in result
    assert "non_diabetic" in result


@requires_data
def test_benchmarks_diabetic_values_are_floats(app_context):
    result = get_benchmarks()
    for val in result["diabetic"].values():
        assert isinstance(val, float)


@requires_data
def test_benchmarks_covers_expected_features(app_context):
    result = get_benchmarks()
    for feature in _BENCHMARK_FEATURES:
        assert feature in result["diabetic"], f"{feature} missing from diabetic benchmarks"
        assert feature in result["non_diabetic"], f"{feature} missing from non_diabetic benchmarks"


@requires_data
def test_benchmarks_diabetic_age_higher_than_non_diabetic(app_context):
    """Diabetic respondents should on average be older — well-established in literature."""
    result = get_benchmarks()
    assert result["diabetic"]["age_imputed"] > result["non_diabetic"]["age_imputed"]


@requires_data
def test_benchmarks_diabetic_bmi_higher_than_non_diabetic(app_context):
    """Diabetic respondents should on average have higher BMI."""
    result = get_benchmarks()
    assert result["diabetic"]["bmi_x100"] > result["non_diabetic"]["bmi_x100"]


@requires_data
def test_benchmarks_is_cached(app_context):
    """Calling get_benchmarks twice should return the same object (cached)."""
    r1 = get_benchmarks()
    r2 = get_benchmarks()
    assert r1 is r2


# ── get_overall_stats ─────────────────────────────────────────────────────────

@requires_data
def test_overall_stats_returns_dict(app_context):
    result = get_overall_stats()
    assert isinstance(result, dict)


@requires_data
def test_overall_stats_covers_expected_features(app_context):
    result = get_overall_stats()
    for feature in _BENCHMARK_FEATURES:
        assert feature in result, f"{feature} missing from overall stats"


@requires_data
def test_overall_stats_values_are_floats(app_context):
    result = get_overall_stats()
    for val in result.values():
        assert isinstance(val, float)


@requires_data
def test_overall_age_within_plausible_range(app_context):
    result = get_overall_stats()
    assert 18.0 <= result["age_imputed"] <= 99.0


@requires_data
def test_overall_bmi_x100_within_plausible_range(app_context):
    result = get_overall_stats()
    # BMI stored as bmi * 100, so 1000–7000 is BMI 10–70
    assert 1000.0 <= result["bmi_x100"] <= 7000.0


# ── load_references ───────────────────────────────────────────────────────────

@requires_data
def test_references_returns_list(app_context):
    refs = load_references()
    assert isinstance(refs, list)


@requires_data
def test_references_not_empty(app_context):
    refs = load_references()
    assert len(refs) > 0


@requires_data
def test_references_have_required_fields(app_context):
    refs = load_references()
    for ref in refs:
        assert "id" in ref
        assert "title" in ref
        assert "authors" in ref
        assert "year" in ref


@requires_data
def test_references_no_todo_placeholders(app_context):
    """All TODO placeholders should have been filled in."""
    refs = load_references()
    for ref in refs:
        for val in ref.values():
            if isinstance(val, str):
                assert "TODO" not in val, f"Unfilled TODO in reference '{ref['id']}': {val}"


@requires_data
def test_references_is_cached(app_context):
    r1 = load_references()
    r2 = load_references()
    assert r1 is r2


# ── Label dictionaries ────────────────────────────────────────────────────────

def test_feature_labels_covers_all_benchmark_features():
    for feature in _BENCHMARK_FEATURES:
        assert feature in FEATURE_LABELS, f"{feature} missing from FEATURE_LABELS"


def test_categorical_labels_values_are_strings():
    for feature, mapping in CATEGORICAL_LABELS.items():
        for code, label in mapping.items():
            assert isinstance(label, str), f"Label for {feature}={code} is not a string"