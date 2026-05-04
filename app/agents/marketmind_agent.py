from typing import TypedDict, List, Dict, Optional, Any
from langgraph.graph import StateGraph, END

from app.services.news_service import get_news
from app.services.sentiment_service import analyze_sentiment
from app.services.risk_service import extract_risks, analyze_headlines, determine_outlook
from app.services.llm_service import generate_briefing


class MarketMindState(TypedDict, total=False):
    query: str
    ticker: Optional[str]

    news_items: List[Dict[str, Any]]
    headlines: List[str]
    source_names: List[str]
    article_scores: List[int]

    sentiment: str
    risks: List[str]
    headline_analysis: List[Dict[str, Any]]

    fallback_outlook: str
    briefing: Dict[str, Any]

    agent_steps: List[str]


def add_step(state: MarketMindState, step: str) -> List[str]:
    return state.get("agent_steps", []) + [step]


def fetch_news_node(state: MarketMindState) -> MarketMindState:
    news_items = get_news(
        query=state["query"],
        ticker=state.get("ticker"),
    )

    headlines = [item.get("title", "") for item in news_items if item.get("title")]
    source_names = [item.get("source", "unknown") for item in news_items]
    article_scores = [int(item.get("score", 0)) for item in news_items]

    return {
        "news_items": news_items,
        "headlines": headlines,
        "source_names": source_names,
        "article_scores": article_scores,
        "agent_steps": add_step(
            state,
            "Router selected fetch_news → fetched and ranked relevant market news",
        ),
    }


def sentiment_node(state: MarketMindState) -> MarketMindState:
    sentiment = analyze_sentiment(state["news_items"])

    return {
        "sentiment": sentiment,
        "agent_steps": add_step(
            state,
            "Router selected sentiment → analysed sentiment across market headlines",
        ),
    }


def risk_node(state: MarketMindState) -> MarketMindState:
    risks = extract_risks(state["news_items"])
    headline_analysis = analyze_headlines(state["news_items"])

    return {
        "risks": risks,
        "headline_analysis": headline_analysis,
        "agent_steps": add_step(
            state,
            "Router selected risk → extracted risk flags and per-headline signals",
        ),
    }


def outlook_node(state: MarketMindState) -> MarketMindState:
    fallback_outlook = determine_outlook(
        sentiment=state["sentiment"],
        risks=state["risks"],
    )

    return {
        "fallback_outlook": fallback_outlook,
        "agent_steps": add_step(
            state,
            "Router selected outlook → calculated fallback market outlook",
        ),
    }


def analyst_node(state: MarketMindState) -> MarketMindState:
    query_label = state["query"]
    ticker = state.get("ticker")

    if ticker:
        query_label = f"{query_label} ({ticker})"

    briefing = generate_briefing(
        query=query_label,
        sentiment=state["sentiment"],
        risks=state["risks"],
        headlines=state["headlines"],
        fallback_outlook=state["fallback_outlook"],
    )

    return {
        "briefing": briefing,
        "agent_steps": add_step(
            state,
            "Router selected analyst → generated final analyst-style briefing",
        ),
    }


def tool_selector_node(state: MarketMindState) -> str:
    if "sentiment" not in state:
        return "sentiment"

    if "risks" not in state:
        return "risk"

    if "fallback_outlook" not in state:
        return "outlook"

    return "analyst"


builder = StateGraph(MarketMindState)

builder.add_node("fetch_news", fetch_news_node)
builder.add_node("sentiment", sentiment_node)
builder.add_node("risk", risk_node)
builder.add_node("outlook", outlook_node)
builder.add_node("analyst", analyst_node)

builder.set_entry_point("fetch_news")

builder.add_conditional_edges(
    "fetch_news",
    tool_selector_node,
    {
        "sentiment": "sentiment",
    },
)

builder.add_conditional_edges(
    "sentiment",
    tool_selector_node,
    {
        "risk": "risk",
    },
)

builder.add_conditional_edges(
    "risk",
    tool_selector_node,
    {
        "outlook": "outlook",
    },
)

builder.add_conditional_edges(
    "outlook",
    tool_selector_node,
    {
        "analyst": "analyst",
    },
)

builder.add_edge("analyst", END)

marketmind_graph = builder.compile()


def run_marketmind_agent(query: str, ticker: Optional[str] = None) -> MarketMindState:
    initial_state: MarketMindState = {
        "query": query,
        "ticker": ticker,
        "agent_steps": ["Started MarketMind LangGraph router agent"],
    }

    return marketmind_graph.invoke(initial_state)