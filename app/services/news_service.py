import os
from typing import List, Dict, Tuple, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

MARKET_POSITIVE_SIGNALS = [
    "stock", "shares", "earnings", "revenue", "profit", "profits",
    "margin", "guidance", "forecast", "demand", "sales", "delivery",
    "deliveries", "buy", "sell", "bull", "bear", "upgrade",
    "downgrade", "valuation", "analyst", "price target", "market",
    "outlook", "quarter", "q1", "q2", "q3", "q4"
]

HIGH_VALUE_PHRASES = [
    "earnings", "guidance", "forecast", "price target", "analyst",
    "delivery miss", "shares", "stock", "revenue", "profit",
    "margin", "sales decline", "warning", "downgrade", "upgrade",
    "not a buy", "too cheap to ignore",
]

MARKET_NEGATIVE_NOISE = [
    "github", "package", "library", "release", "version", "test",
    "#tech", "driver fix", "desktop stutters", "how to", "tutorial",
    "command", "fan render", "photos", "viral", "gaming setup",
    "wallpaper", "benchmark leak",
    "pypi", "npm", "python package", "nat-app", "app 1."
]

WEAK_NOISE = [
    "trolling", "meme", "leak", "rumour roundup",
]

CONSUMER_TECH_NOISE = [
    "spring update", "owners spot", "hands-on", "review",
    "looks improved", "feature update", "software update",
    "confirmed for australia", "track how often drivers use",
    "stats to track",
]

TRUSTED_SOURCES = [
    "bloomberg", "reuters", "cnbc", "marketwatch", "fool",
    "yahoo finance", "investing.com", "benzinga", "barron's",
    "fortune", "business insider", "wall street journal",
]

COMPANY_COMPETITORS = {
    "nvidia": ["tesla", "amd", "intel", "apple", "microsoft", "amazon", "meta", "google"],
    "tesla": ["nvidia", "rivian", "ford", "gm", "byd", "lucid"],
}


def normalize_text(text: Optional[str]) -> str:
    return (text or "").strip().lower()


def build_search_terms(query: str, ticker: Optional[str] = None) -> List[str]:
    terms = [normalize_text(query)]
    if ticker:
        terms.append(normalize_text(ticker))
    return [term for term in terms if term]


def title_signature(title: str) -> str:
    clean = normalize_text(title)
    return clean[:90]


def is_relevant_article(article: dict, query: str, ticker: Optional[str] = None) -> bool:
    title = normalize_text(article.get("title"))
    description = normalize_text(article.get("description"))
    source_name = normalize_text((article.get("source") or {}).get("name"))
    content = f"{title} {description} {source_name}"

    search_terms = build_search_terms(query, ticker)

    # must mention company/ticker
    if not any(term in content for term in search_terms):
        return False

    # remove obvious noise
    for noise in MARKET_NEGATIVE_NOISE:
        if noise in content:
            return False

    # reject competitor-led headlines
    company_key = normalize_text(query)
    competitors = COMPANY_COMPETITORS.get(company_key, [])

    if competitors:
        target_terms = build_search_terms(query, ticker)
        target_in_title = any(term in title for term in target_terms)
        competitor_in_title = any(comp in title for comp in competitors)

        if competitor_in_title and not target_in_title:
            return False

    return True


def score_article(article: dict, query: str, ticker: Optional[str] = None) -> int:
    title = normalize_text(article.get("title"))
    description = normalize_text(article.get("description"))
    source_name = normalize_text((article.get("source") or {}).get("name"))
    content = f"{title} {description} {source_name}"

    search_terms = build_search_terms(query, ticker)
    company_name = normalize_text(query)
    score = 0

    # direct mention
    for term in search_terms:
        if term in title:
            score += 6
        elif term in description:
            score += 2
        elif term in content:
            score += 1

    if company_name in title:
        score += 3

    # finance signals
    for signal in MARKET_POSITIVE_SIGNALS:
        if signal in content:
            score += 2

    for phrase in HIGH_VALUE_PHRASES:
        if phrase in content:
            score += 3

    # trusted source boost
    for source in TRUSTED_SOURCES:
        if source in source_name:
            score += 2

    # intent boost
    if any(term in content for term in ["stock", "shares", "analyst", "earnings"]):
        score += 3

    # penalties
    for noise in MARKET_NEGATIVE_NOISE:
        if noise in content:
            score -= 8

    for weak in WEAK_NOISE:
        if weak in content:
            score -= 2

    for noise in CONSUMER_TECH_NOISE:
        if noise in content:
            score -= 3

    if len(title.split()) < 5:
        score -= 2

    return score


def get_news(query: str, ticker: Optional[str] = None) -> List[Dict[str, object]]:
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        return [{
            "title": f"No live news source configured for {query}",
            "description": "NEWS_API_KEY is missing.",
            "source": "system",
            "score": 0,
        }]

    query_clean = query.strip()
    ticker_clean = ticker.strip().upper() if ticker else None

    url = "https://newsapi.org/v2/everything"
    q_parts = [query_clean]
    if ticker_clean:
        q_parts.append(ticker_clean)

    params = {
        "q": " OR ".join(q_parts),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 30,
        "apiKey": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return [{
            "title": f"No strong live news found for {query_clean}",
            "description": "Fallback due to API error.",
            "source": "system",
            "score": 0,
        }]

    articles = data.get("articles", [])

    filtered = [
        a for a in articles
        if is_relevant_article(a, query_clean, ticker_clean)
    ]

    ranked: List[Tuple[int, dict]] = [
        (score_article(a, query_clean, ticker_clean), a)
        for a in filtered
    ]

    ranked.sort(key=lambda x: x[0], reverse=True)

    news_items: List[Dict[str, object]] = []
    seen_titles = set()

    for score, article in ranked:
        title = (article.get("title") or "").strip()
        description = (article.get("description") or "").strip()
        source_name = ((article.get("source") or {}).get("name") or "unknown").strip()

        if not title:
            continue

        signature = title_signature(title)

        if signature in seen_titles:
            continue

        if score <= 3:
            continue

        seen_titles.add(signature)

        news_items.append({
            "title": title,
            "description": description,
            "source": source_name,
            "score": score,
        })

        if len(news_items) == 5:
            break

    if not news_items:
        return [{
            "title": f"No strong live news found for {query_clean}",
            "description": "Fallback due to low relevance.",
            "source": "system",
            "score": 0,
        }]

    return news_items