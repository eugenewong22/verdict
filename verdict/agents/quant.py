"""Quant — COMPUTE. Writes a valuation model and runs it in a Daytona sandbox
(live) or a local sandboxed exec (mock). Real computed output either way."""
import asyncio

from ..events import ev
from ..schemas import Envelope
from ..integrations import daytona


def _valuation_code(val: dict) -> str:
    return (
        "# valuation model (runs in a Daytona sandbox when live)\n"
        f"price = {val['current_price_usd']}\n"
        f"fair_value = {val['fair_value_usd']}\n"
        f"ev_sales = {val['ev_sales_multiple']}\n"
        f"rev_growth = {val['growth']}\n"
        "upside = (fair_value / price - 1) if price else 0\n"
        "print(round(upside, 4))\n"
    )


def _ranges(current: float, fair: float) -> list:
    """A valuation 'football field' — four method ranges around current/fair."""
    rows = [
        ("Current / last round", current * 0.97, current * 1.03, "#586173"),
        ("Trading comps", fair * 0.80, fair * 1.05, "#3b6f8c"),
        ("DCF · base case", fair * 0.85, fair * 1.12, "#2f8f86"),
        ("Sum-of-the-parts", fair * 0.92, fair * 1.22, "#35a85f"),
    ]
    return [{"label": l, "low": round(lo, 2), "high": round(hi, 2), "color": c} for l, lo, hi, c in rows]


def _rev_series(revenue_b: float, growth: float) -> list:
    """5-point back-cast revenue trend ending at the latest revenue."""
    g = growth or 0.2
    return [round((revenue_b or 1) / ((1 + g) ** (4 - i)), 2) for i in range(5)]


async def run(company, fixture, ctx, emit) -> Envelope:
    val = dict(fixture["valuation"])
    code = _valuation_code(val)
    await emit(ev("quant_code", stage="quant", code=code))
    await asyncio.sleep(0.2)

    r = await daytona.run_code(code)
    try:
        upside = float(r["stdout"].strip().splitlines()[-1])
    except Exception:
        price = val["current_price_usd"]
        upside = (val["fair_value_usd"] / price - 1.0) if price else 0.0
    val["upside"] = round(upside, 4)
    ranges = _ranges(val["current_price_usd"], val["fair_value_usd"])
    bounds = [r["low"] for r in ranges] + [r["high"] for r in ranges] + [val["fair_value_usd"]]
    val["ranges"] = ranges
    val["axis_min"] = round(min(bounds) * 0.95, 2)
    val["axis_max"] = round(max(bounds) * 1.05, 2)
    val["rev_series"] = _rev_series(val.get("revenue_b", 0), val.get("growth", 0))
    await emit(ev("valuation", stage="quant", **val))

    return Envelope(data={"valuation": val}, status="ok", source=r["source"],
                    notes=f'fair value ${val["fair_value_usd"]} ({round(upside * 100)}% upside)')
