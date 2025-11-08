from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.rule import Rule
from app.schemas.rule import RuleCreate


class RuleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: RuleCreate) -> Rule:
        new_rule = Rule(**data.model_dump())
        self.db.add(new_rule)
        self.db.commit()
        self.db.refresh(new_rule)
        return new_rule

    def get_by_id(self, rule_id: int) -> Optional[Rule]:
        return (
            self.db.query(Rule)
            .filter(Rule.id == rule_id, Rule.deleted_at.is_(None))
            .first()
        )

    def get_by_domain(self, domain: str) -> Optional[Rule]:
        return (
            self.db.query(Rule)
            .filter(Rule.domain == domain, Rule.deleted_at.is_(None))
            .first()
        )

    def get_rules(self) -> List[Rule]:
        return (
            self.db.query(Rule)
            .filter(Rule.deleted_at.is_(None))
            .all()
        )

    def delete(self, rule_id: int) -> bool:
        rule = self.db.query(Rule).filter(Rule.id == rule_id, Rule.deleted_at.is_(None)).first()
        if not rule:
            return False
        rule.deleted_at = datetime.now()
        self.db.commit()
        return True
    
    


