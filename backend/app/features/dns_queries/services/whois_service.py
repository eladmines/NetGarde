"""Domain WHOIS / RDAP lookup for anomaly alert investigation."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.shared.domain_utils import extract_root_domain

DOMAIN_RE = re.compile(
    r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+$",
    re.IGNORECASE,
)
RDAP_TIMEOUT_SEC = 15
WHOIS_TIMEOUT_SEC = 15
MAX_WHOIS_BYTES = 32_000


class WhoisLookupError(Exception):
    pass


def normalize_lookup_domain(domain: str) -> str:
    cleaned = domain.strip().lower().rstrip(".")
    if not cleaned:
        raise WhoisLookupError("empty domain")
    root = extract_root_domain(cleaned)
    if not DOMAIN_RE.match(root):
        raise WhoisLookupError(f"invalid domain: {root}")
    return root


def lookup_domain_whois(domain: str) -> dict[str, str]:
    lookup = normalize_lookup_domain(domain)
    rdap_text = _lookup_via_rdap(lookup)
    if rdap_text:
        return {"domain": lookup, "source": "rdap", "text": rdap_text}

    cli_text = _lookup_via_cli(lookup)
    if cli_text:
        return {"domain": lookup, "source": "whois", "text": cli_text}

    raise WhoisLookupError(f"WHOIS lookup failed for {lookup}")


def _lookup_via_rdap(domain: str) -> str | None:
    url = f"https://rdap.org/domain/{domain}"
    req = Request(url, headers={"Accept": "application/rdap+json, application/json"})
    try:
        with urlopen(req, timeout=RDAP_TIMEOUT_SEC) as resp:
            raw = resp.read(MAX_WHOIS_BYTES)
    except (HTTPError, URLError, TimeoutError, OSError):
        return None

    try:
        data = json.loads(raw.decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None

    return _format_rdap(data)


def _format_rdap(data: dict[str, Any]) -> str:
    lines: list[str] = []
    name = data.get("ldhName") or data.get("unicodeName")
    if name:
        lines.append(f"Domain: {name}")

    for event in data.get("events") or []:
        action = event.get("eventAction") or "event"
        date = event.get("eventDate") or ""
        if date:
            lines.append(f"{action.title()}: {date}")

    for status in data.get("status") or []:
        if isinstance(status, str):
            lines.append(f"Status: {status}")

    for entity in data.get("entities") or []:
        roles = entity.get("roles") or []
        if "registrar" not in roles:
            continue
        vcard = entity.get("vcardArray")
        if isinstance(vcard, list) and len(vcard) > 1:
            for row in vcard[1]:
                if isinstance(row, list) and len(row) >= 4 and row[3]:
                    label = str(row[0]).replace("-", " ").title()
                    lines.append(f"Registrar {label}: {row[3]}")
        handle = entity.get("handle")
        if handle:
            lines.append(f"Registrar Handle: {handle}")

    for ns in data.get("nameservers") or []:
        ns_name = ns.get("ldhName") or ns.get("unicodeName")
        if ns_name:
            lines.append(f"Nameserver: {ns_name}")

    if not lines:
        return json.dumps(data, indent=2)[:MAX_WHOIS_BYTES]
    return "\n".join(lines)


def _lookup_via_cli(domain: str) -> str | None:
    if not shutil.which("whois"):
        return None
    try:
        proc = subprocess.run(
            ["whois", domain],
            capture_output=True,
            text=True,
            timeout=WHOIS_TIMEOUT_SEC,
            check=False,
        )
    except (subprocess.SubprocessError, OSError):
        return None

    text = (proc.stdout or proc.stderr or "").strip()
    if not text or proc.returncode not in (0, 1):
        return None
    return text[:MAX_WHOIS_BYTES]
