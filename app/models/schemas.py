from pydantic import BaseModel
from typing import List


class BriefingRequest(BaseModel):
    query: str


class BriefingResponse(BaseModel):
    query: str
    sentiment: str
    outlook: str
    key_drivers: List[str]
    risk_flags: List[str]
    confidence: str
    summary: str