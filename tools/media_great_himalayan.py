"""Web versions of The Great Himalayan (Inspire India, Aug 2026) photos and videos.
Originals: _incoming/himalayan-zip/Artful/ (not in git). Outputs go into site/assets/.
Crops are fractions of the full (rotation-corrected) photo: (left, top, right, bottom).
Run: python tools/media_great_himalayan.py"""
import subprocess
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_incoming/himalayan-zip/Artful"
IMG = ROOT / "site/assets/img"
VID = ROOT / "site/assets/video"

def save(name, crop, out, size, q=82):
    im = ImageOps.exif_transpose(Image.open(SRC / name)).convert("RGB")
    W, H = im.size
    if crop: im = im.crop((round(crop[0] * W), round(crop[1] * H), round(crop[2] * W), round(crop[3] * H)))
    im.thumbnail(size, Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "JPEG", quality=q, optimize=True, progressive=True)
    print(f"{out.relative_to(ROOT)}  {im.size[0]}x{im.size[1]}  {out.stat().st_size // 1024} KB")

# --- Terrain Award Frame product photos (square) ---
P = IMG / "products"
save("VAIL1508.JPG", (0, 290/900, 1, 890/900), P / "terrain-frame-1.jpg", (1200, 1200))          # three frames, angled
save("VAIL1504.JPG", (255/900, 100/600, 755/900, 1), P / "terrain-frame-2.jpg", (1200, 1200))     # three frames, straight on
save("VAIL1508.JPG", (165/600, 585/900, 345/600, 765/900), P / "terrain-frame-3.jpg", (1200, 1200))  # 3D terrain + route close-up
save("VAIL1508.JPG", (195/600, 330/900, 375/600, 510/900), P / "terrain-frame-4.jpg", (1200, 1200))  # medal + race details close-up
save("AD104592.JPG", (0, 280/900, 1, 880/900), P / "terrain-frame-5.jpg", (1200, 1200))           # winner holding the frame

# --- Featured event: The Great Himalayan (3:2) ---
E = IMG / "events/great-himalayan"
save("VAIL1504.JPG", None, E / "podium-frames.jpg", (1600, 1600))
for n in ["AD104601", "AD104655", "AD104671", "AD104680", "AD104695", "AD104699", "AD104619", "AD104594"]:
    save(n + ".JPG", None, E / f"{n.lower()}.jpg", (1200, 1200), q=80)

# --- About page (4:3) ---
save("VAIL1508.JPG", (0, 250/900, 1, 700/900), IMG / "about-frames.jpg", (1400, 1400))

# --- Videos: H.264, no sound, web-optimised; 100fps footage slowed down for smooth slow motion ---
VID.mkdir(parents=True, exist_ok=True)
def video(name, out, vf, poster_at=2):
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(SRC / name), "-an", "-vf", vf, "-r", "30",
           "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(VID / out)]
    subprocess.run(cmd, check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(poster_at), "-i", str(VID / out), "-frames:v", "1", "-q:v", "4", str(VID / out.replace(".mp4", ".jpg"))], check=True)
    print(f"site/assets/video/{out}  {(VID / out).stat().st_size // 1024} KB")

video("OU0143C736A260824_115915J4_OMKKK.MP4", "frames-light.mp4", "setpts=3.333*PTS,scale=1280:-2", poster_at=12)   # light sweeping across the three frames
video("OU0143C734A260824_115844FE_OMKKK.MP4", "frames-closeup.mp4", "setpts=2*PTS,scale=720:-2")     # slow move along the frames (portrait)
video("IMG_1815.MOV", "winner-frame.mp4", "setpts=2*PTS,scale=720:-2")                               # Winner frame in hand (portrait)
