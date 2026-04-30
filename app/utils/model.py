"""Lazy-loads and caches trained model artifacts for use in routes."""
import json
import joblib
from pathlib import Path

_cache: dict = {}
_ARTIFACTS = Path(__file__).parent.parent / "model" / "artifacts"


def get_pipeline():
    if "pipeline" not in _cache:
        path = _ARTIFACTS / "pipeline.joblib"
        if not path.exists():
            raise RuntimeError("Model not trained. Run: uv run python train_model.py")
        _cache["pipeline"] = joblib.load(path)
    return _cache["pipeline"]


def get_metrics() -> dict:
    if "metrics" not in _cache:
        path = _ARTIFACTS / "metrics.json"
        if not path.exists():
            raise RuntimeError("Model not trained. Run: uv run python train_model.py")
        with open(path) as f:
            _cache["metrics"] = json.load(f)
    return _cache["metrics"]


def get_coefficients() -> list[dict]:
    if "coefficients" not in _cache:
        path = _ARTIFACTS / "coefficients.json"
        if not path.exists():
            raise RuntimeError("Model not trained. Run: uv run python train_model.py")
        with open(path) as f:
            _cache["coefficients"] = json.load(f)
    return _cache["coefficients"]
