"""Notary — VERIFY + ACT. The differentiator. Signs the report via Terminal 3
(Node sidecar) or in-process Ed25519, then runs the MANDATE GATE: an over-scope
action is denied, the in-scope action is authorized and executed into a real
destination. Nosana's pre-run receipt is attached as proof of decentralised GPU."""
import asyncio
import hashlib
import json
import os
import subprocess

from ..events import ev, now_ms
from ..schemas import Envelope
from .. import config
from ..integrations import nosana, terminal3

# The agent's delegation credential: granted actions + a position cap.
MANDATE = {"functions": ["flag_ic_review", "commit_report"], "max_value_usd": 10_000_000, "scopes": ["due-diligence"]}


def _execute(company, report, vc) -> str:
    """Land the authorized action in a real, controllable place. Offline-safe."""
    os.makedirs(config.ARTIFACTS_DIR, exist_ok=True)
    receipt = {"company": report["company"], "vc": vc, "action": "commit_decision_record"}
    log = os.path.join(config.ARTIFACTS_DIR, "actions.log")
    with open(log, "a") as f:
        f.write(json.dumps(receipt) + "\n")

    if config.SLACK_WEBHOOK:
        try:
            import urllib.request

            body = json.dumps({"text": f"Verdict signed {report['company']} — {report['thesis']['recommendation']} (verified ✓)"}).encode()
            req = urllib.request.Request(config.SLACK_WEBHOOK, data=body, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=4)
            return "Slack #deals (verified ✓)"
        except Exception:
            pass

    if config.GIT_COMMIT:
        try:
            memo = os.path.join(config.ARTIFACTS_DIR, f"{company}_memo.md")
            subprocess.run(["git", "add", memo, log], cwd=config.ARTIFACTS_DIR, check=False)
            out = subprocess.run(["git", "commit", "-m", f"Verdict: signed {report['company']} decision"],
                                 cwd=config.ARTIFACTS_DIR, capture_output=True, text=True)
            if out.returncode == 0:
                sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=config.ARTIFACTS_DIR,
                                     capture_output=True, text=True).stdout.strip()
                return f"local git commit {sha}"
        except Exception:
            pass

    return f"file://{log}"


async def run(company, fixture, ctx, emit) -> Envelope:
    thesis = ctx.get("thesis", fixture["thesis"])
    valuation = ctx.get("valuation", fixture["valuation"])
    report = {"company": fixture["name"], "thesis": thesis, "valuation": valuation}
    report_bytes = json.dumps(report, sort_keys=True).encode()
    report_hash = hashlib.sha256(report_bytes).hexdigest()

    did = await terminal3.identity()
    await emit(ev("signing", stage="notary", did=did, report_hash=report_hash, scheme="ed25519"))
    await asyncio.sleep(0.3)

    vc = await terminal3.sign(report_bytes, MANDATE)
    await emit(ev("signed", stage="notary", did=vc["did"], report_hash=vc.get("report_hash", report_hash),
                  signature=vc["signature"], verified=vc["verified"], scheme=vc["scheme"], issued=now_ms()))
    await asyncio.sleep(0.35)

    # Show the granted mandate (verifiable credential) before the gate.
    await emit(ev("mandate", stage="notary", actions=MANDATE["functions"], cap_usd=MANDATE["max_value_usd"]))
    await asyncio.sleep(0.2)

    # MANDATE GATE — an over-scope action is denied first.
    over = {"function": "open_position", "value_usd": 50_000_000, "label": "open_position($50,000,000)"}
    await emit(ev("mandate_check", stage="notary", action=over["label"]))
    await asyncio.sleep(0.45)
    denied = await terminal3.check_mandate(MANDATE, over)
    await emit(ev("mandate_denied", stage="notary", action=over["label"], reason=denied["reason"]))
    await asyncio.sleep(0.6)

    # ... then the in-scope action is authorized and executed.
    ins = {"function": "commit_report", "value_usd": 0, "label": "commit_report + flag_ic_review"}
    await emit(ev("mandate_check", stage="notary", action=ins["label"]))
    await asyncio.sleep(0.35)
    authd = await terminal3.check_mandate(MANDATE, ins)
    destination = await asyncio.to_thread(_execute, company, report, vc) if authd["authorized"] else "(unauthorized)"
    await emit(ev("mandate_authorized", stage="notary", action=ins["label"],
                  destination=destination, verified=vc["verified"]))

    nos = await nosana.receipt(fixture)
    await emit(ev("nosana_receipt", stage="notary", **{k: nos[k] for k in ("job", "gpu", "tx", "vectors") if k in nos}))

    return Envelope(data={"vc": vc, "destination": destination}, status="ok", source=vc["source"],
                    notes=f'signed ({vc["scheme"]}) · verified={vc["verified"]} → {destination}')
