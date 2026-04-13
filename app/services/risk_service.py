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
        "margins",
        "margin",
        "tariff",
        "probe",
        "recall",
        "supply chain",
        "demand weakness",
        "uncertainty",
        "rate cut",
        "interest rates",
        "china"
    ]

    found_risks = []

    for item in news_items:
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()

        for keyword in risk_keywords:
            if keyword in text and keyword not in found_risks:
                found_risks.append(keyword)

    return found_risks