import joblib
import os


# Hardcoded safe defaults – always available
DEFAULT_MODELS = {
    "fusion_weights": {"fuzzy": 0.3, "text": 0.5, "image": 0.2},
    "threshold": 0.7,
}

# Start module-level state with defaults so even if load_models()
# is never called (e.g. during reload) we still have usable values.
_models = DEFAULT_MODELS.copy()


def load_models() -> None:
    """
    Initialize the in-memory models dictionary.

    1. Start from hardcoded defaults.
    2. Try to overwrite from local .pkl files if they exist.
    3. Never leave _models without fusion_weights / threshold keys.
    """
    global _models

    base = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "models")
    )

    # Start from defaults every time load_models is called
    _models = DEFAULT_MODELS.copy()
    print(f"[MODELS] Initializing with defaults: {_models}")
    print(f"[MODELS] Looking for model files in: {base}")

    # Try to load fusion_weights
    fusion_path = os.path.join(base, "fusion_weights.pkl")
    try:
        if os.path.exists(fusion_path):
            _models["fusion_weights"] = joblib.load(fusion_path)
            print(f"[MODELS] Loaded fusion_weights from {fusion_path}: "
                  f"{_models['fusion_weights']}")
        else:
            print(f"[MODELS] fusion_weights.pkl not found, "
                  f"using default fusion weights.")
    except Exception as e:
        print(f"[MODELS] Failed to load fusion_weights.pkl, "
              f"using defaults. Error: {e}")

    # Try to load threshold
    threshold_path = os.path.join(base, "threshold.pkl")
    try:
        if os.path.exists(threshold_path):
            _models["threshold"] = joblib.load(threshold_path)
            print(f"[MODELS] Loaded threshold from {threshold_path}: "
                  f"{_models['threshold']}")
        else:
            print(f"[MODELS] threshold.pkl not found, using default threshold.")
    except Exception as e:
        print(f"[MODELS] Failed to load threshold.pkl, "
              f"using default threshold. Error: {e}")

    # Final safety: ensure required keys exist
    for key, value in DEFAULT_MODELS.items():
        _models.setdefault(key, value)

    print(f"[MODELS] Models ready: {_models}")


def get_models() -> dict:
    """
    Return a non-empty models dict that always
    contains fusion_weights and threshold.
    """
    # If for some reason the module-level dict is empty or missing keys,
    # merge it with defaults so callers are always safe.
    merged = DEFAULT_MODELS.copy()
    merged.update(_models or {})
    return merged