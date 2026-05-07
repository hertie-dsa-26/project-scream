"""
tests/test_validation.py

Tests for app.utils.validation.validate_prediction_input.
No Flask app context needed — validation is pure Python.
"""

import pytest
from app.utils.validation import validate_prediction_input


# ── Helpers ───────────────────────────────────────────────────────────────────

def _valid_form(**overrides) -> dict:
    """Return a fully valid form submission, with optional field overrides."""
    base = {
        "age":                   "45",
        "bmi":                   "27.5",
        "sex":                   "1",
        "general_health":        "3",
        "education_level":       "4",
        "income_level":          "5",
        "smoking_status":        "4",
        "any_physical_activity": "1",
        "any_alcohol_past_30d":  "1",
    }
    base.update(overrides)
    return base


# ── Happy path ────────────────────────────────────────────────────────────────

def test_valid_input_passes():
    cleaned, errors = validate_prediction_input(_valid_form())
    assert errors == {}
    assert cleaned is not None


def test_valid_input_maps_age_correctly():
    cleaned, _ = validate_prediction_input(_valid_form(age="52"))
    assert cleaned["age_imputed"] == 52.0


def test_valid_input_scales_bmi():
    cleaned, _ = validate_prediction_input(_valid_form(bmi="27.5"))
    assert cleaned["bmi_x100"] == pytest.approx(2750.0)


def test_valid_input_casts_categoricals_to_float():
    cleaned, _ = validate_prediction_input(_valid_form(sex="2"))
    assert cleaned["sex"] == 2.0


def test_boundary_age_min():
    cleaned, errors = validate_prediction_input(_valid_form(age="18"))
    assert errors == {}
    assert cleaned["age_imputed"] == 18.0


def test_boundary_age_max():
    cleaned, errors = validate_prediction_input(_valid_form(age="99"))
    assert errors == {}


def test_boundary_bmi_min():
    cleaned, errors = validate_prediction_input(_valid_form(bmi="10"))
    assert errors == {}


def test_boundary_bmi_max():
    cleaned, errors = validate_prediction_input(_valid_form(bmi="70"))
    assert errors == {}


def test_all_income_levels_valid():
    for level in range(1, 8):  # 1–7 only, pipeline doesn't know 8
        _, errors = validate_prediction_input(_valid_form(income_level=str(level)))
        assert errors == {}, f"income_level={level} should be valid"


def test_all_education_levels_valid():
    for level in range(1, 5):  # 1–4 only, pipeline doesn't know 5–6
        _, errors = validate_prediction_input(_valid_form(education_level=str(level)))
        assert errors == {}, f"education_level={level} should be valid"


# ── Missing fields ────────────────────────────────────────────────────────────

def test_missing_age_returns_error():
    _, errors = validate_prediction_input(_valid_form(age=""))
    assert "age" in errors


def test_missing_bmi_returns_error():
    _, errors = validate_prediction_input(_valid_form(bmi=""))
    assert "bmi" in errors


def test_missing_categorical_returns_error():
    _, errors = validate_prediction_input(_valid_form(sex=""))
    assert "sex" in errors


def test_multiple_missing_fields_returns_all_errors():
    _, errors = validate_prediction_input(_valid_form(age="", bmi="", sex=""))
    assert "age" in errors
    assert "bmi" in errors
    assert "sex" in errors


# ── Out of range ──────────────────────────────────────────────────────────────

def test_age_below_min_rejected():
    _, errors = validate_prediction_input(_valid_form(age="17"))
    assert "age" in errors


def test_age_above_max_rejected():
    _, errors = validate_prediction_input(_valid_form(age="100"))
    assert "age" in errors


def test_bmi_below_min_rejected():
    _, errors = validate_prediction_input(_valid_form(bmi="9.9"))
    assert "bmi" in errors


def test_bmi_above_max_rejected():
    _, errors = validate_prediction_input(_valid_form(bmi="70.1"))
    assert "bmi" in errors


# ── Invalid category codes ────────────────────────────────────────────────────

def test_income_level_8_rejected():
    """Pipeline was not trained on income_level=8."""
    _, errors = validate_prediction_input(_valid_form(income_level="8"))
    assert "income_level" in errors


def test_education_level_5_rejected():
    """Pipeline was not trained on education_level=5."""
    _, errors = validate_prediction_input(_valid_form(education_level="5"))
    assert "education_level" in errors


def test_education_level_6_rejected():
    """Pipeline was not trained on education_level=6."""
    _, errors = validate_prediction_input(_valid_form(education_level="6"))
    assert "education_level" in errors


def test_invalid_sex_code_rejected():
    _, errors = validate_prediction_input(_valid_form(sex="3"))
    assert "sex" in errors


def test_invalid_general_health_rejected():
    _, errors = validate_prediction_input(_valid_form(general_health="6"))
    assert "general_health" in errors


# ── Type safety ───────────────────────────────────────────────────────────────

def test_non_numeric_age_rejected():
    _, errors = validate_prediction_input(_valid_form(age="forty-five"))
    assert "age" in errors


def test_non_numeric_bmi_rejected():
    _, errors = validate_prediction_input(_valid_form(bmi="normal"))
    assert "bmi" in errors


def test_non_numeric_categorical_rejected():
    _, errors = validate_prediction_input(_valid_form(sex="male"))
    assert "sex" in errors


def test_float_categorical_rejected():
    """Categorical codes must be whole numbers — 1.5 is not a valid code."""
    _, errors = validate_prediction_input(_valid_form(sex="1.5"))
    assert "sex" in errors


# ── Return shape ──────────────────────────────────────────────────────────────

def test_on_error_cleaned_is_none():
    cleaned, errors = validate_prediction_input(_valid_form(age="999"))
    assert cleaned is None
    assert errors != {}


def test_on_success_errors_is_empty():
    cleaned, errors = validate_prediction_input(_valid_form())
    assert cleaned is not None
    assert errors == {}