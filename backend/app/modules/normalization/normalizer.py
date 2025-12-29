import re

UNIT_FACTORS = {
    "mm": 1.0,
    "cm": 10.0,
    "m": 1000.0,
    "in": 25.4,
}

WEIGHT_FACTORS = {
    "kg": 1.0,
    "g": 0.001,
    "lb": 0.453592,
}


def normalize_dimension(raw_value: str) -> str:
    match = re.match(r"(\d+(?:\.\d+)?)\s*(mm|cm|m|in)", raw_value, re.IGNORECASE)
    if not match:
        return raw_value
    value, unit = match.groups()
    mm_value = float(value) * UNIT_FACTORS[unit.lower()]
    return f"{mm_value:.1f} mm"


def normalize_weight(raw_value: str) -> str:
    match = re.match(r"(\d+(?:\.\d+)?)\s*(kg|g|lb)", raw_value, re.IGNORECASE)
    if not match:
        return raw_value
    value, unit = match.groups()
    kg_value = float(value) * WEIGHT_FACTORS[unit.lower()]
    return f"{kg_value:.3f} kg"


def normalize_capacity(raw_value: str) -> str:
    match = re.match(r"(\d+(?:\.\d+)?)\s*wh", raw_value, re.IGNORECASE)
    if not match:
        return raw_value
    return f"{float(match.group(1)):.0f} Wh"


def normalize_inverter(raw_value: str) -> str:
    match = re.match(r"(\d+(?:\.\d+)?)\s*w", raw_value, re.IGNORECASE)
    if not match:
        return raw_value
    return f"{float(match.group(1)):.0f} W"


def normalize_name(raw_value: str) -> str:
    cleaned = re.sub(r"\s+", " ", raw_value.strip())
    cleaned = re.sub(r"\b(plus|pro|max|lite)\b", lambda m: m.group(1).lower(), cleaned, flags=re.IGNORECASE)
    return cleaned


def normalize_field(field_name: str, raw_value: str) -> str:
    if field_name in {"length", "width", "height"}:
        return normalize_dimension(raw_value)
    if field_name in {"gross_weight", "net_weight"}:
        return normalize_weight(raw_value)
    if field_name == "capacity_wh":
        return normalize_capacity(raw_value)
    if field_name == "inverter_w":
        return normalize_inverter(raw_value)
    if field_name == "model_name":
        return normalize_name(raw_value)
    return raw_value
