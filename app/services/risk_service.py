from typing import List, Dict

RISK_KEYWORDS = {
    "competition": [
        "competition",
        "rival",
        "rivals",
        "market share",
        "smarter play",
    ],
    "valuation": [
        "valuation",
        "overvalued",
        "not a buy",
        "not buying",
        "musk premium",
    ],
    "inflation": [
        "inflation",
    ],
    "margin pressure": [
        "pressure",
        "margins",
        "margin",
    ],
    "lawsuit": [
        "lawsuit",
        "litigation",
    ],
    "regulation": [
        "regulation",
        "regulatory",
        "probe",
        "investigation",
        "scrutiny",
    ],
    "slowdown": [
        "slowdown",
        "weak demand",
        "soft demand",
        "demand slowdown",
        "slowing demand",
        "decline",
    ],
    "volatility": [
        "volatility",
        "volatile",
        "crash",
        "selloff",
        "down 30%",
        "crash 60%",
    ],
    "tariff": [
        "tariff",
    ],
    "recall": [
        "recall",
    ],
    "supply chain": [
        "supply chain",
        "shortage",
        "disruption",
    ],
    "uncertainty": [
        "uncertainty",
        "caution",
        "high caution",
        "warns",
        "warning",
        "rumor",
        "speculation",
    ],
    "inventory": [
        "inventory",
        "overstock",
        "unsold",
    ],
    "china exposure": [
        "china",
    ],
    "demand weakness": [
        "weak demand",
        "soft demand",
        "demand slowdown",
        "slowing demand",
    ],
    "analyst downgrade": [
        "not a buy",
        "not buying",
        "downgrade",
        "price target cut",
    ],
    "execution risk": [
        "must overcome",
        "execution",
        "problem",
        "delay",
        "delivery miss",
        "miss",
    ],
    "m&a speculation": [
        "negotiating to buy",
        "buy a large company",
        "rumor says",
        "final negotiations",
        "acquisition rumor",
    ],
}


def extract_risks(news_items: List[Dict[str, str]]) -> List[str]:
    found_risks: List[str] = []

    for item in news_items:
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()

        for risk_label, keywords in RISK_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                if risk_label not in found_risks:
                    found_risks.append(risk_label)

    return found_risks


def determine_outlook(sentiment: str, risks: List[str]) -> str:
    risk_count = len(risks)

    if sentiment == "positive" and risk_count == 0:
        return "bullish"

    if sentiment == "positive" and risk_count >= 1:
        return "neutral"

    if sentiment == "negative":
        return "cautious"

    if sentiment == "neutral" and risk_count >= 3:
        return "cautious"

    return "neutral"


def analyze_headlines(news_items: List[Dict[str, str]]) -> List[Dict[str, object]]:
    analysis: List[Dict[str, object]] = []

    positive_words = [
        "strong",
        "growth",
        "beat",
        "surge",
        "gain",
        "record",
        "profit",
        "boost",
        "expansion",
        "rebound",
        "improves",
        "higher",
        "buy",
        "strong buy",
        "hopes",
    ]

    negative_words = [
        "pressure",
        "risk",
        "slowdown",
        "drop",
        "decline",
        "weak",
        "lawsuit",
        "regulation",
        "probe",
        "tariff",
        "volatility",
        "margin",
        "recall",
        "inventory",
        "crash",
        "caution",
        "cautious",
        "warn",
        "warning",
        "not a buy",
        "not buying",
        "down",
        "unsold",
        "overstock",
        "problem",
        "miss",
        "rumor",
        "speculation",
    ]

    for item in news_items:
        headline = item.get("title", "")
        description = item.get("description", "")
        text = f"{headline} {description}".lower()

        pos_hits = sum(1 for word in positive_words if word in text)
        neg_hits = sum(1 for word in negative_words if word in text)

        # Extra negative weighting for stronger signals
        if "inventory" in text:
            neg_hits += 2

        if "not buying" in text or "not a buy" in text:
            neg_hits += 3

        if "delivery miss" in text:
            neg_hits += 2

        if "problem" in text:
            neg_hits += 1

        if "rumor" in text:
            neg_hits += 1

        if "down " in text and "%" in text:
            neg_hits += 2

        if "crash " in text and "%" in text:
            neg_hits += 3

        if pos_hits > neg_hits:
            sentiment_hint = "positive"
        elif neg_hits > pos_hits:
            sentiment_hint = "negative"
        else:
            sentiment_hint = "neutral"

        local_risks: List[str] = []
        for risk_label, keywords in RISK_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                local_risks.append(risk_label)

        analysis.append(
            {
                "headline": headline,
                "sentiment_hint": sentiment_hint,
                "risk_flags": local_risks,
            }
        )

    return analysis