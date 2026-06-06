from app.features.dashboard.services.overview_templates import build_network_overview_bullets


def test_quiet_network_includes_no_anomalies_line():
    bullets = build_network_overview_bullets(
        {
            "period_minutes": 60,
            "live": {"reporting": 0, "total_mib_per_sec": 0},
            "history": {"peak_mib_per_sec": 0},
            "alerts": {"total": 0, "by_type": {}},
            "blocked": {"count": 0, "top_domains": []},
            "policy": {"enabled_pack_names": []},
            "behavior": {"elevated_count": 0, "threshold": 70},
        }
    )
    assert any("No clients are reporting" in b for b in bullets)
    assert any("No security anomalies" in b for b in bullets)


def test_active_network_summarizes_traffic_alerts_and_blocks():
    bullets = build_network_overview_bullets(
        {
            "period_minutes": 30,
            "live": {"reporting": 2, "total_mib_per_sec": 4.5},
            "history": {"peak_mib_per_sec": 9.2},
            "alerts": {"total": 3, "by_type": {"behavior_anomaly": 2, "bandwidth_spike": 1}},
            "blocked": {
                "count": 5,
                "top_domains": [{"domain": "ads.example.com", "count": 3}],
            },
            "policy": {"enabled_pack_names": ["Social"]},
            "behavior": {"elevated_count": 1, "threshold": 70},
        }
    )
    text = " ".join(bullets)
    assert "2 clients reporting" in text
    assert "Peak throughput" in text
    assert "3 DNS alerts" in text
    assert "behavior anomalies" in text
    assert "ads.example.com" in text
    assert "Social" in text
    assert "elevated behavior" in text
