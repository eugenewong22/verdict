"""Runtime config. Every sponsor integration is MOCK by default and goes LIVE
only when its key is present in the environment — so the demo always runs."""
import os


def _flag(name: str) -> bool:
    return bool(os.environ.get(name, "").strip())


# Which sponsor integrations are live (real API) vs mock (fixture-backed).
LIVE = {
    "kimi": _flag("MOONSHOT_API_KEY"),
    "tokenrouter": _flag("TOKENROUTER_API_KEY"),
    "brightdata": _flag("BRIGHTDATA_API_TOKEN"),
    "videodb": _flag("VIDEO_DB_API_KEY"),
    "daytona": _flag("DAYTONA_API_KEY"),
    "nosana": _flag("NOSANA_API_KEY"),
    "terminal3": _flag("TERMINAL3_AGENT_KEY"),
}

# Authorized-action destination (the demo climax lands here — offline-safe by default).
GIT_COMMIT = _flag("VERDICT_GIT_COMMIT")
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL", "").strip()

_ROOT = os.path.dirname(os.path.dirname(__file__))
ARTIFACTS_DIR = os.environ.get("VERDICT_ARTIFACTS", os.path.join(_ROOT, "artifacts"))


def live_map() -> dict:
    return dict(LIVE)
