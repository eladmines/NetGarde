import json
from typing import Any

from app.features.dashboard.services.llm_common import parse_summary_from_content, text_looks_like_metric_dump
from app.features.dashboard.services.ollama_connectivity import ensure_model_available, resolve_ollama_base_url
from app.shared.config import settings


def compact_behavior_snapshot_for_llm(snapshot: dict[str, Any]) -> dict[str, Any]:
    baseline = snapshot.get("baseline") or {}
    return {
        "device_label": snapshot.get("device_label"),
        "profile_ready": snapshot.get("profile_ready"),
        "last_score": snapshot.get("last_score"),
        "alert_threshold": snapshot.get("alert_threshold"),
        "window": snapshot.get("window"),
        "baseline": {
            "median_queries_per_hour": baseline.get("median_queries_per_hour"),
            "p95_new_roots_per_hour": baseline.get("p95_new_roots_per_hour"),
            "rollup_hours": baseline.get("rollup_hours"),
        },
        "recent_alerts": (snapshot.get("recent_alerts") or [])[:3],
        "active_block_count": snapshot.get("active_block_count"),
    }


def build_behavior_review_prompt(snapshot: dict[str, Any], *, strict: bool = False) -> tuple[str, str]:
    example = (
        '{"summary":"Your child\'s tablet had a burst of new websites and higher DNS volume '
        'than usual. Most lookups were blocked or flagged. Consider checking what app was in use."}'
    )
    system = (
        "You explain home network behavior alerts to parents in calm, plain English. "
        "Read the JSON about one device. Write one short paragraph (3–5 sentences) about what "
        "likely happened and what a parent might do. Do not use bullet lists. "
        f'Return ONLY valid JSON: {example} '
        "Do NOT copy raw field names or 'key: value' metric lines. "
        "Do not recommend turning off security. Scoring already triggered alerts; explain only."
    )
    if strict:
        system += " IMPORTANT: Previous reply was invalid. Use a single parent-friendly paragraph."
    compact = compact_behavior_snapshot_for_llm(snapshot)
    user = (
        f"Explain behavior for this device:\n"
        + json.dumps(compact, separators=(",", ":"), default=str)
    )
    return system, user


def _ollama_chat(system: str, user: str, *, strict: bool) -> str:
    import httpx

    base = resolve_ollama_base_url()
    ensure_model_available(base)
    url = f"{base}/api/chat"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "options": {
            "temperature": 0.2 if strict else 0.3,
            "num_predict": 400,
            "num_ctx": 2048,
        },
    }
    timeout = httpx.Timeout(
        connect=15.0,
        read=settings.LLM_TIMEOUT_SEC,
        write=30.0,
        pool=15.0,
    )
    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
    content = data.get("message", {}).get("content", "")
    if not content:
        raise RuntimeError("Ollama returned an empty message")
    return content


def summarize_behavior_review_ollama(snapshot: dict[str, Any]) -> str:
    import httpx

    last_error: Exception | None = None
    for strict in (False, True):
        try:
            system, user = build_behavior_review_prompt(snapshot, strict=strict)
            content = _ollama_chat(system, user, strict=strict)
            summary = parse_summary_from_content(content)
            if text_looks_like_metric_dump(summary):
                raise ValueError("model returned metric labels instead of a summary")
            return summary
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                f"Ollama timed out after {int(settings.LLM_TIMEOUT_SEC)}s. "
                "Set LLM_TIMEOUT_SEC=240 in backend.env and retry."
            ) from exc
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Ollama behavior review failed: {last_error}") from last_error


def summarize_behavior_review_openai(snapshot: dict[str, Any]) -> str:
    api_key = settings.OPENAI_API_KEY.strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    system, user = build_behavior_review_prompt(snapshot)
    base = settings.OPENAI_BASE_URL.rstrip("/") or "https://api.openai.com/v1"
    url = f"{base}/chat/completions"
    payload = {
        "model": settings.OPENAI_MODEL,
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    import httpx

    with httpx.Client(timeout=settings.LLM_TIMEOUT_SEC) as client:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    content = data["choices"][0]["message"]["content"]
    return parse_summary_from_content(content)
