"""One OpenAI-compatible client. Uses Kimi K2 directly (verified path) or the
TokenRouter gateway as failover. Returns None when no live key is set, so the
Analyst falls back to its pre-staged thesis and the demo still runs."""
import asyncio
import json
import os

from . import config


def _client_and_model():
    from openai import OpenAI  # lazy import — only needed when live

    # Prefer direct Kimi K2 (verified OpenAI-compatible); TokenRouter is the failover.
    if config.LIVE["kimi"]:
        client = OpenAI(base_url="https://api.moonshot.ai/v1", api_key=os.environ["MOONSHOT_API_KEY"])
        return client, os.environ.get("KIMI_MODEL", "kimi-k2.6")

    client = OpenAI(
        base_url=os.environ.get("TOKENROUTER_BASE_URL", "https://api.tokenrouter.io/v1"),
        api_key=os.environ["TOKENROUTER_API_KEY"],
    )
    return client, os.environ.get("TOKENROUTER_MODEL", "auto:balance")


async def reason(prompt: str, system: str = "", model_override: str | None = None) -> str | None:
    """Return model text, or None if no live model is configured. `model_override`
    lets callers pick a faster model (e.g. moonshot-v1-32k) for structured generation."""
    if not (config.LIVE["kimi"] or config.LIVE["tokenrouter"]):
        return None

    def _call():
        client, model = _client_and_model()
        messages = ([{"role": "system", "content": system}] if system else []) + [
            {"role": "user", "content": prompt}
        ]
        resp = client.chat.completions.create(model=model_override or model, messages=messages)
        return resp.choices[0].message.content

    try:
        return await asyncio.to_thread(_call)
    except Exception:
        # Any live failure -> fall back to the pre-staged thesis. Demo must not break.
        return None


# ---- agentic tool-calling loop ---------------------------------------------

_TOOLS = [
    {"type": "function", "function": {
        "name": "web_search",
        "description": "Search the live web (news, filings, analysis) about the company. Returns top headlines.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    }},
    {"type": "function", "function": {
        "name": "earnings_search",
        "description": "Search the company's latest earnings-call video for a topic; returns the spoken segment.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    }},
]


def _extract_json(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
    i, j = text.find("{"), text.rfind("}")
    return text[i:j + 1] if i != -1 and j != -1 else "{}"


async def analyze(company: str, fixture: dict, ctx: dict, emit, max_calls: int = 4) -> dict:
    """Real bounded tool-calling loop: the model researches via web_search /
    earnings_search (Bright Data / VideoDB), then emits a structured verdict.
    Raises on failure so the Analyst can fall back to the pre-staged trace."""
    from .events import ev
    from .integrations import brightdata, videodb

    client, model = _client_and_model()
    messages = [
        {"role": "system", "content": (
            "You are a decisive sell-side equity analyst. Research the company with the "
            "tools (at most ~4 calls total), then issue an investment verdict. Be rigorous.")},
        {"role": "user", "content": (
            f"Company: {fixture['name']} ({fixture['ticker']}). Sector: {fixture['sector']}. "
            "Research recent results, guidance and risks, then recommend BUY, HOLD or SELL.")},
    ]

    calls = 0
    while calls < max_calls:
        resp = await asyncio.to_thread(lambda: client.chat.completions.create(
            model=model, messages=messages, tools=_TOOLS, tool_choice="auto"))
        msg = resp.choices[0].message
        if not getattr(msg, "tool_calls", None):
            break
        messages.append({
            "role": "assistant", "content": msg.content or "",
            "tool_calls": [{"id": tc.id, "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                           for tc in msg.tool_calls],
        })
        for tc in msg.tool_calls:
            calls += 1
            try:
                q = json.loads(tc.function.arguments or "{}").get("query", "")
            except Exception:
                q = ""
            await emit(ev("analyst_step", stage="analyst", tool=tc.function.name, query=q))
            if tc.function.name == "earnings_search":
                r = await videodb.search_earnings(company, q, fixture)
                obs = r.get("detail") or r.get("title", "")
            else:
                r = await brightdata.search(q, fixture)
                obs = r.get("observation", "")
            await emit(ev("analyst_step", stage="analyst", tool=tc.function.name, query=q, observation=obs))
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": obs or "(no result)"})

    messages.append({"role": "user", "content": (
        'Output ONLY JSON: {"recommendation":"BUY|HOLD|SELL","conviction":"Low|Medium|Medium-High|High",'
        '"summary":"one paragraph","risks":["r1","r2","r3"]}')})
    final = await asyncio.to_thread(lambda: client.chat.completions.create(
        model=model, messages=messages))
    thesis = json.loads(_extract_json(final.choices[0].message.content))
    thesis.setdefault("conviction", "Medium")
    thesis.setdefault("risks", [])
    if not thesis.get("recommendation") or not thesis.get("summary"):
        raise ValueError("incomplete thesis from model")
    return thesis
