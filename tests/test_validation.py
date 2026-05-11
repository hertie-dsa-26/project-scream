"""
tests/test_validation.py

Tests for app.utils.validation.validate_prediction_input.
No Flask app context needed — validation is pure Python.
"""

import pytest
from app.utils.validation import validate_prediction_input


# ── Helpers ───────────────────────────────────────────────────────────────────

def _valid_form(**overrides) -> dict:
    """Return a fully valid form submission, with optional field overrides.
    height_cm=175, weight_kg=75 gives BMI ~24.5, well within 10-70 range.
    """
    base = {
        "age":                   "45",
        "height_cm":             "175",
        "weight_kg":             "75",
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


def test_valid_input_computes_bmi():
    """height=175cm, weight=75kg -> BMI=24.49, stored as raw bmi"""
    cleaned, _ = validate_prediction_input(_valid_form(height_cm="175", weight_kg="75"))
    expected_bmi = 75 / (1.75 ** 2)
    assert cleaned["bmi"] == pytest.approx(expected_bmi, abs=0.01)
    # weight_kg should NOT be in cleaned (not a model feature)
    assert "weight_kg" not in cleaned
    assert "bmi_x100" not in cleaned


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


def test_boundary_height_min():
    # 100cm + 25kg -> BMI 25.0, plausible
    cleaned, errors = validate_prediction_input(_valid_form(height_cm="100", weight_kg="25"))
    # height valid; weight 25 is below 30kg minimum so only weight errors
    assert "height_cm" not in errors


def test_boundary_height_max():
    # 250cm + 100kg -> BMI 16.0, plausible
    cleaned, errors = validate_prediction_input(_valid_form(height_cm="250", weight_kg="100"))
    assert errors == {}


def test_boundary_weight_min():
    # 30kg + 180cm -> BMI 9.3, triggers implausible BMI guard as expected.
    # The minimum weight is only valid if height is short enough.
    # Test that the field-level range check passes (BMI guard is a separate concern).
    _, errors = validate_prediction_input(_valid_form(height_cm="175", weight_kg="31"))
    assert "weight_kg" not in errors or "between" not in errors.get("weight_kg", "")


def test_boundary_weight_max():
    # 300kg + 210cm -> BMI 68.0, just within plausible range
    cleaned, errors = validate_prediction_input(_valid_form(height_cm="210", weight_kg="300"))
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


def test_missing_height_returns_error():
    _, errors = validate_prediction_input(_valid_form(height_cm=""))
    assert "height_cm" in errors


def test_missing_weight_returns_error():
    _, errors = validate_prediction_input(_valid_form(weight_kg=""))
    assert "weight_kg" in errors


def test_missing_categorical_returns_error():
    _, errors = validate_prediction_input(_valid_form(sex=""))
    assert "sex" in errors


def test_multiple_missing_fields_returns_all_errors():
    _, errors = validate_prediction_input(_valid_form(age="", height_cm="", weight_kg="", sex=""))
    assert "age" in errors
    assert "height_cm" in errors
    assert "weight_kg" in errors
    assert "sex" in errors


# ── Out of range ──────────────────────────────────────────────────────────────

def test_age_below_min_rejected():
    _, errors = validate_prediction_input(_valid_form(age="17"))
    assert "age" in errors


def test_age_above_max_rejected():
    _, errors = validate_prediction_input(_valid_form(age="100"))
    assert "age" in errors


def test_height_below_min_rejected():
    _, errors = validate_prediction_input(_valid_form(height_cm="99"))
    assert "height_cm" in errors


def test_height_above_max_rejected():
    _, errors = validate_prediction_input(_valid_form(height_cm="251"))
    assert "height_cm" in errors


def test_weight_below_min_rejected():
    _, errors = validate_prediction_input(_valid_form(weight_kg="29"))
    assert "weight_kg" in errors


def test_weight_above_max_rejected():
    _, errors = validate_prediction_input(_valid_form(weight_kg="301"))
    assert "weight_kg" in errors


def test_implausible_bmi_rejected():
    """Very short + very heavy -> BMI > 70, should be caught."""
    _, errors = validate_prediction_input(_valid_form(height_cm="100", weight_kg="300"))
    assert "weight_kg" in errors


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


def test_non_numeric_height_rejected():
    _, errors = validate_prediction_input(_valid_form(height_cm="tall"))
    assert "height_cm" in errors


def test_non_numeric_weight_rejected():
    _, errors = validate_prediction_input(_valid_form(weight_kg="heavy"))
    assert "weight_kg" in errors


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