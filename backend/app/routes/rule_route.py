from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.rule import RuleCreate
from app.controllers.rule_controller import create_rule_controller, get_rule_by_id_controller, get_rules_controller
from app.dependencies import get_db

router = APIRouter(prefix="/rules", tags=["Rules"])

@router.post("/")
def create_rule_endpoint(rule_data: RuleCreate, db: Session = Depends(get_db)):
    return create_rule_controller(rule_data, db)

@router.get("/")
def get_rules_endpoint(db: Session = Depends(get_db)):
    return get_rules_controller(db)

@router.get("/{rule_id}")
def get_rule_by_id_endpoint(rule_id: int, db: Session = Depends(get_db)):
    return get_rule_by_id_controller(rule_id, db)



