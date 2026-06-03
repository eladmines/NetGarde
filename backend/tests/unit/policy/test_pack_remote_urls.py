from app.features.policy.pack_common import BUILTIN_PACK_SLUGS, REMOTE_PACK_SLUGS
from app.features.policy.pack_fetch import (
    DEFAULT_REMOTE_PACK_URLS,
    parse_domain_list,
    parse_pack_text,
    remote_pack_url,
)


def test_all_builtin_packs_are_remote_refreshable():
    assert REMOTE_PACK_SLUGS == frozenset(BUILTIN_PACK_SLUGS)


def test_default_remote_urls_for_every_pack():
    for slug in BUILTIN_PACK_SLUGS:
        assert slug in DEFAULT_REMOTE_PACK_URLS
        assert DEFAULT_REMOTE_PACK_URLS[slug].startswith("https://")


def test_parse_domain_list_plain_text():
    text = "# games\nsteampowered.com\n\nepicgames.com\n"
    domains = parse_domain_list(text)
    assert domains == {"steampowered.com", "epicgames.com"}


def test_parse_pack_text_prefers_hosts_format():
    text = "0.0.0.0 facebook.com\nsteampowered.com\n"
    domains = parse_pack_text(text)
    assert "facebook.com" in domains
    assert "steampowered.com" not in domains


def test_parse_pack_text_falls_back_to_plain():
    text = "steampowered.com\nepicgames.com\n"
    assert parse_pack_text(text) == {"steampowered.com", "epicgames.com"}


def test_remote_pack_url_uses_defaults(monkeypatch):
    from app.shared import config as config_mod

    monkeypatch.setattr(config_mod.settings, "POLICY_PACK_FETCH_ENABLED", True)
    monkeypatch.setattr(config_mod.settings, "POLICY_PACK_REMOTE_URLS", "")
    assert remote_pack_url("adult") == DEFAULT_REMOTE_PACK_URLS["adult"]
    assert remote_pack_url("games") == DEFAULT_REMOTE_PACK_URLS["games"]
