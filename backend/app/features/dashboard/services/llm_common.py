import json
import re
from typing import Any

MAX_BULLETS = 6
MAX_BULLET_LEN = 220


def parse_bullets_from_content(content: str) -> list[str]:
    """Parse model output into a list of bullet strings."""
    text = (content or "").strip()
    if not text:
        raise ValueError("empty LLM response")

    # Direct JSON array
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return _normalize_bullets(parsed)
    except json.JSONDecodeError:
        pass

    # JSON array embedded in prose
    match = re.search(r"\[[\s\S]*\]", text)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list):
                return _normalize_bullets(parsed)
        except json.JSONDecodeError:
            pass

    # Line-based fallback
    lines = [ln.strip().lstrip("-•* ").strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        return _normalize_bullets(lines)

    raise ValueError("could not parse bullets from LLM response")


def _normalize_bullets(items: list[Any]) -> list[str]:
    bullets: list[str] = []
    for item in items:
        if not isinstance(item, str):
            continue
        s = " ".join(item.split())
        if not s:
            continue
        if len(s) > MAX_BULLET_LEN:
            s = s[: MAX_BULLET_LEN - 3] + "..."
        bullets.append(s)
        if len(bullets) >= MAX_BULLETS:
            break
    if not bullets:
        raise ValueError("no valid bullets in LLM response")
    return bullets


def build_review_prompt(snapshot: dict[str, Any]) -> tuple[str, str]:
    system = (
        "You are a home network security analyst helping parents understand their network. "
        "Given JSON metrics only (no raw logs), write a concise status summary. "
        "Return ONLY a JSON array of 3 to 6 strings. Each string is one bullet, under 180 characters, "
        "plain text, no markdown, no numbering prefix. Be factual and calm."
    )
    user = json.dumps(snapshot, separators=(",", ":"), default=str)
    return system, user
