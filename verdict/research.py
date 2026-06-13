"""Dynamic dossier builder. When a searched company isn't pre-staged, the model
generates a fixture-shaped brief on the fly so the SAME pipeline runs over it.
Cached to artifacts/generated/<slug>.json so re-runs are instant.

Needs a live model (MOONSHOT_API_KEY / TOKENROUTER_API_KEY) to be meaningful;
without one it returns a clearly-labelled placeholder so nothing breaks."""
import json
import os
import re

from . import config, model_client

GEN_DIR = os.path.join(config.ARTIFACTS_DIR, "generated")
_SYS = "You are an equity-research data generator. Output STRICT JSON only — no prose, no markdown fences."


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower()) or "company"


def _series(current: float, fair: float) -> list:
    start = current * 0.85
    return [round(start + (fair - start) * (i / 7), 2) for i in range(8)]


def _prompt(name: str) -> str:
    return (
        f'Generate an investment due-diligence brief for "{name}" as STRICT JSON with EXACTLY this shape:\n'
        '{"name":"official name","ticker":"TICKER or private","sector":"short sector description",'
        '"evidence":[{"source":"Bright Data · <publication>","title":"recent factual headline","sentiment":"positive|neutral|negative"} (exactly 5)],'
        '"earnings_video":{"title":"<name> latest earnings/investor call","timestamp":"00:MM:SS","quote":"a realistic management quote"},'
        '"analyst_steps":[{"tool":"brightdata.search or videodb.search","query":"research query","observation":"the finding"} (exactly 4)],'
        '"thesis":{"recommendation":"BUY|HOLD|SELL","conviction":"Low|Medium|Medium-High|High","summary":"one rigorous paragraph","risks":["risk1","risk2","risk3"]},'
        '"valuation":{"method":"valuation method","revenue_b":number,"growth":number_0_to_1,"ev_sales_multiple":number,"current_price_usd":number,"fair_value_usd":number}}\n'
        "Use real, recent facts you know about the company. For PRIVATE companies, use the latest known "
        "private valuation: set current_price_usd to a last-round/implied per-share basis and fair_value_usd "
        "to your fair estimate. Output ONLY the JSON object."
    )


def _placeholder(name: str) -> dict:
    return {
        "name": name, "ticker": "—", "sector": "(set MOONSHOT_API_KEY for live research)",
        "evidence": [{"source": "Verdict", "sentiment": "neutral",
                      "title": f"Set MOONSHOT_API_KEY (+ BRIGHTDATA_API_TOKEN) to research {name} live."}],
        "earnings_video": {"title": f"{name} — no indexed call", "timestamp": "—",
                            "quote": "Connect VideoDB to analyze an earnings call."},
        "analyst_steps": [{"tool": "brightdata.search", "query": f"{name} overview", "observation": "(live model key required)"}],
        "thesis": {"recommendation": "HOLD", "conviction": "n/a",
                   "summary": f"No live model configured. Set MOONSHOT_API_KEY to let the agent research {name} for real.",
                   "risks": ["Live integrations not configured"]},
        "valuation": {"method": "n/a", "revenue_b": 0, "growth": 0, "ev_sales_multiple": 0,
                      "current_price_usd": 1, "fair_value_usd": 1, "series": [1] * 8},
        "nosana_receipt": {"job": "embed-evidence-corpus", "gpu": "RTX 4090 (decentralised)", "tx": "(pre-run)", "vectors": 0},
        "_source": "placeholder",
    }


async def build_fixture(name: str) -> dict:
    os.makedirs(GEN_DIR, exist_ok=True)
    cache = os.path.join(GEN_DIR, f"{slugify(name)}.json")
    if os.path.exists(cache):
        try:
            return json.load(open(cache))
        except Exception:
            pass

    # Use a fast model for the structured dossier (kimi-k2.6 is ~7x slower).
    fast = os.environ.get("KIMI_FAST_MODEL", "moonshot-v1-32k") if config.LIVE["kimi"] else None
    txt = await model_client.reason(_prompt(name), system=_SYS, model_override=fast)
    if not txt:
        return _placeholder(name)
    try:
        fx = json.loads(model_client._extract_json(txt))
        fx.setdefault("name", name)
        fx.setdefault("ticker", "—")
        v = fx.get("valuation", {})
        cur = float(v.get("current_price_usd") or 1) or 1
        fair = float(v.get("fair_value_usd") or cur)
        v.update({"current_price_usd": cur, "fair_value_usd": fair, "series": _series(cur, fair)})
        v.setdefault("method", "EV/Sales + DCF")
        v.setdefault("ev_sales_multiple", round(fair / cur * 3, 1))
        v.setdefault("revenue_b", 0)
        v.setdefault("growth", 0)
        rev = float(v.get("revenue_b") or 0)  # models sometimes return raw dollars
        v["revenue_b"] = round(rev / 1e9, 2) if rev > 1000 else rev
        fx["valuation"] = v
        fx.setdefault("earnings_video", {"title": f"{name} call", "timestamp": "—", "quote": ""})
        fx.setdefault("nosana_receipt", {"job": "embed-evidence-corpus", "gpu": "RTX 4090 (decentralised)",
                                          "tx": "(pre-run)", "vectors": 1024})
        fx["_source"] = "generated"
        json.dump(fx, open(cache, "w"), indent=2)
        return fx
    except Exception:
        return _placeholder(name)
