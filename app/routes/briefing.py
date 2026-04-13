from fastapi import APIRouter
from app.models.schemas import BriefingRequest, BriefingResponse
from app.services.news_service import get_news
from app.services.sentiment_service import analyze_sentiment
from app.services.risk_service import extract_risks
from app.services.llm_service import generate_briefing

router = APIRouter()


@router.post("/briefing", response_model=BriefingResponse)
def create_briefing(request: BriefingRequest):
    news_items = get_news(request.query)
    sentiment = analyze_sentiment(news_items)
    risks = extract_risks(news_items)
    briefing = generate_briefing(request.query, sentiment, risks)

    return BriefingResponse(
        query=request.query,
        sentiment=sentiment,
        outlook=briefing["outlook"],
        key_drivers=briefing["key_drivers"],
        risk_flags=risks,
        confidence=briefing["confidence"],
        summary=briefing["summary"]
    )