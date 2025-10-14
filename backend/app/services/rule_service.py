from app.models.rule import Rule
from app.schemas.rule import RuleCreate
from app.database import SessionLocal

def create_rule(rule_data: RuleCreate):
    db = SessionLocal()
    new_rule = Rule(**rule_data.model_dump())
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return new_rule