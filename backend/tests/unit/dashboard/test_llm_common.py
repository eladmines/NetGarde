from app.features.dashboard.services.llm_common import compact_snapshot_for_llm


def test_compact_snapshot_trims_top_domains():
    compact = compact_snapshot_for_llm(
        {
            "period_minutes": 60,
            "blocked": {
                "count": 10,
                "top_domains": [
                    {"domain": "a.com", "count": 5},
                    {"domain": "b.com", "count": 4},
                    {"domain": "c.com", "count": 3},
                    {"domain": "d.com", "count": 2},
                ],
            },
            "alerts": {"total": 1, "by_type": {"x": 1}},
            "live": {},
            "history": {},
            "policy": {},
            "behavior": {},
        }
    )
    assert len(compact["blocked"]["top_domains"]) == 3
