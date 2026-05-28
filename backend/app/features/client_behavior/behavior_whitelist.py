"""Root domains never auto-blocked by behavioral scoring."""

from typing import Set

BEHAVIOR_BLOCK_WHITELIST_ROOTS: Set[str] = {
    "apple.com",
    "icloud.com",
    "microsoft.com",
    "windows.com",
    "windowsupdate.com",
    "google.com",
    "googleapis.com",
    "gstatic.com",
    "amazon.com",
    "amazonaws.com",
    "cloudfront.net",
    "github.com",
    "ubuntu.com",
    "debian.org",
}


def is_whitelisted_root(root_domain: str) -> bool:
    root = root_domain.lower().strip()
    if not root:
        return True
    if root in BEHAVIOR_BLOCK_WHITELIST_ROOTS:
        return True
    for allowed in BEHAVIOR_BLOCK_WHITELIST_ROOTS:
        if root == allowed or root.endswith("." + allowed):
            return True
    return False
