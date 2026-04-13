from fastapi import FastAPI

app = FastAPI(title="MarketMind Agent")

@app.get("/")
def home():
    return {"message": "MarketMind Agent is running"}