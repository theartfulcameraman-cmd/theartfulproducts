"""Tests tools/ig_publish.py against a FAKE Instagram API and a local web server (never the real account).
Run: python tools/test_ig_publish.py"""
import json, os, subprocess, sys, tempfile, threading, http.server, socketserver, urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IST = timezone(timedelta(hours=5, minutes=30))
ok = fail = 0
def check(name, cond, extra=""):
    global ok, fail
    if cond: ok += 1; print("  PASS", name)
    else: fail += 1; print("  FAIL", name, extra)

tmp = Path(tempfile.mkdtemp())
site = tmp / "site"; (site / "social").mkdir(parents=True)
Image.new("RGB", (1080, 1350), "orange").save(site / "social/post1.jpg")            # 4:5 ok
Image.new("RGB", (1080, 1080), "black").save(site / "social/c1.jpg")
(site / "social/c2.mp4").write_bytes(b"fake-video")
(site / "social/reel.mp4").write_bytes(b"fake-video")
Image.new("RGB", (500, 1500), "red").save(site / "social/tall.jpg")                # 1:3 too tall
Image.new("RGB", (1080, 1080), "blue").save(site / "social/offline.jpg")           # exists locally, "not uploaded" on the web

calls = []
class FakeIG(http.server.BaseHTTPRequestHandler):
    status_polls = {}
    def log_message(self, *a): pass
    def _send(self, code, obj):
        b = json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = dict(urllib.parse.parse_qsl(u.query)); calls.append(("GET", u.path, q))
        if q.get("access_token") != "TEST": return self._send(400, {"error": {"message": "Invalid OAuth access token"}})
        if u.path.endswith("/me"): return self._send(200, {"name": "The Artful Products", "instagram_business_account": {"id": "IG123"}})
        if q.get("fields", "").startswith("status_code"):
            n = FakeIG.status_polls.get(u.path, 0); FakeIG.status_polls[u.path] = n + 1
            return self._send(200, {"status_code": "FINISHED" if n >= 1 or "IMG" in u.path else "IN_PROGRESS"})
        if q.get("fields") == "permalink": return self._send(200, {"permalink": "https://www.instagram.com/p/" + u.path.split("/")[-1]})
        self._send(404, {"error": {"message": "unknown"}})
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0)); q = dict(urllib.parse.parse_qsl(self.rfile.read(n).decode()))
        u = urllib.parse.urlparse(self.path); calls.append(("POST", u.path, q))
        if q.get("access_token") != "TEST": return self._send(400, {"error": {"message": "Invalid OAuth access token"}})
        if u.path.endswith("/media_publish"): return self._send(200, {"id": "PUB_" + q["creation_id"]})
        if u.path.endswith("/media"):
            kind = "VID" if q.get("media_type") in ("VIDEO", "REELS") else "CAR" if q.get("media_type") == "CAROUSEL" else "IMG"
            return self._send(200, {"id": f"{kind}{len(calls)}"})
        self._send(404, {"error": {"message": "unknown"}})

class Site(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=str(site), **k)
    def log_message(self, *a): pass
    def do_HEAD(self):
        if "offline" in self.path: self.send_response(404); self.end_headers(); return
        super().do_HEAD()

def serve(handler):
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler); srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv
api, web = serve(FakeIG), serve(Site)

