def analyze_sentiment(news_items):
    positive_words = ["strong", "optimistic", "growth", "expansion"]
    negative_words = ["pressure", "warn", "risk", "concern", "slowdown"]

    score = 0

    for item in news_items:
        text = f"{item['title']} {item['description']}".lower()

        for word in positive_words:
            if word in text:
                score += 1

        for word in negative_words:
            if word in text:
                score -= 1

    if score > 1:
        return "positive"
    elif score < -1:
        return "negative"
    else:
        return "neutral"