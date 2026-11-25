"""Writes the page shells in ../site. Each page shares the same <head>, header,
footer and scripts; only the <main> body differs. Run: python build_pages.py"""
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"
DESC = ("3D-printed keepsakes of the routes you ride, run and trek: magnets, keychains, "
        "medal racks and terrain award frames. Made in Pune, shipped across India.")

SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{base}<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="The Artful Products">
<meta property="og:type" content="{ogtype}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{jsonld}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="icon" type="image/svg+xml" href="assets/img/mark.svg">
<meta name="theme-color" content="#111111">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body data-page="{page}"{body_attr}>
<header id="site-header"></header>
<main>
{body}
</main>
<footer id="site-footer"></footer>
<script src="assets/js/data.js"></script>
<script src="assets/js/built.js"></script>
<script src="assets/js/pricing.js"></script>
<script src="assets/js/store.js"></script>
<script src="assets/js/pages.js"></script>
</body>
</html>
"""

def crumb(label):
    return f'<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><i>/</i><span>{label}</span></nav>'

PAGES = {
"index.html": ("home", "The Artful Products: the route you earned, made real", DESC, """
<h1 class="sr">The Artful Products: 3D-printed keepsakes of the routes you ride, run and trek</h1>
<section style="padding:24px 0 0"><div class="wrap"><div class="hero" id="hero"></div></div></section>
<section class="sec" id="circles-sec" style="padding:36px 0 0"><div class="wrap" id="circles"></div></section>
<section class="sec" id="tabbed"><div class="wrap">
  <div class="sec-head"><div><h2>Finisher favourites</h2><p class="muted">Keepsakes for the routes you ride, run and trek.</p></div><div class="tab-nav"></div></div>
  <div class="tab-body"></div>
</div></section>
<section style="padding:0 0 8px" id="flash"></section>
<section class="sec" id="event-sec" style="padding-top:0"><div class="wrap"><div class="event-strip">
  <div class="es-txt"><span class="kick">As awarded at</span><h2>The Great Himalayan 2026</h2>
    <p class="muted">Podium frames with the 600&nbsp;km route in 3D terrain, made for Inspire India&rsquo;s world&rsquo;s highest-altitude ultra cycling race.</p>
    <a class="btn primary" href="organisers.html#featured">See the event</a></div>
  <div class="es-photos">
    <img src="assets/img/products/terrain-frame-5.jpg" alt="Winner holding his terrain award frame" loading="lazy">
    <img src="assets/img/events/great-himalayan/ad104601.jpg" alt="Podium finisher with his frame" loading="lazy">
    <img src="assets/img/products/terrain-frame-3.jpg" alt="Close-up of the 3D terrain and route" loading="lazy">
  </div>
</div></div></section>

<section class="sec" id="catgrid-sec"><div class="wrap">
  <div class="sec-head"><h2>Shop by category</h2><a class="link-u" href="shop.html">View all products &rarr;</a></div>
  <div class="catgrid" id="catgrid"></div>
</div></section>
<section class="sec" style="background:var(--soft)"><div class="wrap spotlight" id="spotlight"></div></section>
<section class="sec" id="lookbook-sec"><div class="wrap lookbook" id="lookbook"></div></section>
<section class="sec" id="sports" style="padding-top:8px"><div class="wrap">
  <div class="sec-head"><div><h2>Shop by sport</h2><p class="muted">Pick your discipline.</p></div><div class="tab-nav"></div></div>
  <div class="grid"></div>
  <p style="text-align:center;margin-top:28px"><a class="btn sp-all" href="shop.html">View all</a></p>
</div></section>
<div class="marquee" aria-hidden="true"><div class="mq"><span>Your route, made real</span><span>Printed in Pune</span><span>Ride &middot; Run &middot; Trek</span><span>Preview before print</span><span>Your route, made real</span><span>Printed in Pune</span><span>Ride &middot; Run &middot; Trek</span><span>Preview before print</span></div></div>
<section class="sec"><div class="wrap">
  <div class="sec-head"><div><h2>Made with care</h2><p class="muted">What goes into every piece we make.</p></div></div>
  <div class="details" id="details"></div>
</div></section>
<section class="sec" id="reviews-sec" style="background:var(--soft)"><div class="wrap">
  <div class="sec-head"><div><h2>Loved by finishers</h2></div></div>
  <div id="reviews"></div>
