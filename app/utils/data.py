"""
Centralized data loader with in-memory caching.
Routes import from here instead of reading files directly.
"""
import pandas as pd
from flask import current_app

_cache: dict = {}


def load_brfss() -> pd.DataFrame:
    """Load the BRFSS 2024 subset, cached after first read."""
    if "brfss" not in _cache:
        path = current_app.config["DATA_DIR"] / "brfss2024_subset.parquet"
        _cache["brfss"] = pd.read_parquet(path)
    return _cache["brfss"]
