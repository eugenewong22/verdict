"""FastAPI server: serves the war room and streams the pipeline over SSE."""
import json
import os

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse

from .orchestrator import companies, load_fixture, run_pipeline

app = FastAPI(title="Verdict")
WEB = os.path.join(os.path.dirname(__file__), "web")


@app.get("/")
async def index():
    return FileResponse(os.path.join(WEB, "index.html"))


@app.get("/api/companies")
async def api_companies():
    out = []
    for c in companies():
        fx = load_fixture(c)
        out.append({"id": c, "name": fx["name"], "ticker": fx["ticker"]})
    return out


@app.get("/api/run")
async def api_run(company: str = "sea"):
    async def gen():
        async for e in run_pipeline(company.lower()):
            yield f"data: {json.dumps(e)}\n\n"

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )
