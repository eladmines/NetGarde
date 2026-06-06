import json
from typing import Dict, Optional


def parse_country_counts(raw: Optional[str]) -> Dict[str, int]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            return {}
        return {str(k).upper(): int(v) for k, v in data.items() if v}
    except (json.JSONDecodeError, TypeError, ValueError):
        return {}


def merge_country_counts(existing: Dict[str, int], delta: Dict[str, int]) -> Dict[str, int]:
    merged = dict(existing)
    for code, count in delta.items():
        key = code.upper()
        merged[key] = merged.get(key, 0) + int(count)
    return merged


def dumps_country_counts(counts: Dict[str, int]) -> str:
    return json.dumps({k: v for k, v in sorted(counts.items()) if v > 0})
