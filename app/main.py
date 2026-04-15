from fastapi import FastAPI
from app.routes.briefing import router as briefing_router

app = FastAPI(
    title="MarketMind Agent",
    description="AI-powered market briefing API for company news, sentiment, and risk analysis.",
    version="1.0.0",
)

app.include_router(briefing_router)


@app.get("/")
def home() -> dict:
    return {"message": "MarketMind Agent is running"}