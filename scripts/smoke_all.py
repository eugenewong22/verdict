"""Which sponsors are LIVE (key present) vs MOCK. Run before the demo so you
know what's wired. Attempts a real ping for Kimi if its key is set."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verdict import config, model_client  # noqa: E402

LABELS = {
    "kimi": "Kimi K2 (reasoning)",
    "tokenrouter": "TokenRouter (routing)",
    "brightdata": "Bright Data (web)",
    "videodb": "VideoDB (perception)",
    "daytona": "Daytona (sandbox)",
    "nosana": "Nosana (GPU receipt)",
    "terminal3": "Terminal 3 (identity)",
}


async def main():
    print("Sponsor integration status\n" + "-" * 40)
    for key, label in LABELS.items():
        state = "LIVE" if config.LIVE[key] else "mock"
        print(f"  {label:28} {state}")

    if config.LIVE["kimi"] or config.LIVE["tokenrouter"]:
        print("\nPinging the live model…")
        out = await model_client.reason("Reply with exactly: OK", system="You are terse.")
        print("  model reply:", (out or "<no response>").strip()[:60])
    else:
        print("\nNo live model key — Analyst uses the pre-staged thesis (demo still runs).")


if __name__ == "__main__":
    asyncio.run(main())
