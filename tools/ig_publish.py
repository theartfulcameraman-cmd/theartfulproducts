"""Instagram publisher for The Artful Products (free: Instagram Graph API + GitHub Actions).

Reads social/queue.json, publishes every post whose time has come and that isn't in
social/posted.json yet, then records it there (with its Instagram link).

  python tools/ig_publish.py --check      validate the queue and media files (no network, no token)
  python tools/ig_publish.py --dry-run    show what would be published now (no posting)
  python tools/ig_publish.py              publish due posts (needs IG_PAGE_TOKEN; run by GitHub Actions)

Environment:
  IG_PAGE_TOKEN   long-lived Facebook Page access token (Page linked to the Instagram professional account)
  IG_USER_ID      optional; otherwise looked up from the Page
  IG_API          optional API base (default https://graph.facebook.com/v21.0; tests point it at a fake server)
  SITE_URL        optional (default https://theartfulproducts.com)
"""
import json, os, sys, time, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = Path(os.environ.get("IG_QUEUE", ROOT / "social" / "queue.json"))       # overridable for tests
POSTED = Path(os.environ.get("IG_POSTED", ROOT / "social" / "posted.json"))
SITE_DIR = Path(os.environ.get("IG_SITE_DIR", ROOT / "site"))
SITE_URL = os.environ.get("SITE_URL", "https://theartfulproducts.com").rstrip("/")
API = os.environ.get("IG_API", "https://graph.facebook.com/v21.0").rstrip("/")
IST = timezone(timedelta(hours=5, minutes=30))
MAX_PER_RUN = 5          # Instagram allows 50/day; keep each run small
MAX_FAILURES = 3         # after this many failed tries a post is skipped until fixed

IMG_EXT = {".jpg", ".jpeg"}
VID_EXT = {".mp4", ".mov"}


def log(*a):
    print(*a, flush=True)


def load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def parse_time(s):
    """'2026-11-25 18:30' (India time) or full ISO with offset."""
    s = str(s).strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=IST)
        except ValueError:
            pass
    return datetime.fromisoformat(s)


# ---------------------------------------------------------------- validation
def validate(post):
    """Return a list of problems (empty = OK). Checks Instagram's limits before anything is sent."""
    errs = []
    pid = post.get("id")
    if not pid or not str(pid).replace("-", "").replace("_", "").isalnum():
        errs.append("needs an 'id' (letters, numbers, - or _)")
    t = post.get("type")
    if t not in ("image", "carousel", "reel"):
        errs.append("type must be image, carousel or reel")
    try:
        parse_time(post.get("publish_at", ""))
    except Exception:
        errs.append("publish_at must look like 2026-11-25 18:30 (India time)")
    cap = post.get("caption", "")
    if len(cap) > 2200:
        errs.append(f"caption is {len(cap)} characters (max 2200)")
    if cap.count("#") > 30:
        errs.append("more than 30 hashtags")
    media = post.get("media") or []
    if isinstance(media, str):
        media = [media]
    n = len(media)
    if t == "image" and n != 1: errs.append("an image post needs exactly 1 file")
    if t == "reel" and n != 1: errs.append("a reel needs exactly 1 video")
    if t == "carousel" and not 2 <= n <= 10: errs.append("a carousel needs 2 to 10 files")
    for m in media:
        f = SITE_DIR / m
        ext = f.suffix.lower()
        if not str(m).startswith("social/"):
            errs.append(f"{m}: media must be inside site/social/")
        elif not f.exists():
            errs.append(f"{m}: file not found in site/")
        elif t == "reel" and ext not in VID_EXT:
            errs.append(f"{m}: a reel must be .mp4 or .mov")
        elif t == "image" and ext not in IMG_EXT:
            errs.append(f"{m}: Instagram images must be JPEG (.jpg)")
        elif t == "carousel" and ext not in IMG_EXT | VID_EXT:
            errs.append(f"{m}: carousel items must be .jpg or .mp4")
        elif ext in IMG_EXT:
            if f.stat().st_size > 8 * 1024 * 1024:
                errs.append(f"{m}: image larger than 8 MB")
            try:
                from PIL import Image
                w, h = Image.open(f).size
                r = w / h
                if not (0.8 - 0.01 <= r <= 1.91 + 0.01):
                    errs.append(f"{m}: aspect ratio {w}x{h} outside Instagram's 4:5 to 1.91:1")
            except ImportError:
                pass
    return errs


# ---------------------------------------------------------------- Graph API
def api(method, path, params=None, timeout=60):
    params = dict(params or {})
    params["access_token"] = os.environ["IG_PAGE_TOKEN"]
    url = f"{API}/{path.lstrip('/')}"
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            msg = json.loads(body).get("error", {}).get("message", body)
        except Exception:
            msg = body
        raise RuntimeError(f"Instagram API {e.code}: {msg[:300]}") from None


def ig_user_id():
    if os.environ.get("IG_USER_ID"):
        return os.environ["IG_USER_ID"]
    me = api("GET", "me", {"fields": "instagram_business_account,name"})
    acct = (me.get("instagram_business_account") or {}).get("id")
    if not acct:
        raise RuntimeError("This Facebook Page has no linked Instagram professional account")
    return acct


