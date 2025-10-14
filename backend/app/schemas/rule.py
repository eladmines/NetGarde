from pydantic import BaseModel

class RuleCreate(BaseModel):
    domain: str
    reason: str

class RuleRead(BaseModel):
    id: int
    domain: str
    reason: str

    class Config:
            orm_mode = True