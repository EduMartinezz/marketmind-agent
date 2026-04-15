# MarketMind Agent

MarketMind Agent is an AI-powered FastAPI microservice that transforms live company news into structured, decision-oriented market briefings.

Instead of simply listing headlines, the system extracts sentiment, detects hidden risks, analyzes each headline individually, and produces a clear market outlook such as **bullish**, **neutral**, or **cautious**.

This project demonstrates how modern AI systems can move beyond prediction into **real-world decision support**.

---

## Why I Built This

Most financial tools stop at:

→ “Here’s what’s happening.”

But real-world decisions require:

→ “What should I do about it?”

MarketMind Agent bridges that gap by combining:

- real-time data ingestion
- rule-based signal extraction
- explainable reasoning
- LLM-assisted summarization
- resilient fallback logic

The goal is simple:

> Turn noisy market information into structured intelligence.

---

## Core Features

- Fetches live company news via NewsAPI
- Supports both **company name** and **ticker symbol**
- Detects sentiment from market-facing language
- Extracts key risk signals such as:
  - valuation
  - volatility
  - analyst downgrade
  - supply chain
  - regulation
  - China exposure
  - execution risk
  - uncertainty
  - M&A speculation
- Performs headline-level sentiment and risk analysis
- Filters and ranks articles for market relevance
- Generates structured market briefings
- Uses modular, production-style service architecture
- Includes fallback logic if the LLM is unavailable

---

## Example Input

```json
{
  "query": "Tesla",
  "ticker": "TSLA"
}
```

## Example Output
{
  "query": "Tesla",
  "ticker": "TSLA",
  "headlines": [
    "Prediction: Down 30%, Tesla Stock Is Still Not a Buy Ahead of Its Earnings Later This Month",
    "Tesla Stock Edges Higher Amid Cheaper EV Plans and Robotaxi Hopes Despite Q1 Delivery Miss",
    "As China Sales Decline, How Should You Play Tesla Stock in Q2?"
  ],
  "sentiment": "negative",
  "outlook": "cautious",
  "key_drivers": [
    "Recent headlines linked to Tesla",
    "Overall sentiment appears negative",
    "Detected 4 risk flag(s) in recent coverage"
  ],
  "risk_flags": [
    "valuation",
    "volatility",
    "analyst downgrade",
    "china exposure"
  ],
  "confidence": "medium",
  "summary": "MarketMind analysis for Tesla: sentiment is negative. The near-term outlook is cautious. Main risks include valuation, volatility, analyst downgrade, and China exposure.",
  "headline_analysis": [
    {
      "headline": "Prediction: Down 30%, Tesla Stock Is Still Not a Buy Ahead of Its Earnings Later This Month",
      "sentiment_hint": "negative",
      "risk_flags": [
        "valuation",
        "volatility",
        "analyst downgrade"
      ]
    }
  ]
}


## System Architecture

MarketMind Agent follows a modular AI pipeline:

User Input (Query + Ticker)
        │
        ▼
FastAPI Endpoint (/briefing)
        │
        ▼
Request Validation (Pydantic)
        │
        ▼
News Service
(fetch + filter + rank articles)
        │
        ├──────────► Sentiment Service
        │            (positive / neutral / negative)
        │
        ├──────────► Risk Service
        │            (detects market risks)
        │
        └──────────► Headline Analysis
                     (per-headline reasoning)
        │
        ▼
LLM Service
(generate analyst-style briefing)
        │
        ├──────────► Fallback Logic
        │            (used if LLM fails or quota is unavailable)
        │
        ▼
Structured Market Output


## Project Structure
marketmind-agent/
├── app/
│   ├── main.py
│   ├── models/
│   │   └── schemas.py
│   ├── routes/
│   │   └── briefing.py
│   └── services/
│       ├── news_service.py
│       ├── sentiment_service.py
│       ├── risk_service.py
│       └── llm_service.py
├── data/
│   └── sample_news.json
├── tests/
├── README.md
├── requirements.txt
└── .gitignore

## API Endpoint
POST /briefing

Generates a structured market briefing for a company.

**Request Body**
{
  "query": "Nvidia",
  "ticker": "NVDA"
}

**Response Fields**
query: company name
ticker: stock ticker if provided
headlines: selected live headlines
sentiment: positive / neutral / negative
outlook: bullish / neutral / cautious
key_drivers: top market signals
risk_flags: detected risk categories
confidence: low / medium / high
summary: analyst-style summary
headline_analysis: per-headline sentiment and risk reasoning

**How It Works**
1. The user submits a company name and optional ticker.
2. The news service fetches recent live articles.
3. Articles are filtered for relevance and ranked by market value.
4. Sentiment service scores the overall tone.
5. Risk service extracts market and business risks.
6. Headline analysis explains each article individually.
7. The LLM service generates a structured briefing.
8. If the LLM fails, fallback logic still returns a useful response.

## Screenshots

### API Documentation
![Docs](screenshots/docs-home.png)

### Tesla Request
![Tesla Request](screenshots/tesla-response.png)

### Tesla Response
![Tesla Response](screenshots/tesla-request.png)

![Tesla Response](screenshots/tesla-request1.png)

### Nvidia Response
![Nvidia Response](screenshots/Nvidia-response.png)

![Nvidia Response](screenshots/Nvidia-response1.png)

## Tech Stack
- Python
- FastAPI
- Pydantic
- Requests
- NewsAPI
- OpenAI API
- Uvicorn
- python-dotenv

## Reliability Design
One of the most important engineering choices in this project is that it does not depend entirely on the LLM.

If the LLM is unavailable because of quota, billing, rate limits, or API failure, the system still returns:

- sentiment
- outlook
- risk flags
- key drivers
- summary
- headline analysis

This makes the API more resilient and closer to real-world production expectations.

## Current Limitations

MarketMind Agent works best for large, well-covered public companies with enough recent news coverage.

It is currently less reliable for:

- obscure or thinly covered tickers
- ambiguous company names
- very noisy media cycles
- highly speculative or rumor-heavy stories

This is a portfolio prototype focused on decision-support AI design, not institutional-grade financial advice.

## Future Improvements
- Better source-level credibility scoring
- Stronger ticker-aware filtering
- More advanced phrase-level sentiment detection
- Finance-specific NLP models such as FinBERT
- Multi-company comparison endpoint
- Dashboard frontend
- Dockerized deployment
- Expanded unit and integration tests

**How to Run Locally**
1. Clone the repository
git clone https://github.com/yourusername/marketmind-agent.git
cd marketmind-agent

2. Create and activate a virtual environment
Windows
python -m venv venv
venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Configure environment variables

Create a .env file in the project root:

NEWS_API_KEY=your_news_api_key
OPENAI_API_KEY=your_openai_api_key

5. Run the API
uvicorn app.main:app --reload

6. Open Swagger Docs
http://127.0.0.1:8000/docs

**Example Use Cases**
- Quickly assess whether current news on a company is bullish, neutral, or cautious
- Surface hidden market risks from noisy headlines
- Support recruiter-facing demos of Applied AI system design
- Show how AI can move from prediction into decision-support workflows

## Why This Project Matters

MarketMind Agent is not just a news summarizer.

It demonstrates how Applied AI systems can combine:

- live data ingestion
- ranking and filtering
- rule-based intelligence
- explainable signal extraction
- LLM-assisted summarization
- fallback reliability

This reflects the direction of modern AI systems:
moving from raw prediction toward structured decision support.

**Author**

Martin Chinedu Oguejiofor
Applied AI | Data Science | Machine Learning