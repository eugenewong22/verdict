"""Bright Data — live web search via the `brightdata-sdk` (BrightDataClient).
Falls back to the fixture's cached evidence corpus. `pip install brightdata-sdk`,
auth via BRIGHTDATA_API_TOKEN."""
from urllib.parse import urlparse

from .. import config


async def search(query: str, fixture: dict | None = None, limit: int = 5) -> dict:
    """Return {items: [...], observation: str, source: 'live'|'mock'}."""
    if config.LIVE["brightdata"]:
        try:
            return await _live(query, limit)
        except Exception as e:
            return _mock(fixture, note=f"live failed: {type(e).__name__}")
    return _mock(fixture)


async def _live(query: str, limit: int) -> dict:
    import os

    from brightdata import BrightDataClient  # lazy; only needed when live

    # auto_create_zones=False: the account may lack permission to create zones
    # (Bright Data requires a payment method for that). Point at an existing SERP
    # zone via BRIGHTDATA_SERP_ZONE; default 'sdk_serp'.
    zone = os.environ.get("BRIGHTDATA_SERP_ZONE", "sdk_serp")
    async with BrightDataClient(auto_create_zones=False, serp_zone=zone) as client:
        res = await client.search.google(query=query, num_results=limit)

    if not getattr(res, "success", False):  # e.g. zone not found -> fall back to mock
        raise RuntimeError(getattr(res, "error", None) or "search failed")

    data = getattr(res, "data", None)
    rows = (data.get("organic") or data.get("results") or []) if isinstance(data, dict) else (data or [])
    items = []
    for r in rows[:limit]:
        title = (r.get("title") or r.get("name") or "").strip()
        link = r.get("link") or r.get("url") or ""
        if not title:
            continue
        items.append({"source": "Bright Data · " + (urlparse(link).netloc or "web"),
                      "title": title, "url": link, "sentiment": "neutral"})
    obs = "; ".join(i["title"] for i in items[:3]) or "no results"
    return {"items": items, "observation": obs, "source": "live"}


def _mock(fixture: dict | None, note: str = "") -> dict:
    items = (fixture or {}).get("evidence", [])[:5]
    obs = "; ".join(i.get("title", "") for i in items[:3]) or "no cached evidence"
    return {"items": items, "observation": obs, "source": "mock", "note": note}
