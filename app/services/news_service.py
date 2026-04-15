import os
from typing import List, Dict, Tuple, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

MARKET_POSITIVE_SIGNALS = [
    "stock",
    "shares",
    "earnings",
    "revenue",
    "profit",
    "profits",
    "margin",
    "guidance",
    "forecast",
    "demand",
    "sales",
    "delivery",
    "deliveries",
    "ai",
    "chip",
    "buy",
    "sell",
    "bull",
    "bear",
    "upgrade",
    "downgrade",
    "valuation",
    "analyst",
    "price target",
    "market",
    "outlook",
    "quarter",
    "q1",
    "q2",
    "q3",
    "q4",
]

MARKET_NEGATIVE_NOISE = [
    "github",
    "package",
    "library",
    "release",
    "version",
    "test",
    "#tech",
    "driver fix",
    "desktop stutters",
    "how to",
    "tutorial",
    "command",
    "fan render",
    "photos",
    "viral",
    "gaming setup",
    "wallpaper",
    "benchmark leak",
]

WEAK_NOISE = [
    "trolling",
    "meme",
    "leak",
    "rumour roundup",
]


def normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def build_search_terms(query: str, ticker: Optional[str] = None) -> List[str]:
    terms = [normalize_text(query)]
    if ticker:
        terms.append(normalize_text(ticker))
    return [term for term in terms if term]


def is_relevant_article(article: dict, query: str, ticker: Optional[str] = None) -> bool:
    title = normalize_text(article.get("title", ""))
    description = normalize_text(article.get("description", ""))
    source_name = normalize_text((article.get("source") or {}).get("name", ""))
    content = f"{title} {description} {source_name}"

    search_terms = build_search_terms(query, ticker)

    if not any(term in content for term in search_terms):
        return False

    for noise in MARKET_NEGATIVE_NOISE:
        if noise in content:
            return False

    return True


def score_article(article: dict, query: str, ticker: Optional[str] = None) -> int:
    title = normalize_text(article.get("title", ""))
    description = normalize_text(article.get("description", ""))
    source_name = normalize_text((article.get("source") or {}).get("name", ""))
    content = f"{title} {description} {source_name}"

    search_terms = build_search_terms(query, ticker)
    score = 0

    for term in search_terms:
        if term in title:
            score += 4
        elif term in description:
            score += 2
        elif term in content:
            score += 1

    for signal in MARKET_POSITIVE_SIGNALS:
        if signal in content:
            score += 2

    # Stronger boost for clearly market-relevant language
    high_value_phrases = [
        "earnings",
        "guidance",
        "forecast",
        "price target",
        "analyst",
        "delivery miss",
        "shares",
        "stock",
        "revenue",
        "profit",
        "margin",
    ]
    for phrase in high_value_phrases:
        if phrase in content:
            score += 3

    # Trusted finance/media boost
    trusted_sources = [
        "bloomberg",
        "reuters",
        "cnbc",
        "marketwatch",
        "fool",
        "yahoo finance",
        "investing.com",
        "benzinga",
        "barron's",
        "the wall street journal",
        "fortune",
        "business insider",
    ]
    for source in trusted_sources:
        if source in source_name:
            score += 2

    # Penalize weak/noisy items
    for noise in MARKET_NEGATIVE_NOISE:
        if noise in content:
            score -= 6

    for weak in WEAK_NOISE:
        if weak in content:
            score -= 2

    # Penalize very short / low-information titles
    if len(title.split()) < 5:
        score -= 2

    return score


def get_news(query: str, ticker: Optional[str] = None) -> List[Dict[str, str]]:
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        return [
            {
                "title": f"No live news source configured for {query}",
                "description": "NEWS_API_KEY is missing.",
            }
        ]

    url = "https://newsapi.org/v2/everything"

    q_parts = [query]
    if ticker:
        q_parts.append(ticker)

    params = {
        "q": " OR ".join(q_parts),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        print(f"News API error: {exc}")
        return [
            {
                "title": f"No strong live news found for {query}",
                "description": "Using fallback market note due to a news API error.",
            }
        ]

    articles = data.get("articles", [])

    filtered_articles = [
        article for article in articles
        if is_relevant_article(article, query, ticker)
    ]

    ranked_articles: List[Tuple[int, dict]] = [
        (score_article(article, query, ticker), article)
        for article in filtered_articles
    ]

    ranked_articles.sort(key=lambda x: x[0], reverse=True)

    news_items: List[Dict[str, str]] = []
    seen_titles = set()

    for score, article in ranked_articles:
        title = article.get("title", "") or ""
        description = article.get("description", "") or ""

        clean_title = title.strip()
        if not clean_title:
            continue

        if clean_title.lower() in seen_titles:
            continue

        if score <= 0:
            continue

        seen_titles.add(clean_title.lower())

        news_items.append(
            {
                "title": clean_title,
                "description": description.strip(),
            }
        )

        if len(news_items) == 5:
            break

    if not news_items:
        return [
            {
                "title": f"No strong live news found for {query}",
                "description": "Using fallback market note due to limited relevant live results.",
            }
        ]

    return news_items