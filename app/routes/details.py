"""
Details blueprint  —  /details

Shows a personalised breakdown of the user's last prediction:
  1. Actionable features — user value vs population benchmarks + what-if deltas
  2. Full model breakdown — all features ranked by odds ratio with citations
"""

from flask import Blueprint, render_template, session, redirect, url_for

from app.utils.data import (
    get_benchmarks,
    get_overall_stats,
    load_references,
    FEATURE_LABELS,
    CATEGORICAL_LABELS,
)
from app.utils.model import get_svm, get_feature_columns

details_bp = Blueprint("details", __name__)

# Which features get the prominent actionable treatment at the top
_ACTIONABLE_KEYS = {"any_physical_activity", "smoking_status", "any_alcohol_past_30d"}

# Features where a lower value is better (for directional arrow logic)
_LOWER_IS_BETTER = {"bmi_x100", "smoking_status", "general_health", "any_alcohol_past_30d"}


def _fmt_value(feature: str, value: float) -> str:
    """Return a human-readable string for a feature value."""
    labels = CATEGORICAL_LABELS.get(feature)
    if labels:
        return labels.get(value, str(value))
    if feature == "bmi_x100":
        return f"{value / 100:.1f}"
    if feature == "age_imputed":
        return f"{int(value)}"
    return f"{value:.2f}"


def _fmt_benchmark(feature: str, stats) -> str:
    """Format a benchmark value for display in the comparison table."""
    if stats is None:
        return "N/A"
    if isinstance(stats, dict):
        if "pct_yes" in stats:
            return f"Yes ({stats['pct_yes'] * 100:.0f}%)"
        mode_val = stats.get("mode")
        mode_pct = stats.get("mode_pct")
        label = CATEGORICAL_LABELS.get(feature, {}).get(mode_val, str(mode_val))
        if mode_pct is not None:
            return f"{label} ({mode_pct * 100:.0f}%)"
        return str(label)
    return _fmt_value(feature, float(stats))


@details_bp.route("/")
def index():
    result = session.get("last_result")

    # No prediction in session — send back to the form
    if not result:
        return redirect(url_for("predictions.predictions"))

    benchmarks   = get_benchmarks()
    overall      = get_overall_stats()
    svm      = get_svm()
    features = get_feature_columns()
    # Build weight rows from SVM weight vector (analogous to logit coefficients)
    coefficients = [
        {"feature": f, "coef": round(float(w), 4), "direction": "risk" if w > 0 else "protective"}
        for f, w in sorted(zip(features, svm.w), key=lambda x: abs(x[1]), reverse=True)
    ]
    references   = load_references()

    inputs = result["input_features"]

    # ── Actionable feature cards ──────────────────────────────────────────
    actionable_cards = []
    for key in _ACTIONABLE_KEYS:
        if key not in inputs:
            continue

        user_val      = inputs[key]
        diabetic_avg  = benchmarks["diabetic"].get(key)
        nondiab_avg   = benchmarks["non_diabetic"].get(key)

        # Find matching suggestion with what-if delta (may not exist if condition not met)
        suggestion = next(
            (s for s in result["suggestions"] if s.get("label") and key in s.get("label", "").lower().replace(" ", "_") or False),
            None,
        )
        # More reliable lookup by key presence in suggestions list
        suggestion = next(
            (s for s in result["suggestions"]
             if not s.get("static", False) and abs(s.get("new_prob_pct", -1)) >= 0),
            None,
        )

        actionable_cards.append({
            "key":           key,
            "label":         FEATURE_LABELS.get(key, key),
            "user_value":    _fmt_value(key, user_val),
            "user_raw":      user_val,
            "diabetic_avg":  _fmt_benchmark(key, diabetic_avg),
            "nondiab_avg":   _fmt_benchmark(key, nondiab_avg),
        })

    # ── Full model feature rows ───────────────────────────────────────────
    # Parse feature name from coefficient entry (e.g. "general_health_3.0" -> "general_health")
    def _base_feature(coef_name: str) -> str:
        parts = coef_name.rsplit("_", 1)
        try:
            float(parts[-1])
            return parts[0]
        except ValueError:
            return coef_name

    # Build readable weight rows from SVM weight vector.
    # SVM weights are analogous to logit coefficients — positive = higher risk.
    coef_rows = []
    for c in coefficients:
        feature = c["feature"]
        label   = FEATURE_LABELS.get(feature, feature.replace("_", " ").title())
        coef_rows.append({
            "display":   label,
            "feature":   feature,
            "coef":      round(c["coef"], 4),
            "direction": c["direction"],
        })

    # ── Citations ─────────────────────────────────────────────────────────
    actionable_refs = [r for r in references if r["topic"] == "actionable"]
    model_refs      = [r for r in references if r["topic"] == "model"]
    general_refs    = [r for r in references if r["topic"] == "general"]
    all_refs        = general_refs + actionable_refs + model_refs

    return render_template(
        "details/index.html",
        result           = result,
        actionable_cards = actionable_cards,
        coef_rows        = coef_rows,
        overall          = overall,
        benchmarks       = benchmarks,
        all_refs         = all_refs,
        feature_labels   = FEATURE_LABELS,
        suggestions      = result["suggestions"],
    )