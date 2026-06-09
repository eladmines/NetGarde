"""
TrustEdge DNS Noise Filter & Root Domain Extractor.

Filters out system/telemetry/CDN noise domains and extracts
root domains for grouping (e.g. www.ynet.co.il → ynet.co.il).

Shared between dns_log_watcher.py and log_parser.py.
"""

from typing import Set

# Known multi-part TLDs (country-code second-level domains)
MULTI_PART_TLDS: Set[str] = {
    'co.il', 'co.uk', 'co.jp', 'co.kr', 'co.nz', 'co.za', 'co.in',
    'com.au', 'com.br', 'com.cn', 'com.mx', 'com.tw', 'com.ar',
    'com.tr', 'com.sg', 'com.hk', 'com.my', 'com.ph', 'com.pk',
    'org.uk', 'org.au', 'org.il',
    'net.au', 'net.il', 'net.br',
    'ac.uk', 'ac.il', 'ac.jp',
    'gov.uk', 'gov.au', 'gov.il',
    'edu.au', 'edu.cn',
}

# Noise domain suffixes — domains ending with these are filtered out
NOISE_SUFFIXES = [
    # Reverse DNS (should already be filtered, but just in case)
    '.in-addr.arpa',
    '.ip6.arpa',

    # Microsoft telemetry & system services
    '.data.microsoft.com',
    '.telemetry.microsoft.com',
    'storequality.microsoft.com',
    'licensing.mp.microsoft.com',
    'wdcp.microsoft.com',
    'activity.windows.com',
    'settings-win.data.microsoft.com',

    # Windows Update
    '.windowsupdate.com',
    '.update.microsoft.com',
    '.delivery.mp.microsoft.com',

    # Browser safety/internals
    'safebrowsing.googleapis.com',
    'safebrowsing-cache.google.com',
    'chrome.google.com',
    'update.googleapis.com',

    # OS connectivity checks
    'connectivitycheck.gstatic.com',
    'connectivity-check.ubuntu.com',
    'captive.apple.com',
    'msftconnecttest.com',
    'msftncsi.com',
    'detectportal.firefox.com',

    # Certificate / OCSP validation
    'ocsp.pki.goog',
    'ocsp.digicert.com',
    'ocsp.sectigo.com',
    'crl.microsoft.com',
    'crl3.digicert.com',
    'crl4.digicert.com',

    # NTP / time sync
    'time.windows.com',
    'time.google.com',
    'ntp.ubuntu.com',
    'time.apple.com',

    # AWS internal (EC2 metadata, monitoring, notifications)
    '.notifications.aws.dev',
    'ec2messages.',
    '.ctrl.prod.os.',
    'ssm.us-east-1.amazonaws.com',
    'ec2.us-east-1.amazonaws.com',
    'monitoring.us-east-1.amazonaws.com',
    'logs.us-east-1.amazonaws.com',

    # Apple system services
    '.push.apple.com',
    '.icloud-content.com',
    'configuration.apple.com',
    'gsp-ssl.ls.apple.com',
    'gspe1-ssl.ls.apple.com',

    # Google internal services (not user-facing)
    'clients1.google.com',
    'clients2.google.com',
    'clients3.google.com',
    'clients4.google.com',
    'mtalk.google.com',
    'alt1-mtalk.google.com',
    'play.googleapis.com',
    'firebaseinstallations.googleapis.com',
    'android.googleapis.com',
    'fcm.googleapis.com',

    # Local / internal
    'localhost',
    'wpad.',
    'isatap.',
    '_dns.',
]

# Exact-match noise domains
NOISE_EXACT = {
    'local',
    'localhost',
    'wpad',
    'isatap',
}


def is_noise_domain(domain: str) -> bool:
    """Check if a domain is system noise that should be filtered out."""
    domain_lower = domain.lower()

    # Exact match
    if domain_lower in NOISE_EXACT:
        return True

    # Suffix match
    for suffix in NOISE_SUFFIXES:
        if domain_lower.endswith(suffix) or domain_lower == suffix.lstrip('.'):
            return True

    return False


def extract_root_domain(domain: str) -> str:
    """
    Extract the root/registrable domain from a full domain.
    """
    domain = domain.lower().rstrip('.')

    parts = domain.split('.')

    if len(parts) <= 2:
        return domain

    # Check for multi-part TLDs (e.g., co.il, com.au)
    if len(parts) >= 3:
        potential_tld = '.'.join(parts[-2:])
        if potential_tld in MULTI_PART_TLDS:
            if len(parts) >= 3:
                return '.'.join(parts[-3:])
            return domain

    return '.'.join(parts[-2:])

