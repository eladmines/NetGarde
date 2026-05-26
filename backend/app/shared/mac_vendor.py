from typing import Optional


# Small built-in OUI prefix map (can be extended later or replaced by a full OUI DB).
OUI_VENDOR_MAP = {
    "00:1B:63": "Apple",
    "28:CF:E9": "Apple",
    "3C:5A:B4": "Apple",
    "40:B0:76": "Apple",
    "F0:18:98": "Apple",
    "FC:FB:FB": "Apple",
    "84:7B:57": "Samsung",
    "A8:9C:ED": "Samsung",
    "D8:E0:E1": "Samsung",
    "FC:C2:DE": "Samsung",
    "00:14:22": "Dell",
    "18:03:73": "Dell",
    "34:17:EB": "Dell",
    "54:BF:64": "Dell",
    "98:90:96": "Dell",
    "00:1A:11": "Google",
    "3C:5A:37": "Google",
    "F8:8F:CA": "Google",
    "00:50:F2": "Microsoft",
    "00:15:5D": "Microsoft",
    "7C:1E:52": "Microsoft",
    "BC:83:85": "Microsoft",
    "00:0C:29": "VMware",
    "00:50:56": "VMware",
    "00:1C:14": "VMware",
    "08:00:27": "VirtualBox",
    "52:54:00": "QEMU/KVM",
}


def normalize_mac(mac_address: str) -> str:
    """
    Normalize MAC to uppercase colon-separated form: AA:BB:CC:DD:EE:FF
    Accepts values with ':', '-', or no separators.
    """
    cleaned = mac_address.strip().replace("-", "").replace(":", "").upper()
    if len(cleaned) != 12:
        return mac_address.strip().upper()
    return ":".join(cleaned[i : i + 2] for i in range(0, 12, 2))


def infer_vendor_from_mac(mac_address: Optional[str]) -> Optional[str]:
    """Infer a vendor from MAC OUI prefix. Returns None if unknown or invalid."""
    if not mac_address:
        return None

    normalized = normalize_mac(mac_address)
    oui = normalized[:8]  # AA:BB:CC
    return OUI_VENDOR_MAP.get(oui)
