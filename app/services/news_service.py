import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_news(query: str):
    api_key = os.getenv("NEWS_API_KEY")

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    articles = data.get("articles", [])

    news_items = []

    for article in articles:
        news_items.append({
            "title": article.get("title", ""),
            "description": article.get("description", "")
        })

    # fallback if API fails
    if not news_items:
        return [
            {
                "title": "No live news found",
                "description": "Using fallback data"
            }
        ]

    return news_items