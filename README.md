# Verdict

**Autonomous due-diligence that earns a verifiable mandate to act.**

Type a company name and Verdict runs a crew of specialist AI agents: they research the live web and earnings-call videos, reason to an investment thesis, run a valuation in a secure sandbox, generate a memo + deck + model, then **cryptographically sign the verdict and earn a revocable mandate to execute one authorized action** — in about 90 seconds, live on screen in an "analyst war room."

The differentiator: most agents treat identity as a login badge. Verdict makes identity *enforce* execution — a Decentralized ID signs the report, and a mandate gate **denies** an out-of-scope action and **authorizes** the in-scope one.

Built for Agent Forge SG on a unified agentic stack: **Bright Data** (live web), **Kimi K2** (reasoning), **Daytona** (sandboxed compute), **VideoDB** (earnings-video perception), **Terminal 3** (verifiable agent identity + mandate), **Nosana** (decentralised GPU), **TokenRouter** (model routing), and **SenseNova**. Each integration runs live when its key is present and falls back to cached data otherwise, so the demo never breaks.

## Run

```bash
bash run.sh                      # → http://localhost:8000
node notary_sidecar/server.js    # Terminal 3 signing sidecar (optional)
```

Runs fully on mock data with no keys. Copy `.env.example` → `.env` and add keys to take each stage live.
