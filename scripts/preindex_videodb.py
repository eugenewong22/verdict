"""Pre-index an earnings-call video in VideoDB so live search is instant at demo
time (indexing takes minutes, so never do it on the hot path).

    VIDEO_DB_API_KEY=... python scripts/preindex_videodb.py <slug> <youtube_or_mp4_url>

Prints the video id — add it to .env as VIDEODB_ID_<SLUG> and the Scout stage will
read the real earnings segment for that company."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    if len(sys.argv) < 3:
        print("usage: preindex_videodb.py <slug> <youtube_or_mp4_url>")
        print("example: preindex_videodb.py sea 'https://www.youtube.com/watch?v=...'")
        return
    slug, url = sys.argv[1], sys.argv[2]
    if not os.environ.get("VIDEO_DB_API_KEY"):
        print("Set VIDEO_DB_API_KEY first (get one free at https://console.videodb.io).")
        return

    import videodb  # noqa: E402

    conn = videodb.connect()  # reads VIDEO_DB_API_KEY
    coll = conn.get_collection()

    print(f"⬆  uploading {url} …")
    video = coll.upload(url=url)
    print(f"   uploaded: {getattr(video, 'name', video.id)}  (id={video.id})")

    print("🧠 indexing spoken words — this can take several minutes …")
    video.index_spoken_words()

    # sanity-check a search so we know it's queryable
    try:
        hits = video.search("guidance outlook margin").get_shots()
        if hits:
            print(f"   ✓ searchable — sample hit @ {int(hits[0].start)}s: {hits[0].text[:80]}…")
    except Exception:
        print("   (indexing may still be finishing; search will work shortly)")

    print(f"\n✅ DONE. Add this to .env:\n   VIDEODB_ID_{slug.upper()}={video.id}\n")


if __name__ == "__main__":
    main()
