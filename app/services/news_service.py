import os
import requests
from dotenv import load_dotenv

load_dotenv()


def is_relevant_article(article, query: str):
    title = (article.get("title") or "").lower()
    description = (article.get("description") or "").lower()
    content = f"{title} {description}"

    query_lower = query.lower()

    bad_keywords = [
        "pypowerwall",
        "github",
        "software release",
        "library",
        "package"
    ]

    for bad_word in bad_keywords:
        if bad_word in content:
            return False

    return query_lower in content


def get_news(query: str):
    api_key = os.getenv("NEWS_API_KEY")

    url = "https://newsapi.org/v2/everything"

    params = {
        "qInTitle": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    articles = data.get("articles", [])

    filtered_articles = [
        article for article in articles
        if is_relevant_article(article, query)
    ]

    news_items = []

    for article in filtered_articles[:5]:
        news_items.append({
            "title": article.get("title", ""),
            "description": article.get("description", "")
        })

    if not news_items:
        return [
            {
                "title": f"No strong live news found for {query}",
                "description": "Using fallback market note due to limited relevant live results."
            }
        ]

    return news_items