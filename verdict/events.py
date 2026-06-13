"""Tiny event helpers. Events are plain dicts streamed over SSE to the war room
and printed by the CLI."""
import time


def now_ms() -> int:
    return int(time.time() * 1000)


def ev(type_: str, **payload) -> dict:
    payload["type"] = type_
    payload.setdefault("ts", now_ms())
    return payload
