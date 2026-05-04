from app.services.news_service import get_news
from app.services.sentiment_service import analyze_sentiment
from app.services.risk_service import extract_risks

TOOLS = {
    "get_news": get_news,
    "analyze_sentiment": analyze_sentiment,
    "extract_risks": extract_risks,
}