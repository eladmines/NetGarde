from app.features.client_behavior.behavior_whitelist import is_whitelisted_root


def test_whitelist_known_roots():
    assert is_whitelisted_root("apple.com")
    assert is_whitelisted_root("cdn.apple.com")


def test_whitelist_unknown():
    assert not is_whitelisted_root("evil.xyz")
