from pydantic import BaseModel


class WhoisLookupResponse(BaseModel):
    domain: str
    source: str
    text: str
