from typing import TypedDict, List, Dict, Optional, Any
from langgraph.graph import StateGraph, END

from app.services.news_service import get_news
from app.services.sentiment_service import analyze_sentiment
from app.services.risk_service import extract_risks, analyze_headlines, determine_outlook
from app.services.llm_service import generate_briefing


class MultiAgentState(TypedDict, total=False):
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
    agent_roles: Dict[str, str]


def add_step(state: MultiAgentState, step: str) -> List[str]:
    return state.get("agent_steps", []) + [step]


def news_agent(state: MultiAgentState) -> MultiAgentState:
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
            "News Agent → fetched, filtered, scored, and ranked market headlines",
        ),
    }


def risk_agent(state: MultiAgentState) -> MultiAgentState:
    sentiment = analyze_sentiment(state["news_items"])
    risks = extract_risks(state["news_items"])
    headline_analysis = analyze_headlines(state["news_items"])

    fallback_outlook = determine_outlook(
        sentiment=sentiment,
        risks=risks,
    )

    return {
        "sentiment": sentiment,
        "risks": risks,
        "headline_analysis": headline_analysis,
        "fallback_outlook": fallback_outlook,
        "agent_steps": add_step(
            state,
            "Risk Agent → analysed sentiment, extracted risk flags, and calculated fallback outlook",
        ),
    }


def analyst_agent(state: MultiAgentState) -> MultiAgentState:
    query_label = state["query"]

    if state.get("ticker"):
        query_label = f"{query_label} ({state['ticker']})"

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
            "Analyst Agent → generated final decision-oriented market briefing",
        ),
    }


def should_continue_to_risk(state: MultiAgentState) -> str:
    if not state.get("headlines"):
        return "end"
    return "risk_agent"


def should_continue_to_analyst(state: MultiAgentState) -> str:
    if not state.get("sentiment"):
        return "end"
    return "analyst_agent"


builder = StateGraph(MultiAgentState)

builder.add_node("news_agent", news_agent)
builder.add_node("risk_agent", risk_agent)
builder.add_node("analyst_agent", analyst_agent)

builder.set_entry_point("news_agent")

builder.add_conditional_edges(
    "news_agent",
    should_continue_to_risk,
    {
        "risk_agent": "risk_agent",
        "end": END,
    },
)

builder.add_conditional_edges(
    "risk_agent",
    should_continue_to_analyst,
    {
        "analyst_agent": "analyst_agent",
        "end": END,
    },
)

builder.add_edge("analyst_agent", END)

multi_agent_graph = builder.compile()


def run_multi_agent_marketmind(query: str, ticker: Optional[str] = None) -> MultiAgentState:
    initial_state: MultiAgentState = {
        "query": query,
        "ticker": ticker,
        "agent_steps": ["Started MarketMind multi-agent system"],
        "agent_roles": {
            "News Agent": "Fetches, filters, scores, and ranks market news",
            "Risk Agent": "Analyses sentiment, extracts risks, and estimates fallback outlook",
            "Analyst Agent": "Generates final decision-oriented market briefing",
        },
    }

    return multi_agent_graph.invoke(initial_state)