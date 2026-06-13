# Verdict — autonomous due-diligence agent

**Agent Forge SG · "Build Production AI Systems."** Type a company → a 5-agent crew researches the live web + earnings videos, reasons to a thesis, runs a valuation in a sandbox, generates a signed memo + deck + Excel, and **earns a verifiable mandate to act** — in ~90 seconds, on screen.

The differentiator: most agents treat identity as a login badge. Verdict makes identity *enforce* execution — the report is signed by the agent's Decentralized ID into a Verifiable Credential, and a **mandate gate** denies an out-of-scope action and authorizes the in-scope one. You can watch it get **DENIED, then authorized, live.**

## Run (no API keys needed — runs fully on mock data)

```bash
bash run.sh
# open http://localhost:8000  →  pick a company  →  Run ▸
```

## The spine — all 8 sponsors, mock by default, live when a key is present

```
Scout ──▶ Analyst ──▶ Quant ──▶ Producer ──▶ Notary
Bright Data Kimi K2   Daytona   python-pptx   Terminal 3 (sign + mandate gate)
VideoDB                         /openpyxl     Nosana (pre-run receipt)
            └─ TokenRouter routes every model call (failover) ─┘
```

Every stage shows a **MOCK** / **LIVE** tag in the UI. Breadth (criterion 4) is honest: each stage is load-bearing. To flip a stage to LIVE, copy `.env.example` → `.env`, add the key, restart:

| Env var | Effect when set |
|---|---|
| `MOONSHOT_API_KEY` | Analyst writes the thesis with real **Kimi K2** (`kimi-k2.6` @ `api.moonshot.ai/v1`) |
| `TOKENROUTER_API_KEY` | Model calls route through the **TokenRouter** failover gateway |
| `DAYTONA_API_KEY` | Quant runs the valuation in a real **Daytona** sandbox (`code_run`) |
| `BRIGHTDATA_API_TOKEN` / `VIDEODB_API_KEY` | Real perception hooks |
| `TERMINAL3_AGENT_KEY` | Notary signs via the live **Terminal 3** path (else real local Ed25519) |
| `VERDICT_GIT_COMMIT=1` *or* `SLACK_WEBHOOK_URL` | Where the authorized action lands |

> The signature is **real Ed25519** even in mock mode — `verified ✓` is a genuine cryptographic check, not a fake badge.

## Going live (real integrations)

```bash
pip install -r requirements-live.txt        # brightdata-sdk, videodb, daytona (lazy-imported)
cp .env.example .env                         # add the keys you have
node notary_sidecar/server.js                # Terminal 3 — auto-detected → notary goes LIVE
bash run.sh                                  # restart the app
```

Architecture: agents never branch on liveness — they call the `verdict/integrations/`
layer, which picks the real API (key present) or the cached fixture (mock) behind one
async signature. So each `MOCK`→`LIVE` flip is a one-line env change:

- **Analyst** — searched companies are researched by the model in `build_fixture` (fast `moonshot-v1-32k`, cached) and the dossier is replayed; an optional real-time tool-calling loop (`web_search`/`earnings_search`) is available via `VERDICT_LIVE_REASONING=1`.
- **Quant** runs the valuation in a real Daytona sandbox (`code_run`) or locally.
- **Notary** signs via the Terminal 3 sidecar (`@terminal3/t3n-sdk` hook) or in-process Ed25519; the mandate gate is identical either way.

## Search any company

The search bar researches ANY company, not just the pre-staged three. An unknown name triggers `research.build_fixture()` → the model generates a full dossier (~12s with the fast model, cached to `artifacts/generated/<slug>.json`), then the same pipeline runs over it. Quick-pick companies stay instant. Private companies (e.g. SpaceX, Stripe) are valued off their last private round.

## Pre-index a real earnings video

```bash
VIDEO_DB_API_KEY=... python scripts/preindex_videodb.py sea "<youtube-earnings-call-url>"
# add the printed VIDEODB_ID_SEA=... to .env → Scout reads the real spoken segment
```

Note: `kimi-k2.6` only accepts `temperature=1` and is ~7× slower than `moonshot-v1-32k`; dossier generation uses the fast model (override with `KIMI_FAST_MODEL`). On Python 3.14, set `SSL_CERT_FILE` to certifi's bundle for Daytona (done in `.env`).

## 90-second demo script

1. **Cold open on the payoff.** "A full investment due-diligence memo, written by AI agents in 90 seconds — and it's cryptographically signed." Click the green ✓ badge.
2. **Controlled live choice.** "Judge, pick one: Sea, Grab, or GoTo." → Run ▸ (all three are pre-staged, so it's fast and unfakeable).
3. **Watch the crew (~25s).** Evidence streams in (Bright Data + a VideoDB earnings-call segment); the Analyst's bounded tool-loop reasons step by step; the valuation chart renders from the Daytona model.
4. **THE CLIMAX.** Terminal 3 signs the report → the mandate **DENIES** "Wire $2.4M" → **AUTHORIZES** the signed memo, which lands in a real destination. **Hold 3 seconds.**
5. **Close.** "Verdict doesn't just read the web — it reasons, values, and then *earns the right to act*, with a signature you can take to your board."

## Verify / debug

```bash
.venv/bin/python scripts/run_pipeline.py sea   # full pipeline in the terminal
.venv/bin/python scripts/smoke_all.py          # which sponsors are live vs mock
```

Generated deliverables land in `artifacts/` (`<company>_memo.md`, `_deck.pptx`, `_model.xlsx`, signed `actions.log`).

## Architecture notes (the production story)

- **Degrade-and-continue:** every stage returns a uniform envelope; on timeout/error it falls back to its cached fixture (`status=degraded`) so the run always reaches the Terminal 3 signature. A global ~100s deadline short-circuits to Notary.
- **Honest agentic framing:** one autonomous reasoning agent (Analyst) on a deterministic spine with four specialist tool-stages; the tool loop is bounded (≤4 calls) and every step is shown.
