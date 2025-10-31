from fastapi import FastAPI, Depends
from app.utils.logging import setup_logging
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.routes.rule_route import router as rule_router
from app.routes.rule_route import router
# Initialize logging early
setup_logging()

app = FastAPI(title="NetGarde API")

@app.get("/health")
def health(db: Session = Depends(get_db)):
    return {"status": "ok"}

app.include_router(rule_router)
