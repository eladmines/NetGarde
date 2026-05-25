import pytest

from app.features.dns_queries.dns_anomaly import (
    is_high_entropy_subdomain,
    is_suspicious_domain,
    is_suspicious_tld,
)


def test_suspicious_tld():
    assert is_suspicious_tld("tracker.xyz") is True
    assert is_suspicious_tld("ynet.co.il") is False


def test_high_entropy_subdomain():
    assert is_high_entropy_subdomain("abc123456789012345678901234567890.example.com") is True
    assert is_high_entropy_subdomain("www.google.com") is False


def test_suspicious_domain_combined():
    assert is_suspicious_domain("cdn.evil.xyz") is True
    assert is_suspicious_domain("www.ynet.co.il") is False
