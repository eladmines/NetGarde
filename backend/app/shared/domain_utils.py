"""
Root domain extraction utility for grouping DNS queries.
"""

from typing import Set

# Known multi-part TLDs
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

# Noise domain suffixes — for filtering at the API level
NOISE_SUFFIXES = [
    '.data.microsoft.com',
    '.telemetry.microsoft.com',
    'storequality.microsoft.com',
    'licensing.mp.microsoft.com',
    'wdcp.microsoft.com',
    'activity.windows.com',
    '.windowsupdate.com',
    '.update.microsoft.com',
    '.delivery.mp.microsoft.com',
    'safebrowsing.googleapis.com',
    'safebrowsing-cache.google.com',
    'chrome.google.com',
    'update.googleapis.com',
    'connectivitycheck.gstatic.com',
    'connectivity-check.ubuntu.com',
    'captive.apple.com',
    'msftconnecttest.com',
    'msftncsi.com',
    'detectportal.firefox.com',
    'ocsp.pki.goog',
    'ocsp.digicert.com',
    'ocsp.sectigo.com',
    'crl.microsoft.com',
    'time.windows.com',
    'time.google.com',
    'ntp.ubuntu.com',
    '.notifications.aws.dev',
    '.ctrl.prod.os.',
    '.push.apple.com',
    'clients1.google.com',
    'clients2.google.com',
    'clients3.google.com',
    'clients4.google.com',
    'mtalk.google.com',
    'play.googleapis.com',
    'firebaseinstallations.googleapis.com',
    'android.googleapis.com',
    'fcm.googleapis.com',
    '.in-addr.arpa',
    '.ip6.arpa',
]


def extract_root_domain(domain: str) -> str:
    """
    Extract the root/registrable domain from a full domain.
    
    Examples:
        www.ynet.co.il   → ynet.co.il
        cdn.taboola.com  → taboola.com
        api2.cursor.sh   → cursor.sh
        google.com       → google.com
    """
    domain = domain.lower().rstrip('.')
    parts = domain.split('.')

    if len(parts) <= 2:
        return domain

    # Check for multi-part TLDs
    if len(parts) >= 3:
        potential_tld = '.'.join(parts[-2:])
        if potential_tld in MULTI_PART_TLDS:
            return '.'.join(parts[-3:])

    return '.'.join(parts[-2:])


def is_noise_domain(domain: str) -> bool:
    """Check if a domain is system noise."""
    domain_lower = domain.lower()
    for suffix in NOISE_SUFFIXES:
        if domain_lower.endswith(suffix) or domain_lower == suffix.lstrip('.'):
            return True
    return False
