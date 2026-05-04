from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class BriefingRequest(BaseModel):
    query: str
    ticker: Optional[str] = None


class HeadlineAnalysis(BaseModel):
    headline: str
    sentiment_hint: str
    risk_flags: List[str]
    positive_signal_count: Optional[int] = 0
    negative_signal_count: Optional[int] = 0


class BriefingResponse(BaseModel):
    query: str
    ticker: Optional[str] = None
    mode: str
    system_design: Dict[str, Any]
    agent_steps: List[str]
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
    headline_analysis: List[HeadlineAnalysis]