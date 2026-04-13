def analyze_sentiment(news_items):
    positive_words = [
        "strong", "optimistic", "growth", "expansion", "beat", "surge",
        "gain", "gains", "rise", "rises", "record", "improves", "improved",
        "bullish", "upside", "profit", "profits", "rebound"
    ]

    negative_words = [
        "pressure", "warn", "risk", "concern", "slowdown", "drop", "falls",
        "fall", "decline", "declines", "cuts", "cut", "weak", "lawsuit",
        "regulation", "probe", "tariff", "volatility", "loss", "losses",
        "margin", "margins", "competition", "recall"
    ]

    score = 0

    for item in news_items:
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()

        for word in positive_words:
            if word in text:
                score += 1

        for word in negative_words:
            if word in text:
                score -= 1

    if score >= 2:
        return "positive"
    elif score <= -2:
        return "negative"
    else:
        return "neutral"