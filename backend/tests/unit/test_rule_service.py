from unittest.mock import MagicMock
from app.features.rules.schemas.rule import RuleCreate
from app.features.rules.services.rule_service import create_rule,get_rule_by_id, get_rules
from app.features.rules.models.rule import Rule

def test_create_rule_unit(monkeypatch):
    fake_db = MagicMock()

    monkeypatch.setattr(
        "app.features.rules.repositories.rule_repository.RuleRepository.get_by_domain",
        lambda self, domain: None,
    )

    data = RuleCreate(domain="example.com", reason="Stam")


    rule = create_rule(data, fake_db)


    fake_db.add.assert_called_once()
    fake_db.commit.assert_called_once()
    fake_db.refresh.assert_called_once()

    assert rule.domain == "example.com"

def test_get_rule_by_id_unit(monkeypatch):
    fake_db = MagicMock()
    fake_rule = Rule(id=1, domain="example.com", reason="Stam")

    monkeypatch.setattr(
        "app.features.rules.repositories.rule_repository.RuleRepository.get_by_id",
        lambda self, rule_id: fake_rule,
    )

    rule = get_rule_by_id(1, fake_db)

    assert rule is fake_rule
    assert rule.id == 1
    assert rule.domain == "example.com"

def test_get_rules_unit(monkeypatch):
    fake_db = MagicMock()
    fake_rules = [
        Rule(id=1, domain="example.com", reason="A"),
        Rule(id=2, domain="example.org", reason="B"),
    ]

    monkeypatch.setattr(
        "app.features.rules.repositories.rule_repository.RuleRepository.get_rules",
        lambda self: fake_rules,
    )

    rules = get_rules(fake_db)

    assert rules == fake_rules
    assert len(rules) == 2
