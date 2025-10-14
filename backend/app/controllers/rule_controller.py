from fastapi import HTTPException
from app.schemas.rule import RuleCreate
from app.services.rule_service import create_rule

def create_rule_controller(rule_data: RuleCreate):
    try:
        return create_rule(rule_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
