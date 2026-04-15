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


@router.post("/briefing", response_model=BriefingResponse)
def create_briefing(request: BriefingRequest) -> BriefingResponse:
    query = request.query.strip()
    ticker = request.ticker.strip().upper() if request.ticker else None

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Pass ticker if your news_service supports it.
    # If your current get_news only accepts query, change this call back to get_news(query)
    try:
        news_items = get_news(query=query, ticker=ticker)
    except TypeError:
        news_items = get_news(query)

    headlines = [item.get("title", "") for item in news_items if item.get("title")]

    if not headlines:
        raise HTTPException(status_code=404, detail=f"No news found for {query}.")

    sentiment = analyze_sentiment(news_items)
    risks = extract_risks(news_items)
    headline_analysis_raw = analyze_headlines(news_items)
    fallback_outlook = determine_outlook(sentiment, risks)

    briefing = generate_briefing(
        query=query if not ticker else f"{query} ({ticker})",
        sentiment=sentiment,
        risks=risks,
        headlines=headlines,
        fallback_outlook=fallback_outlook,
    )

    return BriefingResponse(
        query=query,
        ticker=ticker,
        headlines=headlines,
        sentiment=sentiment,
        outlook=briefing["outlook"],
        key_drivers=briefing["key_drivers"],
        risk_flags=risks,
        confidence=briefing["confidence"],
        summary=briefing["summary"],
        headline_analysis=[
            HeadlineAnalysis(**item) for item in headline_analysis_raw
        ],
    )