</div></section>
<section class="sec" style="padding-bottom:0"><div class="wrap"><div class="soon-band">
  <div id="soon"><span class="kick">More on the way</span><h2>New collections are coming soon</h2><p class="muted">We're designing new pieces beyond route keepsakes. Leave your email and you'll be the first to know.</p></div>
  <form class="soon-form" data-subscribe="coming-soon"><input type="email" name="email" required placeholder="Your email" aria-label="Email"><input type="text" name="website" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true"><button class="btn primary">Notify me</button></form>
</div></div></section>
<section class="sec"><div class="wrap"><div class="org-band">
  <div><span class="kick">For race &amp; event organisers</span><h2>Give every finisher their course to keep.</h2><p>Custom 3D course keepsakes, podium trophies and volunteer gifts, made in bulk and branded for your event.</p><a class="btn light" href="organisers.html">Request a quote</a></div>
  <ul><li>Course-map finisher magnets, coasters and keychains</li><li>Podium trophies made from your course terrain</li><li>Your logo and branding on every piece</li><li>A sample to approve before production</li><li>A stall at your expo for personalised orders</li></ul>
</div></div></section>
<div id="recent"></div>"""),

"shop.html": ("shop", "Shop | The Artful Products", DESC, """
<div class="wrap">
  <div class="col-head" id="col-head"></div>
  <div class="col">
    <aside id="filters" aria-label="Filters"></aside>
    <div>
      <div class="toolbar">
        <button class="btn ghost sm only-m" data-fopen>Filter</button>
        <span id="count"></span>
        <button class="colbtn" data-cols="3" title="3 per row">3</button><button class="colbtn on" data-cols="4" title="4 per row">4</button>
        <label><span class="sr">Sort by</span><select id="sort"><option value="featured">Featured</option><option value="new">Newest</option><option value="rating">Top rated</option><option value="low">Price, low to high</option><option value="high">Price, high to low</option></select></label>
      </div>
      <div class="chips" id="chips"></div>
      <div class="grid" id="grid" data-cols="4"></div>
    </div>
  </div>
</div>
<div id="after"></div>"""),

"product.html": ("product", "Product | The Artful Products", DESC, """
<div class="wrap" id="pdp"></div>
<div id="related"></div>
<div id="recent"></div>"""),

"cart.html": ("cart", "Cart | The Artful Products", DESC, f"""
<div class="wrap">
  {crumb("Cart")}
  <h1>Your cart</h1>
  <div class="cartpg" id="cart"></div>
</div>"""),

"wishlist.html": ("wishlist", "Wishlist | The Artful Products", DESC, f"""
<div class="wrap" style="padding-bottom:40px">
  {crumb("Wishlist")}
  <h1>Your wishlist</h1>
  <p class="muted">Saved on this device.</p>
  <div id="wish"></div>
</div>"""),

"organisers.html": ("org", "For Organisers | The Artful Products",
  "Custom 3D-printed finisher keepsakes, podium trophies and volunteer gifts for races, marathons, cycling events and treks across India.", f"""
<div class="wrap">
  {crumb("For Organisers")}
  <div class="page-hero">
    <div><span class="kick">For race &amp; event organisers</span><h1>Awards your finishers will actually keep.</h1>
      <p class="muted">We turn your course into 3D-printed finisher gifts, podium trophies and volunteer keepsakes, branded for your event and delivered in bulk. We can also run a stall at your expo for personalised orders.</p>
      <div class="row" style="flex-wrap:wrap"><a class="btn primary" href="#enquire">Request a quote</a><a class="btn" href="https://wa.me/" data-wa>WhatsApp us</a></div></div>
    <div class="art photo" id="org-art"><img src="assets/img/events/great-himalayan/podium-frames.jpg" alt="Winner, 2nd and 3rd place terrain award frames made for The Great Himalayan 2026" width="1600" height="1067"></div>
  </div>
