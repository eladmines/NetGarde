from app.features.policy.pack_fetch import parse_hosts_file


def test_parse_hosts_file_strips_comments_and_localhosts():
    text = """
# social extension
127.0.0.1 localhost
0.0.0.0 facebook.com
0.0.0.0 www.facebook.com
"""
    domains = parse_hosts_file(text)
    assert "facebook.com" in domains
    assert "localhost" not in domains
    assert len(domains) == 1


def test_parse_hosts_file_normalizes_case():
    text = "0.0.0.0 Facebook.COM\n"
    assert "facebook.com" in parse_hosts_file(text)
