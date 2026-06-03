"""Unit tests for dnsmasq block line generation."""

from sync import block_domain_dnsmasq_lines, domains_to_dnsmasq_lines


def test_block_domain_emits_ipv4_and_ipv6():
    lines = block_domain_dnsmasq_lines("facebook.com", "0.0.0.0", "::")
    assert lines == [
        "address=/facebook.com/0.0.0.0",
        "address=/facebook.com/::",
    ]


def test_domains_dedupes_and_dual_stack():
    lines = domains_to_dnsmasq_lines(
        ["facebook.com", "Facebook.COM", "https://www.foo.com/"],
        "0.0.0.0",
        "::",
    )
    assert "address=/facebook.com/0.0.0.0" in lines
    assert "address=/facebook.com/::" in lines
    assert "address=/foo.com/0.0.0.0" in lines
    assert "address=/foo.com/::" in lines
    assert len(lines) == 4
