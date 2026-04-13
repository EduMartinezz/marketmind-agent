from fastapi import FastAPI
from app.routes.briefing import router as briefing_router

app = FastAPI(title="MarketMind Agent")

app.include_router(briefing_router)


@app.get("/")
def home():
    return {"message": "MarketMind Agent is running"}