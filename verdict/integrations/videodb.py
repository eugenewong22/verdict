"""VideoDB — semantic search over an earnings-call video. Falls back to the
fixture's cached segment. `pip install videodb`, auth via VIDEO_DB_API_KEY.

Indexing is slow (minutes), so live mode reuses a PRE-INDEXED video referenced by
id (env VIDEODB_ID_<COMPANY>) rather than uploading on the hot path."""
import asyncio
import os

from .. import config


async def search_earnings(company: str, query: str, fixture: dict | None = None) -> dict:
    """Return {title, detail, source}."""
    if config.LIVE["videodb"]:
        try:
            return await asyncio.to_thread(_live, company, query)
        except Exception as e:
            return _mock(fixture, note=f"live failed: {type(e).__name__}")
    return _mock(fixture)


def _live(company: str, query: str) -> dict:
    import videodb  # lazy

    conn = videodb.connect()  # reads VIDEO_DB_API_KEY
    coll = conn.get_collection()

    vid_id = os.environ.get(f"VIDEODB_ID_{company.upper()}")
    url = os.environ.get(f"VIDEODB_URL_{company.upper()}")
    if vid_id:
        video = coll.get_video(vid_id)  # pre-indexed — fast
    elif url:
        video = coll.upload(url=url)  # slow path; pre-stage instead
        video.index_spoken_words()
    else:
        raise RuntimeError("no VIDEODB_ID/URL configured for company")

    res = video.search(query)
    shots = res.get_shots()
    if not shots:
        raise RuntimeError("no matching segment")
    s = shots[0]
    title = getattr(s, "video_title", None) or "earnings call"
    start = int(getattr(s, "start", 0))
    return {"title": title, "detail": s.text, "source": "live", "timestamp": f"{start // 60:02d}:{start % 60:02d}"}


def _mock(fixture: dict | None, note: str = "") -> dict:
    v = (fixture or {}).get("earnings_video", {})
    return {
        "title": v.get("title", "earnings call"),
        "detail": v.get("quote", ""),
        "source": "mock",
        "timestamp": v.get("timestamp", ""),
        "note": note,
    }
