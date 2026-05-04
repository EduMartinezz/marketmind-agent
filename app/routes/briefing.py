from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    BriefingRequest,
    BriefingResponse,
    HeadlineAnalysis,
)
from app.agents.multi_agent_marketmind import run_multi_agent_marketmind

router = APIRouter(tags=["Market Briefing"])


TICKER_FIXES = {
    "NVDIA": "NVDA",
    "NVIDIA": "NVDA",
    "TESLA": "TSLA",
    "APPLE": "AAPL",
    "MICROSOFT": "MSFT",
    "AMAZON": "AMZN",
    "META": "META",
    "GOOGLE": "GOOGL",
    "ALPHABET": "GOOGL",
}


SYSTEM_DESIGN = {
    "architecture": "Multi-Agent AI System",
    "framework": "LangGraph",
    "api_layer": "FastAPI",
    "agents": [
        "News Agent",
        "Risk Agent",
        "Analyst Agent",
    ],
    "flow": [
        "User Query",
        "News Agent",
        "Risk Agent",
        "Analyst Agent",
        "Market Briefing Output",
    ],
    "fallback_strategy": "Graceful LLM fallback using deterministic market reasoning",
}


def normalize_ticker(query: str, ticker: str | None) -> str | None:
    if ticker:
        clean_ticker = ticker.strip().upper()
        return TICKER_FIXES.get(clean_ticker, clean_ticker)

    query_key = query.strip().upper()
    return TICKER_FIXES.get(query_key)


@router.post("/briefing", response_model=BriefingResponse)
def create_briefing(request: BriefingRequest) -> BriefingResponse:
    query = request.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    normalized_query = query.title()
    ticker = normalize_ticker(query=query, ticker=request.ticker)

    agent_output = run_multi_agent_marketmind(
        query=normalized_query,
        ticker=ticker,
    )

    headlines = agent_output.get("headlines", [])

    if not headlines:
        raise HTTPException(
            status_code=404,
            detail=f"No news found for {normalized_query}.",
        )

    briefing = agent_output.get("briefing", {})

    return BriefingResponse(
        query=normalized_query,
        ticker=ticker,
        mode="multi-agent",
        system_design=SYSTEM_DESIGN,
        agent_steps=agent_output.get("agent_steps", []),
        headlines=headlines,
        sentiment=agent_output.get("sentiment", "neutral"),
        outlook=briefing.get("outlook", agent_output.get("fallback_outlook", "neutral")),
        key_drivers=briefing.get("key_drivers", []),
        risk_flags=agent_output.get("risks", []),
        confidence=briefing.get("confidence", "low"),
        summary=briefing.get("summary", "No summary generated."),
        llm_used=briefing.get("llm_used", False),
        article_count=len(headlines),
        source_names=agent_output.get("source_names", []),
        article_scores=agent_output.get("article_scores", []),
        headline_analysis=[
            HeadlineAnalysis(**item)
            for item in agent_output.get("headline_analysis", [])
        ],
    )


@router.post("/agent/trace")
def get_agent_trace(request: BriefingRequest):
    query = request.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    normalized_query = query.title()
    ticker = normalize_ticker(query=query, ticker=request.ticker)

    agent_output = run_multi_agent_marketmind(
        query=normalized_query,
        ticker=ticker,
    )

    return {
        "query": normalized_query,
        "ticker": ticker,
        "mode": "multi-agent",
        "agent_type": "LangGraph multi-agent market intelligence system",
        "system_design": SYSTEM_DESIGN,
        "agent_roles": agent_output.get("agent_roles", {}),
        "graph_flow": [
            "news_agent",
            "risk_agent",
            "analyst_agent",
        ],
        "agent_steps": agent_output.get("agent_steps", []),
        "state_snapshot": {
            "article_count": len(agent_output.get("headlines", [])),
            "sentiment": agent_output.get("sentiment", "neutral"),
            "risk_flags": agent_output.get("risks", []),
            "fallback_outlook": agent_output.get("fallback_outlook", "neutral"),
            "llm_used": agent_output.get("briefing", {}).get("llm_used", False),
        },
        "headlines": agent_output.get("headlines", []),
        "headline_analysis": agent_output.get("headline_analysis", []),
    }


@router.get("/agent/health")
def get_agent_health():
    return {
        "api_status": "running",
        "mode": "multi-agent",
        "agent_framework": "LangGraph",
        "agent_type": "Multi-agent market intelligence system",
        "system_design": SYSTEM_DESIGN,
        "graph_nodes": [
            "news_agent",
            "risk_agent",
            "analyst_agent",
        ],
        "available_routes": [
            "/briefing",
            "/agent/trace",
            "/agent/health",
        ],
        "llm_layer": {
            "status": "fallback_active",
            "reason": "LLM provider quota unavailable or optional",
            "fallback": "deterministic market reasoning engine",
        },
        "production_features": [
            "ticker normalization",
            "news relevance filtering",
            "multi-agent orchestration",
            "risk extraction",
            "sentiment analysis",
            "agent execution trace",
            "graceful LLM fallback",
            "system health reporting",
        ],
    }