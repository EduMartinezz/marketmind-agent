# MarketMind Agent

MarketMind Agent is an LLM-powered financial research and risk briefing assistant built with FastAPI.

## What it does

It helps answer market questions like:

- What are the biggest risks for Tesla this week?
- Summarise market-moving news on Nvidia and give a risk outlook.
- Should I watch GBP/USD today? Why?

The current version:

- accepts a market query
- retrieves matching news from sample data
- performs simple sentiment analysis
- extracts key risk themes
- returns a structured analyst-style briefing

## Example output

```json
{
  "query": "Tesla",
  "sentiment": "negative",
  "outlook": "cautious",
  "key_drivers": [
    "Recent headlines linked to Tesla",
    "Overall sentiment appears negative",
    "Short-term market attention remains elevated"
  ],
  "risk_flags": [
    "margins",
    "pressure",
    "competition"
  ],
  "confidence": "medium",
  "summary": "MarketMind analysis for Tesla: sentiment is negative. The near-term outlook is cautious. Main risks include margins, pressure, competition."
}