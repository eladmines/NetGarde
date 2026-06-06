from app.features.dashboard.services.llm_common import build_review_prompt, parse_summary_from_content
from app.shared.config import settings


def summarize_network_review(snapshot: dict) -> str:
    api_key = settings.OPENAI_API_KEY.strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    system, user = build_review_prompt(snapshot)
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
