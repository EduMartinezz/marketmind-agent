from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    BriefingRequest,
    BriefingResponse,
    HeadlineAnalysis,
)
from app.services.news_service import get_news
from app.services.sentiment_service import analyze_sentiment
from app.services.risk_service import extract_risks, analyze_headlines, determine_outlook
from app.services.llm_service import generate_briefing

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

    agent_steps = [
        "Received company or ticker query",
        "Resolved company query to ticker where possible",
        "Collected recent market headlines",
        "Filtered and ranked company-relevant articles",
        "Analysed sentiment signals across headlines",
        "Extracted financial and operational risk flags",
        "Generated final analyst-style market outlook",
    ]

    news_items = get_news(query=normalized_query, ticker=ticker)

    headlines = [item.get("title", "") for item in news_items if item.get("title")]
    source_names = [item.get("source", "unknown") for item in news_items]
    article_scores = [int(item.get("score", 0)) for item in news_items]

    if not headlines:
        raise HTTPException(status_code=404, detail=f"No news found for {normalized_query}.")

    sentiment = analyze_sentiment(news_items)
    risks = extract_risks(news_items)
    headline_analysis_raw = analyze_headlines(news_items)
    fallback_outlook = determine_outlook(sentiment, risks)

    llm_query_label = normalized_query if not ticker else f"{normalized_query} ({ticker})"

    briefing = generate_briefing(
        query=llm_query_label,
        sentiment=sentiment,
        risks=risks,
        headlines=headlines,
        fallback_outlook=fallback_outlook,
    )

    return BriefingResponse(
        query=normalized_query,
        ticker=ticker,
        agent_steps=agent_steps,
        headlines=headlines,
        sentiment=sentiment,
        outlook=briefing["outlook"],
        key_drivers=briefing["key_drivers"],
        risk_flags=risks,
        confidence=briefing["confidence"],
        summary=briefing["summary"],
        llm_used=briefing["llm_used"],
        article_count=len(headlines),
        source_names=source_names,
        article_scores=article_scores,
        headline_analysis=[
            HeadlineAnalysis(**item) for item in headline_analysis_raw
        ],
    )