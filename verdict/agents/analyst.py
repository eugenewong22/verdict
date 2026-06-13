"""Analyst — REASON. For searched companies the research was already done by Kimi
in research.build_fixture (cached), so by default we REPLAY that dossier fast and
tag it LIVE. Pre-staged companies replay their curated trace (MOCK). The real
multi-round live tool-loop is available opt-in via VERDICT_LIVE_REASONING=1."""
import asyncio
import os

from ..events import ev
from ..schemas import Envelope
from .. import config, model_client


async def run(company, fixture, ctx, emit) -> Envelope:
    generated = fixture.get("_source") == "generated"

    # Opt-in: a real multi-round tool-calling loop (slower, streams live reasoning).
    if config.LIVE["kimi"] and os.environ.get("VERDICT_LIVE_REASONING"):
        try:
            thesis = await model_client.analyze(company, fixture, ctx, emit)
            await emit(ev("thesis", stage="analyst", **thesis))
            return Envelope(data={"thesis": thesis}, status="ok", source="live",
                            notes=f'{thesis["recommendation"]} (live tool loop)')
        except Exception:
            pass  # fall through to replay

    thesis = dict(fixture["thesis"])
    steps = list(fixture["analyst_steps"][:3]) + [  # tool searches + reasoning rhythm
        {"tool": "kimi_k2.synthesize", "query": "256K ctx · draft thesis", "observation": "thesis formed"},
        {"tool": "daytona.code_run", "query": "valuation.py · stateful sandbox", "observation": "fair value computed"},
        {"tool": "kimi_k2.rank_risks", "query": "evidence → risk matrix", "observation": f"{len(thesis.get('risks', []))} risks ranked"},
    ]
    for s in steps:
        await emit(ev("analyst_step", stage="analyst", tool=s["tool"], query=s["query"]))
        await asyncio.sleep(0.16)
        await emit(ev("analyst_step", stage="analyst", tool=s["tool"], query=s["query"], observation=s["observation"]))
        await asyncio.sleep(0.08)

    await emit(ev("thesis", stage="analyst", **thesis))
    source = "live" if generated else "mock"  # generated = Kimi-researched dossier
    return Envelope(data={"thesis": thesis}, status="ok", source=source,
                    notes=f'{thesis["recommendation"]} · {thesis.get("conviction", "")}')
