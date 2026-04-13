def generate_briefing(query, sentiment, risks):
    risk_count = len(risks)

    if sentiment == "positive" and risk_count == 0:
        outlook = "bullish"
        confidence = "medium"
    elif sentiment == "positive" and risk_count >= 1:
        outlook = "neutral"
        confidence = "medium"
    elif sentiment == "negative":
        outlook = "cautious"
        confidence = "medium"
    else:
        outlook = "neutral"
        confidence = "low"

    key_drivers = [
        f"Recent headlines linked to {query}",
        f"Overall sentiment appears {sentiment}",
        f"Detected {risk_count} risk flag(s) in recent coverage"
    ]

    if risks:
        risk_text = ", ".join(risks)
    else:
        risk_text = "general market uncertainty"

    summary = (
        f"MarketMind analysis for {query}: sentiment is {sentiment}. "
        f"The near-term outlook is {outlook}. "
        f"Main risks include {risk_text}."
    )

    return {
        "outlook": outlook,
        "confidence": confidence,
        "key_drivers": key_drivers,
        "summary": summary
    }