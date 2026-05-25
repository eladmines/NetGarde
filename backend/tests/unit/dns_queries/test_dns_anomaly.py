import pytest

from app.features.dns_queries.dns_anomaly import (
    get_suspicious_domain_reasons,
    high_entropy_subdomain_reasons,
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


def test_get_suspicious_domain_reasons_tld():
    reasons = get_suspicious_domain_reasons("cdn.evil.xyz")
    assert any("suspicious TLD (.xyz)" in reason for reason in reasons)


def test_get_suspicious_domain_reasons_entropy():
    domain = "abc123456789012345678901234567890.example.com"
    reasons = get_suspicious_domain_reasons(domain)
    assert any("many digits" in reason for reason in reasons)


def test_high_entropy_subdomain_reasons_describes_label():
    reasons = high_entropy_subdomain_reasons("xk8f2a9m3n7p1q4r5.example.com")
    assert len(reasons) == 1
    assert "xk8f2a9m3n7p1q4r5" in reasons[0]
