/* ==================================================================
   The Artful Products — store data
   This is the ONLY file you edit to add products, change prices or
   update contact details. See ../../../README.md for a step-by-step guide.

   Anything marked PLACEHOLDER must be replaced before launch.

   The site adjusts itself to what's here:
   - a category appears in the menu only once it has a product
   - "On Sale" appears only once a product has a compareAt price
   - stars appear only on products with a rating
   - filters, tabs and "Shop by sport" appear once there are 9+ products
   ================================================================== */

window.SITE = {
  name: "The Artful Products",
  tagline: "Objects made from the moments you earned.",
  whatsapp: "917588130344",            // WhatsApp Business: country code + number, no +
  email: "orders@theartfulproducts.com",
  phone: "+91 75881 30344",
  city: "Pune, Maharashtra",
  social: { instagram: "#", youtube: "#", strava: "#" }, // PLACEHOLDER links
  freeShippingAbove: 1799,
  shippingFlat: 79,
  giftWrap: 49,
  dispatchDays: [3, 5],                 // working days, for the delivery estimate

  showCategoryIcons: true,              // round category icons below the home-page banner

  announcements: [
    "Free shipping across India on orders above ₹1,799",
    "Meet us at race expos — personalised frames made to order",
    "Organising an event? Finisher gifts in bulk"
  ],

  // First slide of the home-page banner: a looping video. Set active:false to hide it.
  heroFeature: { active: true, video: "assets/video/frames-light.mp4",
    kicker: "Featured · The Great Himalayan 2026", title: "Podium awards made from the route",
    text: "Medal, race details and the 600 km route in 3D terrain, for every podium finisher.",
    cta: "See the event", href: "organisers.html#featured" },

  // Home-page countdown strip — switch on when you run a real offer.
  flashSale: { active: false, title: "Finisher Week", text: "10% off route keepsakes this week.", code: "FINISHER10", percent: 10, ends: "2026-12-31T23:59:59+05:30" },

  // Other discount codes customers can type at checkout: CODE: percent off. Example: { EXPO10: 10 }
  discountCodes: {},

  // Email popup — switch on once a newsletter service is connected.
  popup: { active: false, delaySec: 12, title: "Get 10% off your first keepsake", text: "New drops and expo dates. No spam.", code: "FINISHER10" },

  // Razorpay — PLACEHOLDER. Paste your Key ID from the Razorpay dashboard (rzp_test_… first, then rzp_live_…).
  // The Key SECRET never goes here: it lives only on the server, in /home/<cpanel-user>/artful-config.php.
  razorpayKey: "rzp_test_U20L0ZHQXXOCAc",   // TEST key — swap for rzp_live_… after KYC approval
  // Payment server (PHP, in site/api). Works on MilesWeb; not on the local preview, which has no PHP.
  razorpayOrderEndpoint: "api/create-order.php",
  razorpayVerifyEndpoint: "api/verify-payment.php"
};

/* Categories. "art" picks the placeholder drawing used until you add a photo
   (magnet, keychain, holder, frame, coaster, print, trophy, ornament, lamp, …). */
window.CATEGORIES = [
  { id: "fridge-magnets",  code: "MAG", name: "3D Trail Fridge Magnets", art: "magnet",   blurb: "The ride, run or trek you finished, raised in 3D on your fridge." },
  { id: "keychains",       code: "KEY", name: "3D Trail Keychains",      art: "keychain", blurb: "Your route outline, carried every day." },
  { id: "frames",          code: "FRM", name: "Terrain Frames",  art: "frame",  blurb: "Your route in 3D terrain, framed next to your medal." },
  { id: "medal-display",   code: "MED", name: "Medal Display",   art: "holder", blurb: "Ridge-line racks for every medal you've earned." }
];

window.SPORTS = [
  { id: "running", name: "Running" },
  { id: "cycling", name: "Cycling" },
  { id: "trekking", name: "Trekking" }
];

/* code = the last part of a SKU (3 letters, unique) */
const COLOURS = {
  charcoal: { name: "Charcoal", hex: "#2B2A28", code: "CHR" }, white: { name: "Chalk", hex: "#F1EFEA", code: "CHK" },
  sand: { name: "Sand", hex: "#D8C6A5", code: "SND" }, orange: { name: "Ember", hex: "#EC683B", code: "EMB" },
  glow: { name: "Glow", hex: "#CDE7AE", code: "GLW" }, oak: { name: "Oak", hex: "#B98B5E", code: "OAK" }, stone: { name: "Stone", hex: "#9A9792", code: "STN" }
};