</div>
<section class="sec" id="featured" style="padding-top:8px"><div class="wrap">
  <div class="feat">
    <div class="feat-txt">
      <span class="kick">Featured event</span>
      <h2>The Great Himalayan 2026</h2>
      <p class="muted">Podium awards for the 8th edition of The Great Himalayan by Inspire India, the world&rsquo;s highest-altitude ultra cycling race, held on 22 August 2026.</p>
      <p>Every podium finisher took home a frame with their medal, a race panel showing their place, category, distance, date and elevation, and the 600&nbsp;km route rebuilt below it in 3D terrain.</p>
      <ul class="feat-facts">
        <li><b>600 km</b><span>route in 3D terrain</span></li>
        <li><b>Podium</b><span>Winner, 2nd &amp; 3rd per category</span></li>
        <li><b>Made in Pune</b><span>designed, printed, framed</span></li>
      </ul>
      <a class="btn primary" href="#enquire">Get frames like these for your event</a>
    </div>
    <div class="feat-vid"><video src="assets/video/winner-frame.mp4" poster="assets/video/winner-frame.jpg" autoplay muted loop playsinline aria-label="A Winner frame from The Great Himalayan, held in hand"></video></div>
  </div>
  <h3 class="feat-gal-h">On the podium</h3>
  <div class="feat-gal">
    <a href="assets/img/events/great-himalayan/ad104601.jpg" target="_blank" rel="noopener"><img src="assets/img/events/great-himalayan/ad104601.jpg" alt="Rider with their podium frame at The Great Himalayan 2026" loading="lazy" width="1200" height="800"></a>
    <a href="assets/img/events/great-himalayan/ad104655.jpg" target="_blank" rel="noopener"><img src="assets/img/events/great-himalayan/ad104655.jpg" alt="Rider with their podium frame at The Great Himalayan 2026" loading="lazy" width="1200" height="800"></a>
    <a href="assets/img/events/great-himalayan/ad104671.jpg" target="_blank" rel="noopener"><img src="assets/img/events/great-himalayan/ad104671.jpg" alt="Rider with their podium frame at The Great Himalayan 2026" loading="lazy" width="1200" height="800"></a>
    <a href="assets/img/events/great-himalayan/ad104680.jpg" target="_blank" rel="noopener"><img src="assets/img/events/great-himalayan/ad104680.jpg" alt="Rider with their podium frame at The Great Himalayan 2026" loading="lazy" width="1200" height="800"></a>
    <a href="assets/img/events/great-himalayan/ad104695.jpg" target="_blank" rel="noopener"><img src="assets/img/events/great-himalayan/ad104695.jpg" alt="Rider with their podium frame at The Great Himalayan 2026" loading="lazy" width="1200" height="800"></a>
    <a href="assets/img/events/great-himalayan/ad104699.jpg" target="_blank" rel="noopener"><img src="assets/img/events/great-himalayan/ad104699.jpg" alt="Rider with their podium frame at The Great Himalayan 2026" loading="lazy" width="1200" height="800"></a>
    <a href="assets/img/events/great-himalayan/ad104619.jpg" target="_blank" rel="noopener"><img src="assets/img/events/great-himalayan/ad104619.jpg" alt="Rider with their podium frame at The Great Himalayan 2026" loading="lazy" width="1200" height="800"></a>
    <a href="assets/img/events/great-himalayan/ad104594.jpg" target="_blank" rel="noopener"><img src="assets/img/events/great-himalayan/ad104594.jpg" alt="Rider with their podium frame at The Great Himalayan 2026" loading="lazy" width="1200" height="800"></a>
  </div>
</div></section>
<section class="sec" style="padding-top:8px"><div class="wrap">
  <div class="sec-head"><h2>What we make for events</h2></div>
  <div class="offer">
    <div><span class="kick">Finishers</span><h3>Course keepsakes</h3><p class="muted">Course-map magnets or keychains for every finisher, with your event branding.</p></div>
    <div><span class="kick">Podium</span><h3>Terrain awards</h3><p class="muted">Category and podium awards made from your real course terrain, with name plates.</p></div>
    <div><span class="kick">Crew &amp; sponsors</span><h3>Thank-you gifts</h3><p class="muted">Desk pieces and frames for volunteers, pacers and sponsors.</p></div>
  </div>
</div></section>
<section class="sec" style="padding-top:8px"><div class="wrap">
  <div class="sec-head"><div><h2>How it works</h2><p class="muted">Pricing depends on quantity and design. Tell us about your event and we will send a quote.</p></div></div>
  <div class="offer">
    <div><span class="kick">01</span><h3>Share your event</h3><p class="muted">Course map, number of finishers, date and branding.</p></div>
    <div><span class="kick">02</span><h3>Approve a sample</h3><p class="muted">We design your piece and send a sample for your approval.</p></div>
    <div><span class="kick">03</span><h3>We deliver on time</h3><p class="muted">Produced in Pune and delivered before race day.</p></div>
  </div>
