from app.features.dashboard.services.llm_common import build_review_prompt, parse_bullets_from_content
from app.shared.config import settings


def summarize_network_review(snapshot: dict) -> list[str]:
    base = settings.OLLAMA_BASE_URL.rstrip("/")
    if not base:
        raise RuntimeError("OLLAMA_BASE_URL is not set")

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
    return parse_bullets_from_content(content)
