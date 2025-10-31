from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.rule import RuleCreate
from app.services.rule_service import create_rule, get_rule_by_id, get_rule_by_domain
from app.errors.rule import RuleAlreadyExistsError, RuleNotFoundError
from app.utils.logging import get_logger

logger = get_logger(__name__)

def create_rule_controller(rule_data: RuleCreate, db: Session):
    try:
        logger.info("POST /rules - create", extra={"domain": rule_data.domain})
        result = create_rule(rule_data, db)
        logger.info("POST /rules - created", extra={"rule_id": getattr(result, "id", None)})
        return result
    except RuleAlreadyExistsError as e:
        logger.warning("POST /rules - conflict", extra={"domain": rule_data.domain})
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error("POST /rules - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

def get_rule_by_id_controller(rule_id: int, db: Session):
    try:
        logger.info("GET /rules/{rule_id} - fetch", extra={"rule_id": rule_id})
        rule = get_rule_by_id(rule_id, db)
        if rule is None:
            raise RuleNotFoundError(rule_id)
        logger.info("GET /rules/{rule_id} - ok", extra={"rule_id": rule_id})
        return rule
    except RuleNotFoundError as e:
        logger.warning("GET /rules/{rule_id} - not found", extra={"rule_id": rule_id})
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("GET /rules/{rule_id} - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

def get_rule_by_domain_controller(rule_domain: str, db: Session):
    try:
        logger.info("GET /rules/by-domain - fetch", extra={"domain": rule_domain})
        rule = get_rule_by_domain(rule_domain, db)
        if rule is None:
            raise RuleNotFoundError(rule_domain)
        logger.info("GET /rules/by-domain - ok", extra={"domain": rule_domain})
        return rule
    except RuleNotFoundError as e:
        logger.warning("GET /rules/by-domain - not found", extra={"domain": rule_domain})
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("GET /rules/by-domain - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
