from app.features.dashboard.services.llm_common import build_review_prompt, parse_bullets_from_content
from app.features.dashboard.services.ollama_connectivity import ensure_model_available, resolve_ollama_base_url
from app.shared.config import settings


def summarize_network_review(snapshot: dict) -> list[str]:
    base = resolve_ollama_base_url()
    ensure_model_available(base)

    system, user = build_review_prompt(snapshot)
    url = f"{base}/api/chat"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "options": {"temperature": 0.3},
    }

    import httpx

    with httpx.Client(timeout=settings.LLM_TIMEOUT_SEC) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    content = data.get("message", {}).get("content", "")
    if not content:
        raise RuntimeError("Ollama returned an empty message")
    return parse_bullets_from_content(content)
