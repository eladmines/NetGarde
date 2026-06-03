from app.features.policy.pack_fetch import list_pack_domains_page, write_snapshot


def test_list_pack_domains_page_search_and_pagination(tmp_path, monkeypatch):
    from app.features.policy import pack_fetch

    monkeypatch.setattr(pack_fetch, "DATA_DIR", tmp_path)
    monkeypatch.setattr(pack_fetch, "SNAPSHOT_DIR", tmp_path / "snapshots")
    write_snapshot("social", {"alpha.com", "beta.com", "gamma.net"})

    page1, total, source = list_pack_domains_page("social", skip=0, limit=2)
    assert source == "snapshot"
    assert total == 3
    assert len(page1) == 2

    page2, total2, _ = list_pack_domains_page("social", skip=2, limit=2)
    assert total2 == 3
    assert len(page2) == 1

    filtered, ftotal, _ = list_pack_domains_page("social", q="beta", skip=0, limit=10)
    assert ftotal == 1
    assert filtered == ["beta.com"]