/* ------------------------------------------------------------------
   PRODUCTS — copy a block to add a new one. Only id, sku, name, cat, price,
   short, desc are required. Everything else is optional:
     sku:      "TAP-<category code>-<3-letter product code>", e.g. "TAP-MAG-TRL".
               The colour code is added per order line: TAP-MAG-TRL-CHR = Trail magnet, Charcoal.
               Custom (admin-only) products get TAP-CUS-<category>-<number>; one-off items TAP-ONEOFF.
     images:   ["assets/img/products/trail-magnet-1.jpg", …]  (real photos)
     colours:  [COLOURS.charcoal, …]       options: { label, values, extra }
     personal: true  → shows the "your event & details" box
     isNew / best / featured / badge / compareAt / rating / reviews / stock / tiers
     status:   "live" (default) · "soon" (notify me) · "quote" (bulk only)
   ------------------------------------------------------------------ */
window.PRODUCTS = [
  { id: "trail-magnet", sku: "TAP-MAG-TRL", name: "3D Trail Fridge Magnet", cat: "fridge-magnets", art: "magnet",
    price: 349,                          // PLACEHOLDER price
    best: true, personal: true,
    sports: ["running", "cycling", "trekking"], colours: [COLOURS.charcoal, COLOURS.white, COLOURS.sand],
    short: "Your route raised on real terrain, on a strong magnet.",
    desc: "A palm-sized relief of the terrain you covered, with your route raised on top in a contrasting colour. Backed with a strong magnet.",
    specs: ["Approx. 70 × 50 mm", "Two-colour 3D print", "Strong magnet backing", "Dispatch in 3–5 working days"] },

  { id: "route-keychain", sku: "TAP-KEY-RTE", name: "3D Trail Keychain", cat: "keychains", art: "keychain",
    price: 299,                          // PLACEHOLDER price
    isNew: true, personal: true,
    sports: ["running", "cycling", "trekking"], colours: [COLOURS.charcoal, COLOURS.orange, COLOURS.glow],
    short: "Your route outline as a slim, tough keychain.",
    desc: "The outline of your route as a slim keychain tag, with the event name and date on the back. Steel ring included.",
    specs: ["Approx. 55 mm tall", "Tough, flexible print", "Steel split ring", "Dispatch in 3–5 working days"] },

  { id: "medal-holder", sku: "TAP-MED-RDG", name: "Ridge Medal Holder", cat: "medal-display", art: "holder",
    price: 1499,                         // PLACEHOLDER price
    best: true,
    sports: ["running", "cycling", "trekking"], colours: [COLOURS.charcoal, COLOURS.stone, COLOURS.orange],
    short: "A wall rack shaped like a ridge line, for all your medals.",
    desc: "A wall hanger shaped like an elevation profile, with hooks for your medals. Wall plugs and screws included.",
    specs: ["Approx. 400 × 90 mm", "Steel hooks", "Holds up to 12 medals", "Dispatch in 3–5 working days"] },

  { id: "terrain-frame", sku: "TAP-FRM-TER", name: "Terrain Award Frame", cat: "frames", art: "frame",
    price: 3499,                         // PLACEHOLDER price
    best: true, featured: true, badge: "Made to order", personal: true,   // featured = the home-page spotlight
    sports: ["running", "cycling", "trekking"], colours: [COLOURS.charcoal, COLOURS.oak, COLOURS.white],
    images: ["assets/img/products/terrain-frame-1.jpg", "assets/img/products/terrain-frame-2.jpg", "assets/img/products/terrain-frame-3.jpg",
             "assets/img/products/terrain-frame-4.jpg", "assets/img/products/terrain-frame-5.jpg"],
    video: "assets/video/winner-frame.mp4",   // shown as the last item in the product gallery
    short: "Your route in 3D terrain, framed next to your finisher medal.",
    desc: "Our signature piece. Your finisher medal is mounted on a printed race panel with your event, category, distance, date and elevation, and the route you completed is rebuilt below it in 3D terrain. Pictured: the podium frames we made for The Great Himalayan 2026.",
    specs: ["Deep shadow-box frame", "3D-printed terrain insert", "Medal mount + name plate", "Dispatch in 7–10 working days"] }
];

/* Customer reviews — leave empty until you have real ones; the section hides itself.
   Example: { name: "Priya, runner, Pune", text: "…", product: "terrain-frame" } */
window.TESTIMONIALS = [];

window.FAQ = [
  ["How do I send you my route?", "After you order, we'll message you on WhatsApp. Send us a GPX file, a Strava/Garmin activity link, or just the event name."],
  ["Will I see a preview before you print?", "Yes. For every personalised piece we send a digital preview for your approval before printing."],
  ["How long does delivery take?", "Ready items dispatch in 3–5 working days; personalised frames take 7–10. Delivery across India usually takes another 2–5 days."],
  ["What payment methods do you accept?", "UPI, credit and debit cards, netbanking and wallets through Razorpay."],
  ["Do you take bulk orders for events?", "Yes — finisher keepsakes and podium awards for races and treks. See the For Organisers page or WhatsApp us."],
  ["What if my piece arrives damaged?", "Send us a photo within 48 hours of delivery and we'll reprint and resend it."],
  ["Can I return a personalised item?", "Personalised items can't be returned because they're made for you, but we'll always fix print or delivery issues."]
];
