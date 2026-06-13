"""The spine. A deterministic stage-runner: each stage gets a timeout and, on
failure, DEGRADES to its cached fixture instead of killing the run. A global
deadline short-circuits to Notary so the signature beat always fires.

`run_pipeline` is an async generator of event dicts — consumed by the SSE server
and the CLI alike."""
import asyncio
import json
import os

from .agents import analyst, notary, producer, quant, scout
from .events import ev
from .schemas import STAGES, Envelope
from . import config, research

AGENTS = {"scout": scout, "analyst": analyst, "quant": quant, "producer": producer, "notary": notary}

GLOBAL_DEADLINE_S = float(os.environ.get("VERDICT_DEADLINE", "100"))
STAGE_TIMEOUT_S = float(os.environ.get("VERDICT_STAGE_TIMEOUT", "20"))

_FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def companies() -> list[str]:
    return sorted(f[:-5] for f in os.listdir(_FIXTURES) if f.endswith(".json"))


def load_fixture(company: str) -> dict:
    with open(os.path.join(_FIXTURES, f"{company}.json")) as f:
        return json.load(f)


async def run_pipeline(company: str):
    q: asyncio.Queue = asyncio.Queue()

    async def emit(e: dict):
        await q.put(e)

    async def driver():
        loop = asyncio.get_event_loop()
        t0 = loop.time()
        await emit(ev("run_started", company=company, live=config.live_map()))

        # Resolve the company: a pre-staged fixture, or a dynamic dossier built live.
        key = company.strip().lower()
        known = set(companies())
        if key in known:
            slug, fixture = key, load_fixture(key)
        elif research.slugify(company) in known:
            slug = research.slugify(company)
            fixture = load_fixture(slug)
        else:
            slug = research.slugify(company)
            await emit(ev("resolving", company=company))
            fixture = await research.build_fixture(company)
        await emit(ev("resolved", company=company, name=fixture.get("name", company),
                      ticker=fixture.get("ticker", ""), sector=fixture.get("sector", ""),
                      indexed=bool(os.environ.get(f"VIDEODB_ID_{slug.upper()}")),
                      source=fixture.get("_source", "fixture")))

        ctx: dict = {}
        for name, label in STAGES:
            if loop.time() - t0 > GLOBAL_DEADLINE_S and name != "notary":
                await emit(ev("stage_skipped", stage=name, label=label, reason="global deadline"))
                continue

            await emit(ev("stage_started", stage=name, label=label))
            s0 = loop.time()
            try:
                env: Envelope = await asyncio.wait_for(
                    AGENTS[name].run(slug, fixture, ctx, emit), STAGE_TIMEOUT_S
                )
            except Exception as ex:  # timeout or agent error -> degrade to cache
                env = Envelope(data=fixture.get(name, {}), status="degraded", source="cache",
                               notes=f"{type(ex).__name__}: {ex}")
            env.latency_ms = int((loop.time() - s0) * 1000)
            if isinstance(env.data, dict):
                ctx.update(env.data)
            await emit(ev("stage_completed", stage=name, label=label, **env.summary()))

        await emit(ev("run_completed", company=company, name=fixture.get("name", company),
                      verdict=ctx.get("thesis", {}).get("recommendation"),
                      upside=ctx.get("valuation", {}).get("upside"),
                      destination=ctx.get("destination")))
        await q.put(None)

    task = asyncio.create_task(driver())
    try:
        while True:
            e = await q.get()
            if e is None:
                break
            yield e
    finally:
        await task
