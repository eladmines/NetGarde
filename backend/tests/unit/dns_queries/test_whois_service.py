import pytest

from app.features.dns_queries.services.whois_service import (
    WhoisLookupError,
    normalize_lookup_domain,
    _format_rdap,
)


def test_normalize_lookup_domain_uses_root():
    assert normalize_lookup_domain("www.evil.xyz") == "evil.xyz"
    assert normalize_lookup_domain("ynet.co.il") == "ynet.co.il"


def test_normalize_lookup_domain_rejects_invalid():
    with pytest.raises(WhoisLookupError):
        normalize_lookup_domain("not a domain")


def test_format_rdap_summary():
    text = _format_rdap(
        {
            "ldhName": "EXAMPLE.COM",
            "events": [{"eventAction": "registration", "eventDate": "1995-08-14T04:00:00Z"}],
            "status": ["client delete prohibited"],
            "nameservers": [{"ldhName": "NS1.EXAMPLE.COM"}],
        }
    )
    assert "EXAMPLE.COM" in text
    assert "Registration:" in text
    assert "NS1.EXAMPLE.COM" in text
