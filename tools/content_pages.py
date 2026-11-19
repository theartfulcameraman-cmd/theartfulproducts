"""Text pages: About, policies (required by Razorpay) and the 404 page.
Anything inside <mark class="ph">…</mark> is a blank to fill in — it shows highlighted on the site
until replaced. Edit here, then run: python tools/build_pages.py"""

UPDATED = "18 November 2026"

def ph(text):
    return f'<mark class="ph">{text}</mark>'

BIZ = ph("[Legal business name]")
ADDR = ph("[Registered business address, Pune, Maharashtra]")
EMAIL = '<a href="mailto:orders@theartfulproducts.com">orders@theartfulproducts.com</a>'
PHONE = '<a href="https://wa.me/917588130344">+91 75881 30344</a>'

def crumb(label):
    return f'<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><i>/</i><span>{label}</span></nav>'

def doc(title, intro, body):
    return f"""
<div class="wrap doc-wrap">
  {crumb(title)}
  <article class="doc">
    <h1>{title}</h1>
    <p class="muted small">Last updated: {UPDATED}</p>
    {f'<p class="lede">{intro}</p>' if intro else ''}
    {body}
    <div class="doc-help"><b>Questions about this policy?</b> Write to {EMAIL} or WhatsApp {PHONE}. We usually reply the same day.</div>
  </article>
</div>"""

SHIPPING = doc("Shipping policy",
  "We make every piece in our studio in Pune and ship it across India.",
  f"""
<h2>Where we ship</h2>
<p>We currently ship to all serviceable PIN codes in India. {ph("[We do not ship outside India yet. / We ship to: …]")}</p>
<h2>When your order ships</h2>
<ul>
  <li><b>Ready-made items</b> (magnets, keychains, medal holders): dispatched within {ph("3–5")} working days.</li>
  <li><b>Personalised items</b> (route keepsakes and frames): dispatched within {ph("7–10")} working days <b>after you approve the digital preview</b> we send you.</li>
  <li><b>Bulk and event orders:</b> lead time is agreed in your quote.</li>
</ul>
<p>Working days are Monday to Saturday, excluding public holidays.</p>
<h2>Delivery time</h2>
<p>After dispatch, delivery usually takes {ph("2–5")} working days for metro cities and {ph("4–8")} working days elsewhere. We ship with {ph("[courier / shipping partner]")}, and you'll get a tracking link by WhatsApp or email when your order ships.</p>
<h2>Shipping charges</h2>
<p>Shipping is <b>free on orders above ₹999</b>. Orders below ₹999 have a flat shipping charge of <b>₹79</b>. Digital gift cards have no shipping charge.</p>
<h2>Damaged or missing parcels</h2>
<p>If your parcel arrives damaged, please share a photo or unboxing video within <b>48 hours</b> of delivery and we'll reprint and resend your piece at no cost. If tracking shows delivered but you haven't received it, contact us within 7 days and we'll raise it with the courier.</p>
<h2>Wrong address</h2>
<p>Please check your address and PIN code carefully at checkout. If a parcel is returned because of an incorrect address or failed delivery attempts, we can re-ship it once you pay the shipping charge again.</p>
""")

REFUND = doc("Cancellation & refund policy",
  "Most of what we make is personalised, so here's exactly how cancellations, reprints and refunds work.",
  f"""
<h2>Cancelling an order</h2>
<ul>
  <li><b>Ready-made items:</b> you can cancel any time before the order is dispatched for a full refund.</li>
  <li><b>Personalised items:</b> you can cancel for a full refund <b>until you approve the digital preview</b>. Once you've approved it, printing starts and the order can't be cancelled.</li>
  <li><b>Bulk and event orders:</b> cancellation terms are set out in your quote.</li>
</ul>
<p>To cancel, message us on WhatsApp or email with your order number. {ph("[Confirm or change these cancellation windows]")}</p>
<h2>Returns</h2>
<p>Because personalised pieces are made for you, they can't be returned or exchanged unless they arrive damaged or with a mistake on our side. Ready-made items can be returned unused, in original packaging, within {ph("7")} days of delivery; return shipping is paid by the customer.</p>
<h2>Damaged, defective or wrong items</h2>
<p>If your piece arrives damaged, has a printing defect, or doesn't match the preview you approved, send us a photo within <b>48 hours</b> of delivery. We'll reprint and resend it free of charge, or refund you in full if you prefer.</p>
<h2>How refunds are paid</h2>
<p>Approved refunds go back to your original payment method (UPI, card, netbanking or wallet) through Razorpay. Refunds are processed within {ph("5–7")} working days of approval; your bank may take a few more days to show it.</p>
""")

