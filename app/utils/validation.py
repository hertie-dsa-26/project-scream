"""
Input validation for the diabetes risk prediction form.

validate_prediction_input(form_data) -> (cleaned: dict | None, errors: dict)

On success: returns (cleaned_dict, {})
On failure: returns (None, {field: error_message, ...})
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Field specifications
# Each entry: (type_converter, min, max, required)
# Categorical fields use min/max as the set of valid integer codes.
# ---------------------------------------------------------------------------

_NUMERIC_FIELDS: dict[str, tuple] = {
    # field_name: (min_value, max_value)
    # Form always submits height_cm and weight_kg; JS converts imperial before submit.
    "age":        (18.0,  99.0),
    "height_cm":  (100.0, 250.0),   # cm; ~3ft 3in to ~8ft 2in
    "weight_kg":  (30.0,  300.0),   # kg; ~66lbs to ~661lbs
}

_CATEGORICAL_FIELDS: dict[str, set[int]] = {
    "sex":                   {1, 2},
    "general_health":        {1, 2, 3, 4, 5},
    "education_level":       {1, 2, 3, 4},          # pipeline trained on codes 1-4 only
    "income_level":          {1, 2, 3, 4, 5, 6, 7},  # pipeline trained on codes 1-7 only
    "smoking_status":        {1, 2, 3, 4},
    "any_physical_activity": {1, 2},
    "any_alcohol_past_30d":  {1, 2},
}

_FIELD_LABELS: dict[str, str] = {
    "age":                   "Age",
    "height_cm":             "Height",
    "weight_kg":             "Weight",
    "sex":                   "Sex",
    "general_health":        "General health",
    "education_level":       "Education level",
    "income_level":          "Income level",
    "smoking_status":        "Smoking status",
    "any_physical_activity": "Physical activity",
    "any_alcohol_past_30d":  "Alcohol use",
}


def validate_prediction_input(
    form_data: dict,
) -> tuple[dict | None, dict[str, str]]:
    """
    Validate and clean raw form data from a Flask request.form object.

    Returns
    -------
    (cleaned, errors)
        cleaned : dict ready to pass to utils.model.predict(), or None on failure
        errors  : dict mapping field name -> human-readable error string
    """
    errors: dict[str, str] = {}
    cleaned: dict[str, float] = {}

    # --- Numeric fields ---
    for field, (min_val, max_val) in _NUMERIC_FIELDS.items():
        label = _FIELD_LABELS[field]
        raw = form_data.get(field, "").strip()

        if not raw:
            errors[field] = f"{label} is required."
            continue

        try:
            value = float(raw)
        except ValueError:
            errors[field] = f"{label} must be a number."
            continue

        if value < min_val or value > max_val:
            errors[field] = f"{label} must be between {min_val:.0f} and {max_val:.0f}."
            continue

        if field == "age":
            cleaned["age_imputed"] = value
        elif field == "height_cm":
            cleaned["_height_cm"] = value   # temp key, used for BMI below
        elif field == "weight_kg":
            cleaned["weight_kg"] = value

    # Compute bmi from height and weight if both valid
    if "_height_cm" in cleaned and "weight_kg" in cleaned:
        h_m = cleaned.pop("_height_cm") / 100.0   # cm -> metres
        bmi = cleaned["weight_kg"] / (h_m ** 2)
        # Sanity-check computed BMI falls in a plausible range
        if not (10.0 <= bmi <= 70.0):
            errors["weight_kg"] = (
                "The height and weight combination gives an implausible BMI "
                f"({bmi:.1f}). Please double-check your entries."
            )
        else:
            cleaned["bmi"] = round(bmi, 2)   # SVM expects raw BMI, not bmi_x100
        cleaned.pop("weight_kg", None)       # weight_kg not a model feature
    elif "_height_cm" in cleaned:
        cleaned.pop("_height_cm", None)

    # --- Categorical fields ---
    for field, valid_codes in _CATEGORICAL_FIELDS.items():
        label = _FIELD_LABELS[field]
        raw = form_data.get(field, "").strip()

        if not raw:
            errors[field] = f"{label} is required."
            continue

        try:
            value = int(raw)
        except ValueError:
            errors[field] = f"{label} contains an unexpected value."
            continue

        if value not in valid_codes:
            errors[field] = f"{label} contains an unexpected value."
            continue

        cleaned[field] = float(value)

    if errors:
        return None, errors

    return cleaned, {}