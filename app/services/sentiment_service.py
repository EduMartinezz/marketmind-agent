from typing import List, Dict

POSITIVE_WORDS = [
    "strong",
    "optimistic",
    "growth",
    "expansion",
    "beat",
    "surge",
    "gain",
    "gains",
    "rise",
    "rises",
    "record",
    "improves",
    "improved",
    "bullish",
    "upside",
    "profit",
    "profits",
    "rebound",
    "boost",
    "boosts",
    "momentum",
    "demand strength",
    "higher",
    "buy",
    "strong buy",
    "hopes",
]

NEGATIVE_WORDS = [
    "pressure",
    "warn",
    "warning",
    "risk",
    "concern",
    "slowdown",
    "drop",
    "falls",
    "fall",
    "decline",
    "declines",
    "cuts",
    "cut",
    "weak",
    "lawsuit",
    "regulation",
    "probe",
    "tariff",
    "volatility",
    "loss",
    "losses",
    "margin",
    "margins",
    "competition",
    "recall",
    "inventory",
    "crash",
    "cautious",
    "caution",
    "not a buy",
    "not buying",
    "selloff",
    "downgrade",
    "down",
    "bearish",
    "overvalued",
    "miss",
    "problem",
    "rumor",
    "speculation",
]


def analyze_sentiment(news_items: List[Dict[str, str]]) -> str:
    score = 0

    for item in news_items:
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()

        for phrase in POSITIVE_WORDS:
            if phrase in text:
                score += 1

        for phrase in NEGATIVE_WORDS:
            if phrase in text:
                score -= 2

        # Strong bearish patterns
        if "not buying" in text:
            score -= 3

        if "not a buy" in text:
            score -= 3

        if "delivery miss" in text:
            score -= 2

        if "miss" in text and "delivery" in text:
            score -= 2

        if "problem" in text:
            score -= 1

        if "down " in text and "%" in text:
            score -= 2

        if "crash " in text and "%" in text:
            score -= 3

        # Mixed headline dampener
        if "despite" in text and any(word in text for word in ["miss", "decline", "problem", "warning"]):
            score -= 1

    if score >= 2:
        return "positive"
    if score <= -2:
        return "negative"
    return "neutral"