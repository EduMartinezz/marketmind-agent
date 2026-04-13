def extract_risks(news_items):
    risk_keywords = [
        "competition",
        "valuation",
        "inflation",
        "pressure",
        "lawsuit",
        "regulation",
        "slowdown",
        "volatility",
        "margins"
    ]

    found_risks = set()

    for item in news_items:
        text = f"{item['title']} {item['description']}".lower()

        for keyword in risk_keywords:
            if keyword in text:
                found_risks.add(keyword)

    return list(found_risks)