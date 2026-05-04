from typing import List, Optional
from pydantic import BaseModel, Field


class HeadlineAnalysis(BaseModel):
    headline: str
    sentiment_hint: str
    risk_flags: List[str]


class BriefingRequest(BaseModel):
    query: str
    ticker: Optional[str] = None


class BriefingResponse(BaseModel):
    query: str
    ticker: Optional[str] = None
    headlines: List[str]
    sentiment: str
    outlook: str
    key_drivers: List[str]
    risk_flags: List[str]
    confidence: str
    summary: str
    llm_used: bool
    article_count: int
    source_names: List[str]
    article_scores: List[int]
    headline_analysis: List[HeadlineAnalysis] = Field(default_factory=list)
    agent_steps: List[str]