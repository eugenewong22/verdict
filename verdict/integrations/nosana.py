"""Nosana — decentralised GPU. Pre-run only (cold start is minutes), so we attach
the job receipt rather than running live. Fetches a real receipt by job id when
configured (NOSANA_JOB_ID + NOSANA_API_KEY), else the fixture receipt."""
import asyncio
import json
import os
import urllib.request

from .. import config


async def receipt(fixture: dict | None = None) -> dict:
    r = dict((fixture or {}).get("nosana_receipt", {}))
    r.setdefault("job", "embed-evidence-corpus")
    job_id = os.environ.get("NOSANA_JOB_ID")
    if config.LIVE["nosana"] and job_id:
        try:
            return await asyncio.to_thread(_live, job_id, r)
        except Exception:
            pass
    r["source"] = "mock"
    return r


def _live(job_id: str, r: dict) -> dict:
    url = f"https://dashboard.nosana.com/api/jobs/{job_id}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {os.environ['NOSANA_API_KEY']}"})
    with urllib.request.urlopen(req, timeout=6) as resp:
        data = json.loads(resp.read())
    r.update({"tx": data.get("tx") or data.get("ipfsResult") or r.get("tx"), "source": "live"})
    return r