def wait_ready(container_id, max_wait=600):
    """Videos are processed by Instagram before they can be published."""
    waited = 0
    while True:
        st = api("GET", container_id, {"fields": "status_code,status"})
        code = st.get("status_code")
        if code in (None, "FINISHED", "PUBLISHED"):
            return
        if code in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram couldn't process the media: {st.get('status', code)}")
        if waited >= max_wait:
            raise RuntimeError("Instagram is still processing the video; will retry next run")
        time.sleep(10); waited += 10


def url_ok(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30) as r:
            return r.status == 200
    except Exception:
        return False


def publish(post, ig_id):
    media = post["media"] if isinstance(post["media"], list) else [post["media"]]
    urls = [f"{SITE_URL}/{m}" for m in media]
    for u in urls:
        if not url_ok(u):
            raise RuntimeError(f"media not live on the website yet: {u}")
    caption = post.get("caption", "")
    t = post["type"]
    if t == "image":
        c = api("POST", f"{ig_id}/media", {"image_url": urls[0], "caption": caption})["id"]
    elif t == "reel":
        params = {"media_type": "REELS", "video_url": urls[0], "caption": caption, "share_to_feed": "true"}
        if post.get("cover_at_ms") is not None:
            params["thumb_offset"] = str(int(post["cover_at_ms"]))
        c = api("POST", f"{ig_id}/media", params)["id"]
    else:
        children = []
        for u in urls:
            if Path(u).suffix.lower() in VID_EXT:
                cid = api("POST", f"{ig_id}/media", {"media_type": "VIDEO", "video_url": u, "is_carousel_item": "true"})["id"]
            else:
                cid = api("POST", f"{ig_id}/media", {"image_url": u, "is_carousel_item": "true"})["id"]
            wait_ready(cid)
            children.append(cid)
        c = api("POST", f"{ig_id}/media", {"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption})["id"]
    wait_ready(c)
    media_id = api("POST", f"{ig_id}/media_publish", {"creation_id": c})["id"]
    link = ""
    try:
        link = api("GET", media_id, {"fields": "permalink"}).get("permalink", "")
    except Exception:
        pass
    return media_id, link


# ---------------------------------------------------------------- main
def main():
    check = "--check" in sys.argv
    dry = "--dry-run" in sys.argv
    q = load(QUEUE, {"posts": []})
    posts = q.get("posts", [])
    posted = load(POSTED, {})
    now = datetime.now(IST)

    ids = [p.get("id") for p in posts]
    dupes = {i for i in ids if ids.count(i) > 1}
    bad = 0
    for p in posts:
        errs = validate(p) + ([f"duplicate id {p.get('id')}"] if p.get("id") in dupes else [])
        if errs:
            bad += 1
            log(f"PROBLEM {p.get('id', '?')}: " + "; ".join(errs))
    if check:
        upcoming = [p for p in posts if p.get("id") not in posted or posted[p["id"]].get("status") != "published"]
        log(f"{len(posts)} posts in queue, {len(upcoming)} not yet published, {bad} with problems")
        for p in sorted(upcoming, key=lambda p: str(p.get("publish_at"))):
            log(f"  {p.get('publish_at')}  {p.get('type'):8}  {p.get('id')}{'  (on hold)' if p.get('hold') else ''}")
        return 1 if bad else 0

    due = []
    for p in posts:
        rec = posted.get(p.get("id"), {})
        if rec.get("status") == "published" or p.get("hold") or validate(p):
            continue
        if rec.get("failures", 0) >= MAX_FAILURES:
            continue
        if parse_time(p["publish_at"]) <= now:
            due.append(p)
    due.sort(key=lambda p: parse_time(p["publish_at"]))
    if not due:
        log("Nothing due.")
        return 0
    if dry:
        for p in due[:MAX_PER_RUN]:
            log(f"WOULD PUBLISH {p['id']} ({p['type']}, due {p['publish_at']})")
        return 0
    if not os.environ.get("IG_PAGE_TOKEN"):
        log("::warning::IG_PAGE_TOKEN is not set - nothing published. See social/README.md.")
        return 0

    ig_id = ig_user_id()
    changed = False
    for p in due[:MAX_PER_RUN]:
        rec = posted.setdefault(p["id"], {})
        try:
            media_id, link = publish(p, ig_id)
            posted[p["id"]] = {"status": "published", "media_id": media_id, "permalink": link,
                               "published_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M"), "type": p["type"]}
            log(f"PUBLISHED {p['id']} -> {link or media_id}")
        except Exception as e:
            rec["failures"] = rec.get("failures", 0) + 1
            rec["last_error"] = str(e)[:400]
            rec["status"] = "failed" if rec["failures"] >= MAX_FAILURES else "retrying"
            log(f"::error::{p['id']} failed ({rec['failures']}/{MAX_FAILURES}): {e}")
        changed = True
    if changed:
        POSTED.write_text(json.dumps(posted, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
