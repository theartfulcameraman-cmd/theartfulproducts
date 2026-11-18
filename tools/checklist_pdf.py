"""Builds a printable A4 PDF of the launch checklist.
Run: python tools/checklist_pdf.py  →  The-Artful-Products-Launch-Checklist.pdf"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
LOGO = (ROOT / "site/assets/img/logo.svg").read_text(encoding="utf-8")
OUT = ROOT / "The-Artful-Products-Launch-Checklist.pdf"

# (title, needed_for_launch, intro, items)  — an item starting with "»" is an indented sub-point
SECTIONS = [
  ("Product photos", True, "For each of the 4 products: Magnet · Keychain · Medal holder · Terrain frame", [
    "Magnet: 3–5 photos", "Keychain: 3–5 photos", "Medal holder: 3–5 photos", "Terrain frame: 3–5 photos",
    "» Clean front shot on a plain light background (square, 1200 px+)",
    "» Angled shot showing the 3D depth of the terrain",
    "» Close-up of the route line / texture",
    "» “In use”: on a fridge, on keys, on a wall with medals",
    "» Every colour / finish you offer"]),
  ("Product details", True, "For each product", [
    "Final price (₹)", "Colours / finishes offered, with names", "Size and material (confirm or correct)",
    "Dispatch time", "Options that cost extra (e.g. frame size)",
    "What you need from the customer to personalise it", "Which products to tag “New” or “Bestseller”"]),
  ("Business & contact details", True, None, [
    "WhatsApp business number", "Order / enquiry email address", "Phone number (if different)",
    "Studio address, or “Pune only”", "Business hours", "Instagram link", "YouTube link",
    "Legal business name (as registered)", "GSTIN (if you have one)"]),
  ("Policies", True, "Razorpay requires these pages. Answer these and I'll draft them.", [
    "Can customers cancel? Up to when?", "Refund rules: damaged · wrong item · personalised",
    "How many days refunds take", "Courier / shipping partner", "Do you ship outside India?"]),
  ("Payments", True, None, [
    "Create & verify Razorpay account (PAN, bank, business details)",
    "Send the Key ID only (rzp_test_… then rzp_live_…). Never share the Key Secret.",
    "Shipping charge: free above ₹999, ₹79 below?", "Gift wrap at ₹49: keep or remove?", "Cash on delivery: yes / no?"]),
  ("Domain & hosting", True, None, [
    "Choose domain (theartfulproducts.com, check .in)", "Buy it (GoDaddy / Hostinger / Namecheap / Cloudflare)",
    "Create free hosting account (Netlify or Cloudflare Pages)", "Optional: email at your domain (Google Workspace / Zoho)"]),
  ("Home page images", False, None, [
    "3–4 wide lifestyle banner photos (about 2400 × 1000 px)",
    "1 wall photo: frame + medal holder + magnets together",
    "4 process photos: GPX on screen · preview on WhatsApp · printing · finishing / packing"]),
  ("Videos (optional)", False, None, [
    "10–20 s loop of the printer printing (MP4, no sound)",
    "Close-up / turntable clip of each product (9:16 works for Reels too)", "Stall / expo clip"]),
  ("For Organisers page", False, None, [
    "Photos of your stall at an event", "Photos of bulk / custom award work (prototypes are fine)",
    "Event / organiser logos (only with permission)", "Minimum order quantities and lead time"]),
  ("Nice to have (after launch)", False, None, [
    "Real customer reviews (name, city, quote, product)", "Upcoming race expos / stalls (name, date, city)",
    "Launch offer: discount %, code, dates", "Newsletter account (e.g. Mailchimp)",
    "Google Analytics / Meta Pixel ID", "Font name used in the logo"]),
]
DONE = ["Logo", "“A” icon files", "Brand colours", "Website design & layout"]

def section(title, star, intro, items):
    lis = "".join(
        f'<li class="sub"><span class="dash"></span>{t[1:].strip()}</li>' if t.startswith("»")
        else f'<li><span class="box"></span>{t}</li>' for t in items)
    return f'''<section class="{'star' if star else ''}">
      <h2>{title}{'<em>Needed for launch</em>' if star else ''}</h2>
      {f'<p class="intro">{intro}</p>' if intro else ''}<ul>{lis}</ul></section>'''

HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  @page {{ size: A4; margin: 14mm 13mm 14mm; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font: 9.6pt/1.4 "Plus Jakarta Sans", Arial, sans-serif; color: #111; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  header {{ display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 10px; border-bottom: 2.5px solid #111; margin-bottom: 4px; }}
  header .logo svg {{ height: 40px; width: auto; display: block; }}
  header .meta {{ text-align: right; font-size: 8.5pt; color: #555; }}
  .bar {{ height: 4px; background: linear-gradient(90deg,#FBEE41,#FCC612 18%,#F18F40 45%,#EC683B 70%,#E63F39); margin-bottom: 14px; }}
  h1 {{ font-size: 21pt; letter-spacing: -.02em; margin: 0 0 2px; }}
  .lead {{ color: #555; margin: 0 0 14px; }}
  .legend {{ display: flex; gap: 18px; font-size: 8.5pt; color: #555; margin-bottom: 14px; }}
  .legend span {{ display: inline-flex; align-items: center; gap: 6px; }}
  .cols {{ column-count: 2; column-gap: 9mm; }}
  section {{ break-inside: avoid; margin: 0 0 12px; padding: 10px 12px 8px; border: 1.2px solid #E2DED7; border-radius: 10px; }}
  section.star {{ border-color: #111; }}
  h2 {{ font-size: 11.5pt; margin: 0 0 4px; display: flex; justify-content: space-between; align-items: center; gap: 8px; }}
  h2 em {{ font-style: normal; font-size: 7pt; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; color: #111; background: linear-gradient(90deg,#FCC612,#F18F40 55%,#EC683B); padding: 2px 7px; border-radius: 20px; white-space: nowrap; }}
  .intro {{ margin: 0 0 6px; font-size: 8.5pt; color: #555; }}
  ul {{ list-style: none; margin: 0; padding: 0; }}
  li {{ display: flex; gap: 8px; align-items: flex-start; padding: 3.5px 0; border-bottom: 1px dotted #D9D4CB; }}
  li:last-child {{ border-bottom: 0; }}
  .box {{ flex: none; width: 11px; height: 11px; border: 1.4px solid #111; border-radius: 2.5px; margin-top: 2px; }}
  li.sub {{ padding-left: 19px; color: #444; font-size: 8.8pt; border-bottom: 0; padding-top: 1.5px; padding-bottom: 1.5px; }}
  .dash {{ flex: none; width: 6px; height: 1.5px; background: #EC683B; margin-top: 7px; }}
  .done {{ border-style: dashed; }}
  .tick {{ flex: none; width: 11px; height: 11px; border-radius: 2.5px; margin-top: 2px; background: #111; color: #FCC612; font-size: 8pt; line-height: 11px; text-align: center; font-weight: 800; }}
  .notes {{ break-inside: avoid; border: 1.2px solid #E2DED7; border-radius: 10px; padding: 10px 12px; }}
  .notes h2 {{ margin-bottom: 6px; }}
  .notes i {{ display: block; height: 20px; border-bottom: 1px solid #D9D4CB; }}
  footer {{ margin-top: 8px; font-size: 8pt; color: #777; text-align: center; }}
</style></head><body>
<header><div class="logo">{LOGO}</div><div class="meta">Website launch checklist<br>Version: Nov 2026</div></header>
<div class="bar"></div>
<h1>What we need to launch the store</h1>
<p class="lead">Tick each item as you send it. Photos and videos can go in any folder; they'll be cropped, resized and connected to the right products.</p>
<div class="legend"><span><span class="box"></span> To do</span><span><b style="background:linear-gradient(90deg,#FCC612,#EC683B);padding:1px 6px;border-radius:20px;font-size:7pt;color:#111">NEEDED FOR LAUNCH</b> Do these first</span></div>
<div class="cols">
{''.join(section(*s) for s in SECTIONS)}
<section class="done"><h2>Already done</h2><ul>{''.join(f'<li><span class="tick">✓</span>{d}</li>' for d in DONE)}</ul></section>
<div class="notes"><h2>Notes</h2>{'<i></i>' * 18}</div>
</div>
<footer>The Artful Products · A unit of The Artful Company · Pune</footer>
</body></html>"""

import re
def to_bw(html):
    """Black-and-white version: every brand colour and gradient becomes black/grey."""
    html = re.sub(r'stop-color="#[0-9a-fA-F]{6}"', 'stop-color="#111111"', html)       # logo "A" marks
    html = re.sub(r"linear-gradient\([^;\"]*?\)(?=[;\"])", "#111", html)                   # bars and badges
    html = html.replace("#EC683B", "#111").replace("color: #FCC612", "color: #fff").replace("color:#111\">NEEDED", "color:#fff\">NEEDED")
    html = html.replace("h2 em {{", "h2 em {{")  # no-op guard
    html = re.sub(r"(h2 em \{[^}]*?)color: #111;", r"\1color: #fff;", html)
    return html

def render(html, out):
    html_path = ROOT / "tools" / "_checklist.html"
    html_path.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(html_path.as_uri(), wait_until="networkidle")
        pg.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True)
        b.close()
    html_path.unlink()
    print("wrote", out)

render(HTML, OUT)
render(to_bw(HTML), OUT.with_name(OUT.stem + "-BW.pdf"))
