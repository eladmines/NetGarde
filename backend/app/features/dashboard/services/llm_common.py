import json
import re
from typing import Any

MAX_BULLETS = 6
MAX_BULLET_LEN = 220

_METRIC_DUMP_RE = re.compile(
    r"^[A-Za-z][A-Za-z0-9_ /]*:\s*[\d.]+",
    re.IGNORECASE,
)


def bullets_look_like_metric_dump(bullets: list[str]) -> bool:
    """Detect LLM echoing JSON fields ('Peak mib/sec: 0.5') instead of prose."""
    if not bullets:
        return True
    matches = sum(1 for b in bullets if _METRIC_DUMP_RE.match(b.strip()))
    return matches >= max(2, len(bullets) // 2)


def parse_bullets_from_content(content: str) -> list[str]:
    """Parse model output into a list of bullet strings."""
    text = (content or "").strip()
    if not text:
        raise ValueError("empty LLM response")

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and isinstance(parsed.get("bullets"), list):
            return _normalize_bullets(parsed["bullets"])
        if isinstance(parsed, list):
            return _normalize_bullets(parsed)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\"bullets\"[\s\S]*\}", text)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict) and isinstance(parsed.get("bullets"), list):
                return _normalize_bullets(parsed["bullets"])
        except json.JSONDecodeError:
            pass

    match = re.search(r"\[[\s\S]*\]", text)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list):
                return _normalize_bullets(parsed)
        except json.JSONDecodeError:
            pass

    lines = [ln.strip().lstrip("-•* ").strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        if bullets_look_like_metric_dump(lines):
            raise ValueError("model returned metric labels instead of a summary")
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
        if ":" in s and _METRIC_DUMP_RE.match(s):
            continue
        if len(s) > MAX_BULLET_LEN:
            s = s[: MAX_BULLET_LEN - 3] + "..."
        bullets.append(s)
        if len(bullets) >= MAX_BULLETS:
            break
    if not bullets:
        raise ValueError("no valid bullets in LLM response")
    return bullets


def compact_snapshot_for_llm(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Smaller JSON for CPU Ollama (faster prompt eval on t3.medium)."""
    blocked = snapshot.get("blocked") or {}
    top_domains = (blocked.get("top_domains") or [])[:3]
    alerts = snapshot.get("alerts") or {}
    return {
        "period_minutes": snapshot.get("period_minutes"),
        "live": snapshot.get("live"),
        "history": snapshot.get("history"),
        "alerts": {"total": alerts.get("total"), "by_type": alerts.get("by_type")},
        "blocked": {"count": blocked.get("count"), "top_domains": top_domains},
        "policy": snapshot.get("policy"),
        "behavior": snapshot.get("behavior"),
    }


def build_review_prompt(snapshot: dict[str, Any], *, strict: bool = False) -> tuple[str, str]:
    example = (
        '{"bullets":["Traffic is light with one device online.",'
        '"Many blocked sites were attempted in the last hour.",'
        '"Alert volume is high; most are blocked DNS attempts.",'
        '"No policy packs are enabled; consider turning on Social."]}'
    )
    system = (
        "You summarize home network security for parents. Read the JSON metrics and write "
        "four complete English sentences. "
        f'Return ONLY valid JSON in this shape: {example} '
        "Do NOT copy field names like 'Peak mib/sec' or 'Total alerts'. "
        "Do NOT use 'key: value' lines. Explain what it means, not just the numbers."
    )
    if strict:
        system += " IMPORTANT: Previous reply was invalid. Use full sentences only."
    compact = compact_snapshot_for_llm(snapshot)
    user = (
        f"Summarize this network snapshot for the last {compact.get('period_minutes', 60)} minutes:\n"
        + json.dumps(compact, separators=(",", ":"), default=str)
    )
    return system, user
