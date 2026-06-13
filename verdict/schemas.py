"""Frozen stage contract. Every stage returns a uniform Envelope so a stalled
stage can DEGRADE to a cached fixture and the pipeline keeps going to the
Terminal 3 signature — the beat we must never miss."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Status = Literal["ok", "degraded", "failed"]
Source = Literal["live", "cache", "mock"]


@dataclass
class Envelope:
    data: Any = None
    status: Status = "ok"
    source: Source = "mock"
    notes: str = ""
    latency_ms: int = 0
    schema_version: int = 1

    def summary(self) -> dict:
        return {
            "status": self.status,
            "source": self.source,
            "notes": self.notes,
            "latency_ms": self.latency_ms,
        }


# The agentic spine, in order. (key, human label)
STAGES = [
    ("scout", "Perceive"),
    ("analyst", "Reason"),
    ("quant", "Compute"),
    ("producer", "Produce"),
    ("notary", "Verify + act"),
]

SPONSOR_BY_STAGE = {
    "scout": ["Bright Data", "VideoDB"],
    "analyst": ["Kimi K2", "TokenRouter"],
    "quant": ["Daytona"],
    "producer": ["python-pptx / openpyxl", "SenseNova U1*"],
    "notary": ["Terminal 3", "Nosana"],
}
