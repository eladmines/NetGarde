"""Resolve a reachable Ollama base URL from inside the backend container."""

from __future__ import annotations

from typing import Optional

from app.shared.config import settings


def ollama_candidate_urls() -> list[str]:
    configured = settings.OLLAMA_BASE_URL.strip().rstrip("/")
    candidates: list[str] = []
    if configured:
        candidates.append(configured)
    for url in (
        "http://ollama:11434",
        "http://host.docker.internal:11434",
        "http://172.17.0.1:11434",
    ):
        if url not in candidates:
            candidates.append(url)
    return candidates


def resolve_ollama_base_url() -> str:
    import httpx

    timeout = min(10.0, float(settings.LLM_TIMEOUT_SEC))
    last_error: Optional[str] = None
    for base in ollama_candidate_urls():
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(f"{base}/api/tags")
                response.raise_for_status()
            return base
        except Exception as exc:
            last_error = f"{base}: {exc}"
    raise RuntimeError(
        "Cannot reach Ollama. Tried: "
        + ", ".join(ollama_candidate_urls())
        + (f". Last error: {last_error}" if last_error else "")
    )


def ensure_model_available(base_url: str) -> None:
    import httpx

    model = settings.OLLAMA_MODEL.strip()
    if not model:
        raise RuntimeError("OLLAMA_MODEL is not set")

    with httpx.Client(timeout=min(10.0, float(settings.LLM_TIMEOUT_SEC))) as client:
        response = client.get(f"{base_url.rstrip('/')}/api/tags")
        response.raise_for_status()
        data = response.json()

    names = {m.get("name", "") for m in data.get("models", []) if isinstance(m, dict)}
    if model in names:
        return
    # Ollama may report "llama3.2:3b" vs "llama3.2:latest"
    if any(name == model or name.startswith(f"{model}:") or model.startswith(f"{name}:") for name in names):
        return
    if not names:
        raise RuntimeError(
            f"Model '{model}' not found on Ollama (no models pulled). Run: "
            f"docker exec netgarde-ollama ollama pull {model}"
        )
    raise RuntimeError(
        f"Model '{model}' not found on Ollama. Available: {', '.join(sorted(names)[:8])}"
    )
