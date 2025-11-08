from pydantic import BaseModel, ConfigDict

class RuleCreate(BaseModel):
    domain: str
    reason: str

class RuleRead(BaseModel):
    id: int
    domain: str
    reason: str
    model_config = ConfigDict(from_attributes=True)