now = datetime.now(IST)
fmt = lambda d: d.strftime("%Y-%m-%d %H:%M")
queue = {"posts": [
    {"id": "img-1", "type": "image", "publish_at": fmt(now - timedelta(minutes=5)), "media": ["social/post1.jpg"], "caption": "Terrain frames #3dprinting"},
    {"id": "car-1", "type": "carousel", "publish_at": fmt(now - timedelta(minutes=3)), "media": ["social/c1.jpg", "social/c2.mp4"], "caption": "Swipe →"},
    {"id": "reel-1", "type": "reel", "publish_at": fmt(now - timedelta(minutes=1)), "media": ["social/reel.mp4"], "caption": "Light on the podium", "cover_at_ms": 4000},
    {"id": "future-1", "type": "image", "publish_at": fmt(now + timedelta(days=1)), "media": ["social/post1.jpg"], "caption": "tomorrow"},
    {"id": "held-1", "type": "image", "publish_at": fmt(now - timedelta(hours=1)), "media": ["social/post1.jpg"], "caption": "on hold", "hold": True},
    {"id": "offline-1", "type": "image", "publish_at": fmt(now - timedelta(minutes=9)), "media": ["social/offline.jpg"], "caption": "not uploaded yet"},
]}
bad_queue = {"posts": [
    {"id": "tall", "type": "image", "publish_at": fmt(now), "media": ["social/tall.jpg"]},
    {"id": "missing", "type": "image", "publish_at": fmt(now), "media": ["social/nope.jpg"]},
    {"id": "car-small", "type": "carousel", "publish_at": fmt(now), "media": ["social/c1.jpg"]},
    {"id": "reel-img", "type": "reel", "publish_at": fmt(now), "media": ["social/post1.jpg"]},
    {"id": "badtime", "type": "image", "publish_at": "next tuesday", "media": ["social/post1.jpg"]},
    {"id": "tags", "type": "image", "publish_at": fmt(now), "media": ["social/post1.jpg"], "caption": "#a " * 31},
]}
qf, pf = tmp / "queue.json", tmp / "posted.json"
def run(*args, token="TEST", queue_obj=None):
    if queue_obj is not None: qf.write_text(json.dumps(queue_obj), encoding="utf-8")
    env = dict(os.environ, IG_QUEUE=str(qf), IG_POSTED=str(pf), IG_SITE_DIR=str(site),
               IG_API=f"http://127.0.0.1:{api.server_address[1]}", SITE_URL=f"http://127.0.0.1:{web.server_address[1]}", PYTHONIOENCODING="utf-8")
    env.pop("IG_USER_ID", None)
    if token: env["IG_PAGE_TOKEN"] = token
    else: env.pop("IG_PAGE_TOKEN", None)
    r = subprocess.run([sys.executable, str(ROOT / "tools/ig_publish.py"), *args], env=env, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr
posted = lambda: json.loads(pf.read_text(encoding="utf-8")) if pf.exists() else {}

print("\n1. Queue checks catch problems before anything is sent")
code, out = run("--check", queue_obj=bad_queue)
check("check fails on a bad queue", code == 1, out)
for needle in ["outside Instagram's 4:5", "file not found", "2 to 10 files", "reel must be .mp4", "publish_at must look like", "more than 30 hashtags"]:
    check(f"flags: {needle}", needle in out, out)
code, out = run("--check", queue_obj=queue)
check("good queue passes check", code == 0, out)

print("\n2. Without a token nothing is posted")
code, out = run(token=None, queue_obj=queue)
check("no token -> warning, nothing published", "IG_PAGE_TOKEN is not set" in out and not posted(), out)
code, out = run("--dry-run")
check("dry run lists due posts only", "WOULD PUBLISH img-1" in out and "future-1" not in out and "held-1" not in out, out)
check("dry run makes no API calls", not calls)

print("\n3. Publishing")
code, out = run()
p = posted()
check("image published", p.get("img-1", {}).get("status") == "published", out)
check("carousel published", p.get("car-1", {}).get("status") == "published", out)
check("reel published", p.get("reel-1", {}).get("status") == "published", out)
check("permalink recorded", p.get("img-1", {}).get("permalink", "").startswith("https://www.instagram.com/p/"))
check("future post not published", "future-1" not in p)
check("held post not published", "held-1" not in p)
check("media not live yet -> retry later", p.get("offline-1", {}).get("status") == "retrying" and "not live" in p["offline-1"].get("last_error", ""), p.get("offline-1"))
posts = [c for c in calls if c[0] == "POST" and c[1].endswith("/media")]
check("carousel children marked as carousel items", sum(1 for c in posts if c[2].get("is_carousel_item") == "true") == 2)
check("carousel video sent as VIDEO", any(c[2].get("media_type") == "VIDEO" for c in posts))
check("reel sent as REELS with cover frame", any(c[2].get("media_type") == "REELS" and c[2].get("thumb_offset") == "4000" for c in posts))
check("image uses the public website URL", any(c[2].get("image_url", "").endswith("/social/post1.jpg") for c in posts))
check("waited for video processing", any(c[0] == "GET" and c[2].get("fields", "").startswith("status_code") for c in calls))

print("\n4. No double posting, failures stop after 3 tries")
n_before = len([c for c in calls if c[1].endswith("/media_publish")])
code, out = run(); code, out = run()
n_after = len([c for c in calls if c[1].endswith("/media_publish")])
check("re-runs publish nothing twice", n_after == n_before, (n_before, n_after))
check("offline post marked failed after 3 tries", posted()["offline-1"].get("status") == "failed" and posted()["offline-1"]["failures"] == 3, posted().get("offline-1"))
code, out = run()
check("failed post not retried any more", "offline-1" not in out or "failed (4" not in out, out)

print("\n5. Instagram errors are reported clearly")
pf.write_text("{}", encoding="utf-8")
code, out = run(token="WRONG", queue_obj={"posts": [queue["posts"][0]]})
check("bad token error shown", "Invalid OAuth access token" in out, out)

api.shutdown(); web.shutdown()
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
