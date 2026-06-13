"""CLI runner — same async generator the war room consumes over SSE.

    python scripts/run_pipeline.py sea
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verdict.orchestrator import companies, run_pipeline  # noqa: E402


async def main():
    company = (sys.argv[1] if len(sys.argv) > 1 else "sea").lower()
    print(f"▶ Verdict — {company}  (companies: {', '.join(companies())})\n")
    async for e in run_pipeline(company):
        t = e.pop("type")
        e.pop("ts", None)
        detail = json.dumps(e, default=str)
        if len(detail) > 180:
            detail = detail[:177] + "..."
        print(f"  {t:18} {detail}")


if __name__ == "__main__":
    asyncio.run(main())