</div></section>
<section class="sec" id="enquire" style="padding-top:8px"><div class="wrap form-wrap">
  <div><h2>Tell us about your event</h2><p class="muted">Share a few details and we will reply within 2 working days with options, a sample plan and pricing.</p><p class="muted small">Lead time is usually 3&ndash;5 weeks depending on quantity.</p></div>
  <form class="form-card" id="org-form">
    <input type="text" name="website" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true">
    <label class="fld">Organisation<input name="org" required></label>
    <label class="fld">Event name<input name="event" required></label>
    <label class="fld">Event date<input name="date" type="date"></label>
    <label class="fld">Expected participants<input name="count" inputmode="numeric" placeholder="e.g. 1500"></label>
    <fieldset class="full"><legend>Interested in</legend>
      <label class="chk"><input type="checkbox" name="want" value="3D Trail Fridge Magnets"><span>3D Trail Fridge Magnets</span></label>
      <label class="chk"><input type="checkbox" name="want" value="3D Trail Keychains"><span>3D Trail Keychains</span></label>
      <label class="chk"><input type="checkbox" name="want" value="Ridge Medal Holders"><span>Ridge Medal Holders</span></label>
      <label class="chk"><input type="checkbox" name="want" value="Terrain Award Frames"><span>Terrain Award Frames</span></label>
      <label class="chk"><input type="checkbox" name="want" value="Custom / not sure yet"><span>Custom / not sure yet</span></label>
    </fieldset>
    <label class="fld">Budget per piece (&#8377;)<input name="budget" inputmode="numeric" placeholder="Optional"></label>
    <label class="fld">Your name<input name="name" required autocomplete="name"></label>
    <label class="fld">Phone<input name="phone" required inputmode="tel" autocomplete="tel"></label>
    <label class="fld">Email<input name="email" type="email" required autocomplete="email"></label>
    <label class="fld full">Anything else<textarea name="notes" rows="3" placeholder="Course link, categories, branding"></textarea></label>
    <div class="actions full"><button class="btn primary" type="submit" value="whatsapp">Send on WhatsApp</button><button class="btn" type="submit" value="email">Send by email</button></div>
  </form>
</div></section>"""),

"account.html": ("account", "My account | The Artful Products", DESC, f"""
<div class="wrap" style="padding-bottom:48px">
  {crumb("My account")}
  <div id="acct"></div>
</div>"""),

"faq.html": ("faq", "FAQ | The Artful Products", DESC, f"""
<div class="wrap" style="padding-bottom:48px">
  {crumb("FAQ")}
  <h1>Frequently asked questions</h1>
  <p class="muted">Can&rsquo;t find your answer? <a class="link-u" style="margin:0" href="contact.html">Contact us</a></p>
  <div id="faq"></div>
</div>"""),

"contact.html": ("contact", "Contact | The Artful Products", DESC, f"""
<div class="wrap">
  {crumb("Contact")}
  <h1>Get in touch</h1>
  <p class="muted">Questions about an order, a custom piece or an event? We usually reply the same day.</p>
  <div class="contact-grid">
    <div class="c-cards">
      <div><b>WhatsApp</b><a id="c-wa" target="_blank" rel="noopener"></a></div>
      <div><b>Email</b><a id="c-mail"></a></div>
      <div><b>Studio</b><span class="muted">The Artful Company, Pune, Maharashtra. PLACEHOLDER address</span></div>
      <div><b>Hours</b><span class="muted">Mon&ndash;Sat, 10am&ndash;7pm IST</span></div>
    </div>
    <form class="form-card" id="contact-form">
      <input type="text" name="website" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true">
      <label class="fld">Name<input name="name" required autocomplete="name"></label>
      <label class="fld">Email<input name="email" type="email" required autocomplete="email"></label>
      <label class="fld">Phone<input name="phone" inputmode="tel" autocomplete="tel"></label>
      <label class="fld">Topic<select name="topic"><option>Question about a product</option><option>My order</option><option>Custom / personalised piece</option><option>Event or bulk order</option><option>Something else</option></select></label>
      <label class="fld full">Message<textarea name="msg" rows="5" required></textarea></label>
      <div class="actions full"><button class="btn primary" type="submit" value="whatsapp">Send on WhatsApp</button><button class="btn" type="submit" value="email">Send by email</button></div>
    </form>
  </div>
</div>"""),
}

# Cache-busting: append a short hash of each asset so browsers fetch the new version after edits.
import hashlib, re as _re
def _ver(m):
    path = m.group(2)
    h = hashlib.md5((SITE / path).read_bytes()).hexdigest()[:8]
    return f'{m.group(1)}{path}?v={h}"'

# ------------------------------------------------------------------
# Extra pages, product pages, preview images, sitemap
# ------------------------------------------------------------------
import json, html as _h, sys
sys.path.insert(0, str(Path(__file__).parent))
from content_pages import pages as content_pages
PAGES.update(content_pages(DESC))

# The live web address. PLACEHOLDER until the domain is bought — then change it and rebuild,
# so Google, WhatsApp and Instagram previews point at the right site.
SITE_URL = "https://theartfulproducts.com"

def catalog():
    """Run data.js in a headless browser and return SITE, CATEGORIES, PRODUCTS as plain data."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        pg.set_content("<script>" + (SITE / "assets/js/data.js").read_text(encoding="utf-8") + "</script>")
        data = pg.evaluate("() => ({ site: window.SITE, cats: window.CATEGORIES, products: window.PRODUCTS })")
        b.close()
    return data

def og_images(products):
    """1200x630 share images: the product photo if there is one, else the placeholder drawing, with the logo."""
    from playwright.sync_api import sync_playwright
    out = SITE / "assets/img/og"; out.mkdir(parents=True, exist_ok=True)
    tpl = (Path(__file__).parent / "_og.html")
    tpl.write_text(f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap" rel="stylesheet">
<style>body{{margin:0;width:1200px;height:630px;font-family:"Plus Jakarta Sans",sans-serif;background:#fff;display:grid;grid-template-columns:560px 1fr;overflow:hidden}}
#art{{background:#F4F2EE;width:560px;height:630px;overflow:hidden}}#art svg,#art img{{width:100%;height:100%;object-fit:cover;display:block}}
.t{{padding:64px 60px;display:flex;flex-direction:column}}.t img.lg{{height:64px;width:auto;align-self:flex-start}}
.k{{margin-top:auto;font-weight:700;font-size:22px;letter-spacing:.06em;text-transform:uppercase;color:#EC683B}}
h1{{font-size:62px;line-height:1.04;letter-spacing:-.03em;margin:12px 0 18px}}p{{font-size:26px;color:#555;margin:0}}
.bar{{position:absolute;left:0;right:0;bottom:0;height:12px;background:linear-gradient(90deg,#FBEE41,#FCC612 18%,#F18F40 45%,#EC683B 70%,#E63F39)}}
#site-header,#site-footer{{display:none}}</style></head>
<body><div id="art"></div><div class="t"><img class="lg" src="{(SITE/'assets/img/logo.svg').as_uri()}"><span class="k" id="k"></span><h1 id="h"></h1><p id="p"></p></div><div class="bar"></div>
<div id="site-header"></div><div id="site-footer"></div>
<script src="{(SITE/'assets/js/data.js').as_uri()}"></script><script src="{(SITE/'assets/js/pricing.js').as_uri()}"></script><script src="{(SITE/'assets/js/store.js').as_uri()}"></script></body></html>""", encoding="utf-8")
    jobs = [("default", None)] + [(p["id"], p) for p in products]
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
        pg.goto(tpl.as_uri(), wait_until="networkidle")
        for name, p in jobs:
            pg.evaluate("""([p]) => {
              const T = window.TAP, S = window.SITE;
              if (!p) { document.getElementById('art').innerHTML = T.art('frame', '#2B2A28', 5, 0, '#F4F2EE').replace('PLACEHOLDER', '');
                document.getElementById('k').textContent = '3D-printed in Pune';
                document.getElementById('h').textContent = 'The route you earned, made real.';
                document.getElementById('p').textContent = 'Magnets, keychains, medal racks and terrain frames made from your ride, run or trek.'; return; }
              const imgs = p.images || [];
              document.getElementById('art').innerHTML = imgs.length ? '<img src="../site/' + imgs[0] + '">' : T.art(p.art, (p.colours && p.colours[0] && p.colours[0].hex) || '#2B2A28', T.seedOf(p.id), 0, '#F4F2EE').replace('PLACEHOLDER', '');
              const cat = (window.CATEGORIES.find(c => c.id === p.cat) || {}).name || '';
              document.getElementById('k').textContent = cat + (p.price ? '  ·  ₹' + p.price.toLocaleString('en-IN') : '');
              document.getElementById('h').textContent = p.name;
              document.getElementById('p').textContent = p.short || '';
            }""", [p])
            pg.wait_for_timeout(150)
            pg.screenshot(path=str(out / f"{name}.png"))
        b.close()
    tpl.unlink()
    print("wrote", len(jobs), "share images")

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"

data = catalog()
S, CATS, PRODUCTS = data["site"], data["cats"], data["products"]
# catalogue the PHP payment server prices orders from (site/api/catalog.json) — always rebuilt from data.js
_srv = {k: S.get(k) for k in ("name", "whatsapp", "freeShippingAbove", "shippingFlat", "giftWrap", "flashSale")}
_srv["discountCodes"] = S.get("discountCodes") or {}
(SITE / "api/catalog.json").write_text(json.dumps({"site": _srv, "products": PRODUCTS}, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
og_images(PRODUCTS)

ORG = {"@context": "https://schema.org", "@type": "Organization", "name": "The Artful Products",
       "url": SITE_URL, "logo": SITE_URL + "/assets/img/logo.svg",
       "parentOrganization": {"@type": "Organization", "name": "The Artful Company"},
       "sameAs": [u for u in (S.get("social") or {}).values() if u and u != "#"]}

# product pages: same layout as product.html, but with their own title, description, preview and Google data
PRODUCT_BODY = PAGES["product.html"][3]
built = []
for p in PRODUCTS:
    slug = f"product-{p['id']}.html"
    cat = next((c["name"] for c in CATS if c["id"] == p.get("cat")), "")
    title = f"{p['name']} | The Artful Products"
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "description": p.get("desc") or p.get("short", ""),
          "brand": {"@type": "Brand", "name": "The Artful Products"}, "category": cat, "sku": p.get("sku") or p["id"],
          "image": [SITE_URL + "/" + i for i in p.get("images", [])] or [SITE_URL + f"/assets/img/og/{p['id']}.png"],
          "url": f"{SITE_URL}/{slug}"}
    if p.get("price") and p.get("status", "live") == "live":
        ld["offers"] = {"@type": "Offer", "priceCurrency": "INR", "price": str(p["price"]), "availability": "https://schema.org/InStock", "url": f"{SITE_URL}/{slug}"}
    if p.get("rating") and p.get("reviews"):
        ld["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": p["rating"], "reviewCount": p["reviews"]}
    PAGES[slug] = ("product", title, _h.escape(p.get("short", ""), quote=True), PRODUCT_BODY,
                   {"image": f"{SITE_URL}/assets/img/og/{p['id']}.png", "ogtype": "product", "jsonld": jsonld(ld), "body_attr": f' data-id="{p["id"]}"'})
    built.append(p["id"])

(SITE / "assets/js/built.js").write_text(
    "/* Generated by tools/build_pages.py — products that have their own page (product-<id>.html). Don't edit. */\n"
    f"window.BUILT_PRODUCTS = {json.dumps(built)};\n", encoding="utf-8", newline="\n")

for name, spec in PAGES.items():
    page, title, desc, body, *extra = spec
    extra = extra[0] if extra else {}
    url = SITE_URL + "/" + ("" if name == "index.html" else name)
    html = SHELL.format(page=page, title=title, desc=desc, body=body.strip(), url=url,
        base='<base href="/">\n' if name == "404.html" else "",
        ogtype=extra.get("ogtype", "website"), image=extra.get("image", SITE_URL + "/assets/img/og/default.png"),
        jsonld=extra.get("jsonld", jsonld(ORG) if name == "index.html" else ""), body_attr=extra.get("body_attr", ""))
    if name in ("cart.html", "wishlist.html", "404.html", "account.html"):
        html = html.replace('<meta name="description"', '<meta name="robots" content="noindex">\n<meta name="description"')
    html = _re.sub(r'((?:href|src)=")(assets/(?:css|js)/[^"?]+)"', _ver, html)
    (SITE / name).write_text(html, encoding="utf-8", newline="\n")
print("wrote", len(PAGES), "pages")

skip = {"cart.html", "wishlist.html", "404.html", "product.html", "account.html"}
urls = [SITE_URL + "/" + ("" if n == "index.html" else n) for n in PAGES if n not in skip]
(SITE / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8", newline="\n")
(SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /cart.html\nDisallow: /wishlist.html\nDisallow: /admin/\nDisallow: /api/\nDisallow: /account.html\nDisallow: /social/\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8", newline="\n")
print("wrote sitemap.xml with", len(urls), "pages, and robots.txt")