PRIVACY = doc("Privacy policy",
  f"This policy explains what personal information {BIZ} (“we”, “us”) collects through this website, why, and how we protect it.",
  f"""
<h2>What we collect</h2>
<ul>
  <li><b>Order details:</b> your name, phone number, email, delivery address and the items you order.</li>
  <li><b>Personalisation details:</b> event names, dates, finish times, and any GPX file or activity link you send us to make your piece.</li>
  <li><b>Messages:</b> anything you send us through our forms, WhatsApp or email.</li>
  <li><b>Payment information:</b> payments are handled by Razorpay. We never see or store your card, UPI or bank details.</li>
  <li><b>Device data:</b> your cart and wishlist are saved in your own browser. {ph("[If you add analytics: we use Google Analytics / Meta Pixel to understand site visits.]")}</li>
</ul>
<h2>How we use it</h2>
<p>Only to make and deliver your order, send you previews and updates, answer your questions, and — if you sign up — send you news about new products. We don't sell or rent your information to anyone.</p>
<h2>Who we share it with</h2>
<p>Only the services needed to run the shop: Razorpay (payments), our courier {ph("[shipping partner]")} (delivery), and {ph("[email / newsletter service, if used]")}. Each handles your data under its own privacy policy.</p>
<h2>Your route data</h2>
<p>GPX files and activity links are used only to make your piece. We don't publish your routes, and we delete route files {ph("6 months")} after your order is delivered unless you ask us to keep them for a reorder.</p>
<h2>How long we keep it</h2>
<p>We keep order records for as long as Indian tax and accounting law requires, and other information only as long as it's needed for the purposes above.</p>
<h2>Your choices</h2>
<p>You can ask us to see, correct or delete your personal information, or unsubscribe from emails at any time, by writing to {EMAIL}.</p>
<h2>Contact</h2>
<p>{BIZ}, {ADDR}. Email: {EMAIL}.</p>
""")

TERMS = doc("Terms & conditions",
  f"These terms apply when you use this website or buy from {BIZ}. By placing an order you agree to them.",
  f"""
<h2>About us</h2>
<p>The Artful Products is a unit of The Artful Company, operated by {BIZ}, {ADDR}{', GSTIN ' + ph('[GSTIN]') }.</p>
<h2>Products and personalisation</h2>
<p>Our pieces are 3D-printed and finished by hand, so small variations in colour, texture and layer lines are normal and not defects. Product photos are representative. For personalised items, you're responsible for the event details, names and route files you give us; please check the digital preview carefully, because we print exactly what you approve.</p>
<h2>Route files and content you send</h2>
<p>By sending us a route file, logo or other content, you confirm you have the right to use it and allow us to use it to make your order. We may share photos of finished pieces on our website and social media; tell us if you'd prefer we didn't feature yours.</p>
<h2>Prices and payment</h2>
<p>All prices are in Indian Rupees (₹) and {ph("[include / exclude]")} GST. Shipping and gift wrap are shown at checkout. Payment is taken in full when you order, through Razorpay. We may correct obvious pricing errors and will contact you before processing an order affected by one.</p>
<h2>Orders</h2>
<p>An order is confirmed once payment succeeds. We may decline or cancel an order (with a full refund) if an item can't be made, a route file can't be used, or we suspect fraud.</p>
<h2>Shipping, cancellations and refunds</h2>
<p>These are covered in our <a href="shipping.html">Shipping policy</a> and <a href="refunds.html">Cancellation &amp; refund policy</a>, which form part of these terms.</p>
<h2>Bulk and event orders</h2>
<p>Bulk orders follow the quote and terms we agree with you in writing, including samples, quantities, lead times and payment schedule.</p>
<h2>Intellectual property</h2>
<p>The website, designs, product shapes, photos and brand names belong to The Artful Company and may not be copied or resold without permission.</p>
<h2>Liability</h2>
<p>Our pieces are decorative keepsakes. To the extent the law allows, our liability for any order is limited to the amount you paid for it.</p>
<h2>Governing law</h2>
<p>These terms are governed by the laws of India, and disputes are subject to the courts of Pune, Maharashtra.</p>
""")

