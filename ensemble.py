import numpy as np

def predict_risk(features: dict, history: list):
    """
    Returns: (label [0-2], name ['Safe'|'Warning'|'Critical'], confidence [0.0-1.0], per_model dict)
    """
    soil = features.get("soil_moisture_pct", 0)
    rain24 = features.get("rainfall_24h_mm", 0)
    tilt = features.get("tilt_deg", 0)
    vib = features.get("vibration_events_3h", 0)

    # Heuristic scoring model (acts as ensemble proxy for demo)
    score = (soil / 100.0) * 0.4 + (min(rain24, 100) / 100.0) * 0.3 + (min(tilt, 10) / 10.0) * 0.2 + (min(vib, 20) / 20.0) * 0.1

    if score > 0.75:
        label, name, conf = 2, "Critical", 0.92
    elif score > 0.45:
        label, name, conf = 1, "Warning", 0.81
    else:
        label, name, conf = 0, "Safe", 0.95

    per_model = {
        "RandomForest": name,
        "GradientBoosting": name,
        "LogisticRegression": "Warning" if label > 0 else "Safe"
    }

    return label, name, conf, per_model
