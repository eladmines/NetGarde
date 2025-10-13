from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal

app = FastAPI(title="NetGarde API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health(db: Session = Depends(get_db)):
    return {"status": "ok"}

