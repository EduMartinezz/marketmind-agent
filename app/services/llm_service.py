import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_briefing(
    query: str,
    sentiment: str,
    risks: List[str],
    headlines: List[str],
    fallback_outlook: str,
) -> Dict[str, object]:
    risk_count = len(risks)
    fallback_confidence = "low"

    if sentiment == "positive" and risk_count == 0:
        fallback_confidence = "medium"
    elif sentiment in {"positive", "negative"}:
        fallback_confidence = "medium"

    fallback_key_drivers = [
        f"Recent headlines linked to {query}",
        f"Overall sentiment appears {sentiment}",
        f"Detected {risk_count} risk flag(s) in recent coverage",
    ]

    risk_text = ", ".join(risks) if risks else "no major flagged risks"
    headline_text = "\n".join(f"- {headline}" for headline in headlines) if headlines else "- No major headlines available"

    fallback_summary = (
        f"MarketMind analysis for {query}: sentiment is {sentiment}. "
        f"The near-term outlook is {fallback_outlook}. "
        f"Main risks include {risk_text}."
    )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "outlook": fallback_outlook,
            "confidence": fallback_confidence,
            "key_drivers": fallback_key_drivers,
            "summary": fallback_summary,
        }

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            instructions=(
                "You are a financial market analyst. "
                "Return only valid JSON matching the supplied schema."
            ),
            input=f"""
Generate a concise analyst-style market briefing.

Query: {query}
Sentiment: {sentiment}
Risk flags: {risk_text}

Recent headlines:
{headline_text}
""",
            text={
                "format": {
                    "type": "json_schema",
                    "name": "market_briefing",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "outlook": {
                                "type": "string",
                                "enum": ["bullish", "neutral", "cautious"],
                            },
                            "confidence": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                            },
                            "key_drivers": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 3,
                                "maxItems": 3,
                            },
                            "summary": {
                                "type": "string",
                            },
                        },
                        "required": ["outlook", "confidence", "key_drivers", "summary"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                }
            },
        )

        parsed = json.loads(response.output_text)

        return {
            "outlook": parsed.get("outlook", fallback_outlook),
            "confidence": parsed.get("confidence", fallback_confidence),
            "key_drivers": parsed.get("key_drivers", fallback_key_drivers),
            "summary": parsed.get("summary", fallback_summary),
        }

    except Exception as exc:
        print(f"LLM briefing fallback triggered: {exc}")
        return {
            "outlook": fallback_outlook,
            "confidence": fallback_confidence,
            "key_drivers": fallback_key_drivers,
            "summary": fallback_summary,
        }