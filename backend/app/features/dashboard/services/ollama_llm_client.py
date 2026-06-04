from app.features.dashboard.services.llm_common import (
    build_review_prompt,
    bullets_look_like_metric_dump,
    parse_bullets_from_content,
)
from app.features.dashboard.services.ollama_connectivity import ensure_model_available, resolve_ollama_base_url
from app.shared.config import settings


def _chat(base: str, snapshot: dict, *, strict: bool) -> str:
    import httpx

    system, user = build_review_prompt(snapshot, strict=strict)
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


def summarize_network_review(snapshot: dict) -> list[str]:
    base = resolve_ollama_base_url()
    ensure_model_available(base)

    import httpx

    last_error: Exception | None = None
    for strict in (False, True):
        try:
            content = _chat(base, snapshot, strict=strict)
            bullets = parse_bullets_from_content(content)
            if bullets_look_like_metric_dump(bullets):
                raise ValueError("model returned metric labels instead of a summary")
            return bullets
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                f"Ollama timed out after {int(settings.LLM_TIMEOUT_SEC)}s on CPU "
                f"(inference can take 60–120s). Set LLM_TIMEOUT_SEC=240 in backend.env and retry."
            ) from exc
        except Exception as exc:
            last_error = exc

    raise RuntimeError(f"Ollama summary failed: {last_error}") from last_error
