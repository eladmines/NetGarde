import json
from urllib import request, error
from typing import Tuple

from app.shared.config import settings


# Minimal seed set for quick wins; can be replaced by feed/AI worker later.
NEWS_DOMAINS = {
    "ynet.co.il",
    "walla.co.il",
    "mako.co.il",
    "cnn.com",
    "edition.cnn.com",
    "bbc.com",
    "reuters.com",
    "nytimes.com",
}

NEWS_KEYWORDS = (
    "news",
    "times",
    "post",
    "journal",
    "gazette",
    "press",
    "herald",
)


def classify_domain_category(domain: str) -> Tuple[str, int, str]:
    """
    Classify a root domain into a category tuple: (category_name, confidence, source).
    This is a heuristic baseline that can later be replaced by feed/AI workers.
    """
    d = domain.strip().lower()
    if not d:
        return "Unknown", 0, "heuristic"

    if d in NEWS_DOMAINS or any(k in d for k in NEWS_KEYWORDS):
        return "News", 85, "heuristic"

    return "Unknown", 40, "heuristic"


ALLOWED_CATEGORIES = {
    "News",
    "Social Media",
    "Gaming",
    "Adult",
    "Gambling",
    "Shopping",
    "Education",
    "Technology",
    "Finance",
    "Unknown",
}


def classify_domain_category_ai(domain: str) -> Tuple[str, int, str]:
    """
    Classify domain with OpenAI chat completions API and return normalized tuple.
    Falls back to heuristic on errors.
    """
    if not settings.OPENAI_API_KEY:
        return classify_domain_category(domain)

    payload = {
        "model": settings.AI_MODEL,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You classify internet domains into a strict fixed set. "
                    "Return only JSON object with keys: category, confidence, reason. "
                    "category must be one of: News, Social Media, Gaming, Adult, Gambling, "
                    "Shopping, Education, Technology, Finance, Unknown. "
                    "confidence must be integer 0..100."
                ),
            },
            {
                "role": "user",
                "content": f"Domain: {domain}",
            },
        ],
    }

    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
    }

    req = request.Request(settings.AI_BASE_URL, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=settings.AI_TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            category = str(parsed.get("category", "Unknown")).strip()
            confidence = int(parsed.get("confidence", 0))
            if category not in ALLOWED_CATEGORIES:
                category = "Unknown"
            confidence = max(0, min(100, confidence))
            return category, confidence, "ai"
    except (ValueError, KeyError, error.URLError, error.HTTPError, TimeoutError):
        return classify_domain_category(domain)

