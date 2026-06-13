"""Scout — PERCEIVE. Bright Data (live web search) + VideoDB (earnings segment).
Streams each evidence item to the war room as it arrives."""
import asyncio

from ..events import ev
from ..schemas import Envelope
from .. import config
from ..integrations import brightdata, videodb


async def run(company, fixture, ctx, emit) -> Envelope:
    if config.LIVE["brightdata"]:
        r = await brightdata.search(f"{fixture['name']} earnings revenue results news", fixture, limit=5)
        evidence, source = r["items"], r["source"]
    else:
        evidence, source = fixture["evidence"], "mock"

    for item in evidence:
        payload = {k: item[k] for k in ("source", "title", "sentiment", "detail") if item.get(k) is not None}
        await emit(ev("evidence", stage="scout", **payload))
        await asyncio.sleep(0.12)

    seg = await videodb.search_earnings(company, "guidance margin outlook", fixture)
    await emit(ev("video_segment", stage="scout", title=seg["title"], transcript=seg["detail"],
                  timestamp=seg.get("timestamp", ""), source=seg["source"]))
    await asyncio.sleep(0.1)

    if seg.get("source") == "live":  # a real indexed video segment counts as live perception
        source = "live"
    return Envelope(data={"evidence": evidence, "earnings_video": seg}, status="ok", source=source,
                    notes=f'{len(evidence)} sources + earnings segment')