ABOUT = f"""
<div class="wrap">
  {crumb("About us")}
  <div class="page-hero about-hero">
    <div>
      <span class="kick">About us</span>
      <h1>We turn the routes you earned into things you can hold.</h1>
      <p class="muted">The Artful Products is the product studio of The Artful Company, a creative agency in Pune. We design and 3D-print keepsakes made from the routes people ride, run and trek: the climb you suffered up, the loop you finally finished, the trail that changed you.</p>
      <div class="row" style="flex-wrap:wrap"><a class="btn primary" href="shop.html">Shop the collection</a><a class="btn" href="organisers.html">For organisers</a></div>
    </div>
    <div class="art photo"><img src="assets/img/about-frames.jpg" alt="Terrain award frames made for The Great Himalayan 2026" width="1400" height="1049"></div>
  </div>
</div>
<section class="sec" style="padding-top:8px"><div class="wrap about-story">
  <div>
    <h2>Why route keepsakes?</h2>
    <p>A finisher medal says you were there. Your route says what it took. Every ride, run and trek has a shape — the switchbacks, the long flat, the last hill before the finish — and we think that shape deserves more than a screenshot in an app.</p>
    <p>So we rebuild it. We take the real terrain and your own GPS track, print it in layers, and finish each piece by hand: a magnet for the fridge, a keychain for every day, a rack for the medals, a frame for the one that mattered most.</p>
  </div>
  <div>
    <h2>How we work</h2>
    <ul class="about-list">
      <li><b>Your real route.</b> Built from elevation data and your GPX or Strava link, not a generic mountain.</li>
      <li><b>Preview first.</b> You see and approve a digital preview before anything is printed.</li>
      <li><b>Made in Pune.</b> Designed, printed, finished and packed in our own studio.</li>
      <li><b>At the start line.</b> You'll find us at race expos across India, taking orders and meeting finishers.</li>
    </ul>
  </div>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap"><div class="org-band">
  <div><span class="kick">More than routes</span><h2>New collections are on the way.</h2><p>Route keepsakes are where we started. We're designing more pieces across new categories, all made with the same care.</p><a class="btn light" href="index.html#soon">Get notified</a></div>
  <ul><li>Designed in-house</li><li>3D-printed in Pune</li><li>Finished and checked by hand</li><li>Made for people who earn their keepsakes</li></ul>
</div></div></section>"""

NOT_FOUND = """
<div class="wrap nf">
  <div class="nf-mark" aria-hidden="true"></div>
  <h1>This trail doesn't go anywhere.</h1>
  <p class="muted">The page you're looking for has moved or never existed. Let's get you back on route.</p>
  <div class="row" style="justify-content:center;flex-wrap:wrap"><a class="btn primary" href="index.html">Back to home</a><a class="btn" href="shop.html">Shop all products</a></div>
</div>"""

def pages(DESC):
    return {
        "about.html": ("about", "About us | The Artful Products", "The Artful Products is the 3D-printing product studio of The Artful Company, Pune — keepsakes made from the routes you ride, run and trek.", ABOUT),
        "shipping.html": ("doc", "Shipping policy | The Artful Products", "Shipping times, charges and delivery across India.", SHIPPING),
        "refunds.html": ("doc", "Cancellation & refund policy | The Artful Products", "How cancellations, reprints and refunds work.", REFUND),
        "privacy.html": ("doc", "Privacy policy | The Artful Products", "What personal information we collect and how we use it.", PRIVACY),
        "terms.html": ("doc", "Terms & conditions | The Artful Products", "The terms that apply when you shop with The Artful Products.", TERMS),
        "404.html": ("nf", "Page not found | The Artful Products", DESC, NOT_FOUND),
    }
