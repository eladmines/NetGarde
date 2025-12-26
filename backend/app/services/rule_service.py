from sqlalchemy.orm import Session
from app.schemas.rule import RuleCreate
from app.repositories.rule_repository import RuleRepository
from app.errors.rule import RuleAlreadyExistsError, RuleNotFoundError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.utils.logging import get_logger

logger = get_logger(__name__)


def create_rule(rule_data: RuleCreate, db: Session):
    repository = RuleRepository(db)
    try:
        logger.info("Creating rule", extra={"domain": rule_data.domain})
        rule = repository.create(rule_data)
        logger.info("Rule created", extra={"rule_id": getattr(rule, "id", None), "domain": rule.domain})
        return rule
    except IntegrityError:
        logger.warning("Rule already exists", extra={"domain": rule_data.domain})
        raise RuleAlreadyExistsError(rule_data.domain)

def get_rule_by_id(rule_id: int, db: Session):
    repository = RuleRepository(db)
    try:
        rule = repository.get_by_id(rule_id)
        if rule is None:
            logger.warning("Rule not found by id", extra={"rule_id": rule_id})
        else:
            logger.info("Fetched rule by id", extra={"rule_id": rule_id})
        return rule
    except IntegrityError:
        logger.error("Integrity error while fetching rule by id", extra={"rule_id": rule_id}, exc_info=True)
        raise RuleNotFoundError(rule_id)

def get_rule_by_domain(rule_domain: str, db: Session):
    repository = RuleRepository(db)
    try:
        rule = repository.get_by_domain(rule_domain)
        if rule is None:
            logger.warning("Rule not found by domain", extra={"domain": rule_domain})
        else:
            logger.info("Fetched rule by domain", extra={"domain": rule_domain})
        return rule
    except IntegrityError:
        logger.error("Integrity error while fetching rule by domain", extra={"domain": rule_domain}, exc_info=True)
        raise RuleNotFoundError(rule_domain)

def get_rules(db: Session):
    repository = RuleRepository(db)
    try:
        rules = repository.get_rules()
        logger.info("Fetched rules", extra={"count": len(rules)})
        return rules
    except SQLAlchemyError as e:
        logger.error("Database error while listing rules", exc_info=True)
        raise e 


