from fastapi import APIRouter
from app.schemas.rule import RuleCreate
from app.controllers.rule_controller import create_rule_controller

router = APIRouter(prefix="/rules", tags=["Rules"])

@router.post("/")
def create_rule_endpoint(rule_data: RuleCreate):
    return create_rule_controller(rule_data)
