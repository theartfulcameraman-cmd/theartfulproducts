/* ==================================================================
   The Artful Products — store engine
   Shared by every page: helpers, placeholder art, cart, wishlist,
   header + mega menu, search, cart drawer, quick view, popup, footer.
   ================================================================== */
(function () {
  const S = window.SITE, P = window.PRODUCTS, CATS = window.CATEGORIES, SPORTS = window.SPORTS;
  P.forEach(p => { p.status = p.status || "live"; p.specs = p.specs || []; });

  /* ---------------- helpers ---------------- */
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const inr = n => "₹" + Math.round(n).toLocaleString("en-IN");
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const param = k => new URLSearchParams(location.search).get(k);
  const byId = id => P.find(p => p.id === id);
  const cat = id => CATS.find(c => c.id === id);
  // The site grows with the catalogue: empty categories, sports and "On Sale" stay hidden.
  const liveCats = () => CATS.filter(c => P.some(p => p.cat === c.id));
  const liveSports = () => SPORTS.filter(s => P.some(p => p.sports?.includes(s.id)));
  const hasSale = () => P.some(p => p.compareAt > p.price);
  const isBig = () => P.length > 8;   // switch on filters, tabs and sport browsing once the shop grows
  const featured = () => P.find(p => p.featured) || P.find(p => p.best) || P[0];
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} }
  };
  const icon = {
    search: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    bag: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 8h14l-1.2 12H6.2z"/><path d="M9 8V7a3 3 0 0 1 6 0v1"/></svg>',
    heart: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>',
    user: '<svg viewBox="0 0 24 24" width="21" height="21" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>',
    pin: '<svg viewBox="0 0 24 24" width="21" height="21" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    eye: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
    plus: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>',
    close: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6 6 18"/></svg>',
    menu: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    chev: '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4"><path d="m6 9 6 6 6-6"/></svg>',
    left: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="m15 6-6 6 6 6"/></svg>',
    right: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 6 6 6-6 6"/></svg>',
    truck: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 6h11v10H3zM14 10h4l3 3v3h-7"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/></svg>',
    lock: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg>',
    spark: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/></svg>',
    chat: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 5h16v11H9l-5 4z"/></svg>',
    star: '<svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor"><path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/></svg>',
    ig: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1.1" fill="currentColor" stroke="none"/></svg>',
    yt: '<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M22.5 7.2a2.8 2.8 0 0 0-2-2C18.8 4.7 12 4.7 12 4.7s-6.8 0-8.5.5a2.8 2.8 0 0 0-2 2A29 29 0 0 0 1 12a29 29 0 0 0 .5 4.8 2.8 2.8 0 0 0 2 2c1.7.5 8.5.5 8.5.5s6.8 0 8.5-.5a2.8 2.8 0 0 0 2-2A29 29 0 0 0 23 12a29 29 0 0 0-.5-4.8zM9.8 15.1V8.9L15.5 12z"/></svg>',
    gift: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="9" width="18" height="12" rx="1"/><path d="M12 9v12M3 13h18M12 9S9 3 6.5 5 9 9 12 9zm0 0s3-6 5.5-4S15 9 12 9z"/></svg>'
  };

  /* ---------------- placeholder product art ----------------
     Every product image is drawn here until real photos arrive.
     Replace by adding `images: ["assets/img/…jpg", …]` to a product. */
  function rnd(seed) { let s = (seed * 9301 + 49297) % 233280; return () => (s = (s * 9301 + 49297) % 233280) / 233280; }
  function seedOf(str) { let h = 7; for (const ch of String(str)) h = (h * 31 + ch.charCodeAt(0)) % 100000; return h; }
  function routePath(r, x0, y0, w, h, n = 12) {
    let d = "", x = x0, y = y0 + h * (0.3 + r() * 0.4);
    for (let i = 0; i <= n; i++) { d += (i ? " L" : "M") + x.toFixed(1) + "," + y.toFixed(1); x += w / n; y = Math.max(y0, Math.min(y0 + h, y + (r() - 0.5) * h * 0.45)); }
    return d;
  }
  function contours(r, cx, cy, rx, ry, n, stroke, op = 0.35) {
    let out = "";
    for (let i = 1; i <= n; i++) {
      const k = i / n, pts = [];
      for (let a = 0; a < 20; a++) { const t = a / 20 * Math.PI * 2, w = 1 + Math.sin(t * 3 + i) * 0.1 + Math.cos(t * 2 + cx) * 0.06; pts.push((cx + Math.cos(t) * rx * k * w).toFixed(1) + "," + (cy + Math.sin(t) * ry * k * w).toFixed(1)); }
      out += `<path d="M${pts.join("L")}Z" fill="none" stroke="${stroke}" stroke-opacity="${op}" stroke-width="1.4"/>`;
    }
    return out;
  }
  function shade(hex, amt) { const n = parseInt(hex.slice(1), 16); const f = c => Math.max(0, Math.min(255, c + amt)); return "#" + ((f(n >> 16) << 16) | (f((n >> 8) & 255) << 8) | f(n & 255)).toString(16).padStart(6, "0"); }
  function lum(hex) { const n = parseInt(hex.slice(1), 16); return ((n >> 16) * 0.3 + ((n >> 8) & 255) * 0.59 + (n & 255) * 0.11) / 255; }

  function art(type, hex = "#2B2A28", seed = 1, view = 0, bg = "#F2F0EC") {
    const r = rnd(seed + view * 17), dark = lum(hex) < 0.5, line = dark ? "#FFFFFF" : "#2B2A28", accent = hex === "#EC683B" ? "#2B2A28" : "#EC683B";
    const zoom = [1, 1.25, 0.9, 1.1][view % 4], tilt = [-6, 4, 0, -2][view % 4];
    let g = "";
    switch (type) {
      case "magnet":
        g = `<rect x="110" y="140" width="180" height="125" rx="16" fill="${shade(hex, -25)}" transform="translate(6 8)"/>
          <rect x="110" y="140" width="180" height="125" rx="16" fill="${hex}"/>
          ${contours(r, 200, 202, 85, 58, 6, line, 0.28)}
          <path d="${routePath(r, 125, 165, 150, 75)}" fill="none" stroke="${accent}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>`; break;
      case "keychain":
        g = `<circle cx="200" cy="105" r="30" fill="none" stroke="#A8A49C" stroke-width="7"/>
          <path d="M200 135 L200 150" stroke="#A8A49C" stroke-width="6"/>
          <path d="M150 155 C190 140 250 150 262 190 C275 240 240 300 200 300 C150 300 128 250 140 210 C146 190 120 170 150 155Z" fill="${shade(hex, -25)}" transform="translate(5 7)"/>
          <path d="M150 155 C190 140 250 150 262 190 C275 240 240 300 200 300 C150 300 128 250 140 210 C146 190 120 170 150 155Z" fill="${hex}"/>
          <path d="${routePath(r, 155, 185, 95, 90, 8)}" fill="none" stroke="${line}" stroke-opacity=".7" stroke-width="5" stroke-linecap="round"/>
          <circle cx="200" cy="164" r="7" fill="${bg}"/>`; break;
      case "coaster":
        g = [[150, 235], [250, 235], [200, 160]].map(([x, y], i) => `<circle cx="${x + 5}" cy="${y + 7}" r="70" fill="${shade(hex, -25)}"/><circle cx="${x}" cy="${y}" r="70" fill="${hex}"/>${contours(r, x, y, 62, 62, 5, line, 0.3)}${i === 2 ? `<path d="${routePath(r, x - 45, y - 25, 90, 50, 7)}" fill="none" stroke="${accent}" stroke-width="5" stroke-linecap="round"/>` : ""}`).join(""); break;
      case "print":
        g = `<rect x="95" y="90" width="210" height="250" rx="4" fill="${shade(hex, -30)}" transform="translate(7 9)"/>
          <rect x="95" y="90" width="210" height="250" rx="4" fill="${hex}"/>
          ${contours(r, 200, 205, 95, 105, 9, line, 0.3)}
          <path d="${routePath(r, 115, 130, 170, 160, 11)}" fill="none" stroke="${accent}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
          <rect x="115" y="312" width="80" height="7" rx="3" fill="${line}" fill-opacity=".45"/>`; break;
      case "frame":
        g = `<rect x="70" y="80" width="260" height="250" rx="6" fill="${shade(hex, -25)}" transform="translate(8 10)"/>
          <rect x="70" y="80" width="260" height="250" rx="6" fill="${hex}"/>
          <rect x="90" y="100" width="220" height="210" fill="#F7F5F1"/>
          <rect x="104" y="116" width="120" height="150" rx="3" fill="#E7E1D6"/>
          ${contours(r, 164, 191, 56, 70, 6, "#2B2A28", 0.25)}
          <path d="${routePath(r, 112, 140, 104, 100, 8)}" fill="none" stroke="#EC683B" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M257 116 L247 175 M271 116 L281 175" stroke="#2F7F86" stroke-width="9"/>
          <circle cx="264" cy="195" r="24" fill="#D4A63A"/><circle cx="264" cy="195" r="15" fill="none" stroke="#B88A22" stroke-width="3"/>
          <rect x="104" y="280" width="110" height="16" rx="2" fill="#C9B79A"/>`; break;
      case "holder": {
        let pts = "60,215"; for (let i = 0; i <= 14; i++) pts += ` ${60 + i * 20},${150 + Math.sin(i * 0.9 + seed) * 22 - r() * 30}`; pts += " 340,215";
        g = `<polygon points="${pts}" fill="${shade(hex, -25)}" transform="translate(5 7)"/><polygon points="${pts}" fill="${hex}"/>`;
        for (let i = 0; i < 6; i++) { const x = 85 + i * 46, c = ["#D4A63A", "#B7B7B7", "#C47A3E"][i % 3], rib = ["#2F7F86", "#EC683B", "#2F5D50", "#5B4B8A"][i % 4];
          g += `<path d="M${x - 7} 215 L${x - 4} ${260 + (i % 2) * 18} M${x + 7} 215 L${x + 4} ${260 + (i % 2) * 18}" stroke="${rib}" stroke-width="7"/><circle cx="${x}" cy="${276 + (i % 2) * 18}" r="18" fill="${c}"/>`; }
        break; }
      case "trophy":
        g = `<rect x="125" y="285" width="150" height="40" rx="4" fill="${shade(hex, -25)}"/><rect x="125" y="280" width="150" height="38" rx="4" fill="${hex}"/>
          <rect x="165" y="292" width="70" height="14" rx="2" fill="#D4A63A"/>
          <polygon points="135,280 190,130 220,190 245,150 265,280" fill="#E7E1D6"/>
          <polygon points="190,130 205,170 220,190 200,180" fill="#FFFFFF" fill-opacity=".8"/>
          <polygon points="135,280 190,130 175,280" fill="#2B2A28" fill-opacity=".10"/>
          <path d="M150 268 L180 220 L205 238 L232 196 L252 262" fill="none" stroke="#EC683B" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>`; break;
      case "giftcard":
        g = `<rect x="85" y="130" width="230" height="145" rx="14" fill="${shade(hex, -25)}" transform="translate(7 9) rotate(-6 200 200)"/>
          <rect x="85" y="130" width="230" height="145" rx="14" fill="${hex}" transform="rotate(-6 200 200)"/>
          <g transform="rotate(-6 200 200)">${contours(r, 260, 230, 70, 50, 5, "#FFFFFF", 0.25)}
          <text x="105" y="170" font-family="Plus Jakarta Sans, sans-serif" font-weight="800" font-size="17" fill="#FFFFFF">THE ARTFUL</text>
          <text x="105" y="190" font-family="Plus Jakarta Sans, sans-serif" font-weight="500" font-size="13" fill="#FFFFFF" fill-opacity=".8">GIFT CARD</text>
          <text x="105" y="255" font-family="Plus Jakarta Sans, sans-serif" font-weight="800" font-size="30" fill="#FFFFFF">₹</text></g>`; break;
      case "ornament":
        g = `<path d="M200 70 L200 150" stroke="#A8A49C" stroke-width="3"/>
          <polygon points="120,300 200,150 240,220 262,190 300,300" fill="${shade(hex, -25)}" transform="translate(6 8)"/>
          <polygon points="120,300 200,150 240,220 262,190 300,300" fill="${hex}"/>
          <polygon points="200,150 220,190 205,185 190,200 180,180" fill="#FFFFFF" fill-opacity=".85"/>`; break;
      case "lamp":
        g = `<rect x="185" y="250" width="30" height="60" fill="#B9B4AA"/><ellipse cx="200" cy="315" rx="60" ry="12" fill="#9C978D"/>`;
        for (let i = 0; i < 9; i++) { const w = 70 + i * 14, y = 110 + i * 16; g += `<ellipse cx="200" cy="${y}" rx="${w}" ry="10" fill="${i % 2 ? hex : shade(hex, -12)}"/>`; }
        g += `<ellipse cx="200" cy="250" rx="120" ry="18" fill="#FFE9B8" fill-opacity=".7"/>`; break;
      case "bookend":
        g = [[95, 0], [215, 1]].map(([x, i]) => `<rect x="${x}" y="290" width="95" height="18" fill="${shade(hex, -25)}"/><polygon points="${x},290 ${x + 40},${150 + i * 20} ${x + 60},${200 + i * 10} ${x + 72},${180 - i * 10} ${x + 95},290" fill="${hex}"/>`).join("") +
          `<rect x="185" y="200" width="12" height="90" fill="#C47A3E"/><rect x="199" y="185" width="14" height="105" fill="#2F7F86"/>`; break;
      case "organiser":
        g = `<rect x="100" y="210" width="200" height="90" rx="8" fill="${shade(hex, -25)}" transform="translate(6 8)"/><rect x="100" y="210" width="200" height="90" rx="8" fill="${hex}"/>
          <path d="M100 210 L130 190 L160 200 L190 175 L230 195 L260 185 L300 210Z" fill="${shade(hex, 15)}"/>
          <rect x="135" y="130" width="8" height="85" fill="#EC683B" transform="rotate(-8 139 172)"/><rect x="155" y="120" width="8" height="95" fill="#2F7F86" transform="rotate(5 159 167)"/><rect x="240" y="160" width="40" height="45" fill="#FFFFFF"/>`; break;
      default:
        g = contours(r, 200, 200, 140, 140, 8, "#2B2A28");
    }
    return `<svg viewBox="0 0 400 400" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Product placeholder image">
      <rect width="400" height="400" fill="${bg}"/>
      <g transform="translate(200 210) scale(${zoom}) rotate(${tilt}) translate(-200 -210)">${g}</g>
      <text x="16" y="388" font-family="ui-monospace, monospace" font-size="10" letter-spacing="1.4" fill="#2B2A28" fill-opacity=".32">PLACEHOLDER</text></svg>`;
  }
  // product image: real photo if provided, else placeholder drawing
  function img(p, view = 0, hex) {
    if (p.images?.length) return `<img src="${esc(p.images[view % p.images.length])}" alt="${esc(p.name)}" loading="lazy">`;
    return art(p.art, hex || p.colours?.[0]?.hex, seedOf(p.id), view);
  }

  /* ---------------- pricing ---------------- */
  const unit = (p, qty = 1, optIdx = 0) => window.TAP_PRICING.unit(p, qty, optIdx);   // shared with the payment server (pricing.js)
  // product link: its own page (product-<id>.html, with share previews) once built, else the generic page
  const purl = p => (window.BUILT_PRODUCTS || []).includes(p.id) ? `product-${p.id}.html` : `product.html?id=${p.id}`;
  function priceHtml(p) {
    if (p.status === "quote") return `<span class="price">From ${inr(p.from)}<small>/piece</small></span>`;
    const cmp = p.compareAt && p.compareAt > p.price ? `<s>${inr(p.compareAt)}</s>` : "";
    return `<span class="price ${cmp ? "sale" : ""}">${inr(p.price)}${cmp}</span>`;
  }
  const stars = (rt, n) => rt ? `<span class="stars" aria-label="${rt} out of 5">${icon.star.repeat(5)}<em style="width:${rt / 5 * 100}%">${icon.star.repeat(5)}</em></span><span class="rev">(${n})</span>` : "";

  /* ---------------- cart / wishlist / recently viewed ---------------- */
  const CK = "tap_cart_v2", WK = "tap_wish_v1", RK = "tap_recent_v1";
  const Cart = {
    items: () => store.get(CK, []).filter(i => byId(i.id)),
    save(v) { store.set(CK, v); refreshCounts(); document.dispatchEvent(new Event("cart:change")); },
    add(it) {
      const c = Cart.items(), same = c.find(i => i.id === it.id && i.colour === it.colour && i.opt === it.opt && i.note === it.note);
      same ? (same.qty += it.qty) : c.push(it); Cart.save(c);
    },
    line: i => { const p = byId(i.id); return unit(p, i.qty, i.optIdx || 0) * i.qty; },
    subtotal: () => Cart.items().reduce((n, i) => n + Cart.line(i), 0),
    count: () => Cart.items().reduce((n, i) => n + i.qty, 0),
    // full order totals (same calculation the payment server runs)
    totals(opts) { return window.TAP_PRICING.compute(Cart.items(), opts, S, P); }
  };
  const Wish = {
    ids: () => store.get(WK, []).filter(byId),
    has: id => Wish.ids().includes(id),
    toggle(id) { const w = Wish.ids(), i = w.indexOf(id); i < 0 ? w.unshift(id) : w.splice(i, 1); store.set(WK, w); refreshCounts(); $$(`[data-wish="${id}"]`).forEach(b => b.classList.toggle("on", i < 0)); toast(i < 0 ? "Saved to wishlist" : "Removed from wishlist"); }
  };
  const Recent = {
    ids: () => store.get(RK, []).filter(byId),
    push(id) { const r = Recent.ids().filter(x => x !== id); r.unshift(id); store.set(RK, r.slice(0, 8)); }
  };
  function refreshCounts() {
    $$("[data-cart-count]").forEach(e => { const n = Cart.count(); e.textContent = n; e.hidden = !n; });
    $$("[data-wish-count]").forEach(e => { const n = Wish.ids().length; e.textContent = n; e.hidden = !n; });
  }

  /* ---------------- toast ---------------- */
  let toastT;
  function toast(msg) {
    let t = $("#toast"); if (!t) { t = document.createElement("div"); t.id = "toast"; t.setAttribute("role", "status"); document.body.appendChild(t); }
    t.textContent = msg; t.classList.add("show"); clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 2200);
  }

  /* ---------------- product card ---------------- */
  function card(p, opts = {}) {
    const c = cat(p.cat), off = p.compareAt ? Math.round((1 - p.price / p.compareAt) * 100) : 0;
    const badges = [off ? `<span class="tag sale">-${off}%</span>` : "", p.isNew ? `<span class="tag new">New</span>` : "", p.status === "soon" ? `<span class="tag soon">Coming soon</span>` : "", p.status === "quote" ? `<span class="tag bulk">Bulk</span>` : "", p.badge ? `<span class="tag">${esc(p.badge)}</span>` : ""].join("");
    const action = p.status === "live" ? `<button class="qa" data-quickadd="${p.id}">${icon.plus}<span>Quick add</span></button>`
      : p.status === "quote" ? `<a class="qa" href="organisers.html?product=${p.id}">Get a quote</a>` : `<a class="qa" href="${purl(p)}">Notify me</a>`;
    return `<article class="pcard ${opts.cls || ""}">
      <div class="pimg">
        <a href="${purl(p)}" class="pimg-link" aria-label="${esc(p.name)}"><span class="v1">${img(p, 0)}</span><span class="v2">${img(p, 1)}</span></a>
        <div class="tags">${badges}</div>
        <button class="wish ${Wish.has(p.id) ? "on" : ""}" data-wish="${p.id}" aria-label="Save ${esc(p.name)} to wishlist">${icon.heart}</button>
        <button class="qv" data-quickview="${p.id}" aria-label="Quick view ${esc(p.name)}">${icon.eye}</button>
        ${action}
      </div>
      <div class="pinfo">
        <span class="pcat">${esc(c?.name || "")}</span>
        <a class="pname" href="${purl(p)}">${esc(p.name)}</a>
        <div class="prate">${stars(p.rating, p.reviews)}</div>
        ${priceHtml(p)}
        ${p.colours?.length > 1 ? `<div class="sw-mini">${p.colours.map(s => `<span title="${esc(s.name)}" style="--c:${s.hex}"></span>`).join("")}</div>` : ""}
      </div></article>`;
  }

  /* ---------------- header ---------------- */
  function header() {
    const page = document.body.dataset.page;
    const live = liveCats(), fp = featured();
    const megaCats = `<div class="mega"><div class="wrap mega-in">
        <div class="mega-cols">${live.map(c => `<a class="mega-cat" href="shop.html?cat=${c.id}"><span class="mc-img">${art(c.art, "#2B2A28", seedOf(c.id))}</span><span><b>${c.name}</b><small>${esc(c.blurb)}</small></span></a>`).join("")}</div>
        <a class="mega-promo" href="${purl(fp)}"><span class="mp-img">${img(fp)}</span><span class="mp-txt"><small>Customer favourite</small><b>${esc(fp.name)}</b><u>Shop now</u></span></a>
      </div></div>`;
    const megaSport = `<div class="mega sm"><div class="wrap mega-list">${liveSports().map(s => `<a href="shop.html?sport=${s.id}">${s.name}</a>`).join("")}<a href="shop.html">All products →</a></div></div>`;
    $("#site-header").innerHTML = `
      <div class="announce"><div class="wrap ann-in">
        <div class="ann-links soc"><a href="${S.social.instagram}" target="_blank" rel="noopener" aria-label="Instagram">${icon.ig}</a><a href="${S.social.youtube}" target="_blank" rel="noopener" aria-label="YouTube">${icon.yt}</a></div>
        <div class="ann-msg" aria-live="polite">${S.announcements.map((m, i) => `<span class="${i ? "" : "on"}">${esc(m)}</span>`).join("")}</div>
        <div class="ann-links r"><span>🇮🇳 India (INR ₹)</span></div>
      </div></div>
      <div class="hmain"><div class="wrap hmain-in">
        <button class="icon-btn only-m" data-open="menu" aria-label="Open menu">${icon.menu}</button>
        <a class="logo" href="index.html"><img src="assets/img/logo-main.svg" alt="${S.name}" width="362" height="34"></a>
        <form class="search" action="shop.html" role="search">
          <label class="sel"><span class="sr">Category</span><select name="cat"><option value="">All categories</option>${live.map(c => `<option value="${c.id}">${c.name}</option>`).join("")}</select>${icon.chev}</label>
          <input name="q" type="search" placeholder="Search magnets, frames, medal racks…" autocomplete="off" aria-label="Search products">
          <button aria-label="Search">${icon.search}</button>
          <div class="sresults" hidden></div>
        </form>
        <div class="hicons">
          <a class="icon-btn only-d" href="organisers.html" aria-label="Find us at events">${icon.pin}</a>
          <a class="icon-btn only-d" href="contact.html" aria-label="Account">${icon.user}</a>
          <a class="icon-btn" href="wishlist.html" aria-label="Wishlist">${icon.heart}<b class="dot" data-wish-count hidden>0</b></a>
          <button class="icon-btn" data-open="cart" aria-label="Open cart">${icon.bag}<b class="dot" data-cart-count hidden>0</b></button>
        </div>
      </div></div>
      <nav class="hnav" aria-label="Main"><div class="wrap hnav-in">
        <div class="ni has"><a href="shop.html" ${page === "shop" ? 'aria-current="page"' : ""}>Shop all ${icon.chev}</a>${megaCats}</div>
        ${isBig() ? `<div class="ni has"><a href="shop.html">Shop by Sport ${icon.chev}</a>${megaSport}</div>` : ""}
        ${live.slice(0, 4).map(c => `<div class="ni"><a href="shop.html?cat=${c.id}">${c.name}</a></div>`).join("")}
        <div class="ni"><a href="organisers.html" ${page === "org" ? 'aria-current="page"' : ""}>For Organisers</a></div>        ${hasSale() ? `<div class="ni"><a class="hot" href="shop.html?sale=1">On Sale</a></div>` : ""}
      </div></nav>`;

    // rotating announcement
    const msgs = $$(".ann-msg span"); let ai = 0;
    if (msgs.length > 1) setInterval(() => { msgs[ai].classList.remove("on"); ai = (ai + 1) % msgs.length; msgs[ai].classList.add("on"); }, 4000);

    // sticky shadow
    const h = $("#site-header"); addEventListener("scroll", () => h.classList.toggle("stuck", scrollY > 40), { passive: true });

    // live search
    const f = $(".search"), q = f.q, out = $(".sresults", f);
    if (param("q")) q.value = param("q"); if (param("cat")) f.cat.value = param("cat");
    q.addEventListener("input", () => {
      const t = q.value.trim().toLowerCase(); if (t.length < 2) { out.hidden = true; return; }
      const hits = P.filter(p => (!f.cat.value || p.cat === f.cat.value) && (p.name + " " + p.short + " " + (cat(p.cat)?.name || "")).toLowerCase().includes(t)).slice(0, 6);
      out.innerHTML = hits.length ? hits.map(p => `<a href="${purl(p)}"><span class="sr-img">${img(p)}</span><span><b>${esc(p.name)}</b>${priceHtml(p)}</span></a>`).join("") + `<button class="sr-all">See all results for “${esc(q.value)}”</button>` : `<p class="sr-none">No products match “${esc(q.value)}”.</p>`;
      out.hidden = false;
    });
    out.addEventListener("click", e => { if (e.target.closest(".sr-all")) f.submit(); });
    document.addEventListener("click", e => { if (!f.contains(e.target)) out.hidden = true; });

    // mobile menu drawer
    const m = document.createElement("aside"); m.className = "drawer left"; m.id = "menu-drawer"; m.setAttribute("aria-label", "Menu");
    m.innerHTML = `<div class="dr-head"><b>Menu</b><button class="icon-btn" data-close aria-label="Close menu">${icon.close}</button></div>
      <div class="dr-body mnav">
        <p class="mnav-h">Shop</p><a href="shop.html">All products</a>${live.map(c => `<a href="shop.html?cat=${c.id}">${c.name}</a>`).join("")}
        ${isBig() ? `<p class="mnav-h">Shop by sport</p>${liveSports().map(s => `<a href="shop.html?sport=${s.id}">${s.name}</a>`).join("")}` : ""}
        <p class="mnav-h">More</p><a href="organisers.html">For Organisers</a>${hasSale() ? `<a class="hot" href="shop.html?sale=1">On Sale</a>` : ""}<a href="wishlist.html">Wishlist</a><a href="faq.html">Help centre</a><a href="contact.html">Contact</a>
      </div>`;
    document.body.appendChild(m);
  }

  /* ---------------- overlay drawers + modal ---------------- */
  function overlay() {
    let o = $("#overlay"); if (!o) { o = document.createElement("div"); o.id = "overlay"; document.body.appendChild(o); o.addEventListener("click", closeAll); } return o;
  }
  function open(el) { closeAll(); overlay().classList.add("on"); el.classList.add("on"); document.body.classList.add("locked"); el.querySelector("[data-close]")?.focus(); }
  function closeAll() { $$(".drawer.on, .modal.on").forEach(x => x.classList.remove("on")); $("#overlay")?.classList.remove("on"); document.body.classList.remove("locked"); }
  document.addEventListener("keydown", e => { if (e.key === "Escape") closeAll(); });

  /* ---------------- cart drawer ---------------- */
  function cartDrawer() {
    const d = document.createElement("aside"); d.className = "drawer right"; d.id = "cart-drawer"; d.setAttribute("aria-label", "Cart");
    document.body.appendChild(d);
    const render = () => {
      const items = Cart.items(), sub = Cart.subtotal(), left = S.freeShippingAbove - sub;
      d.innerHTML = `<div class="dr-head"><b>Your cart <span class="muted">(${Cart.count()})</span></b><button class="icon-btn" data-close aria-label="Close cart">${icon.close}</button></div>
        ${items.length ? `<div class="ship-bar"><p>${left > 0 ? `Add <b>${inr(left)}</b> more for <b>free shipping</b>` : `🎉 You've unlocked <b>free shipping</b>`}</p><i><em style="width:${Math.min(100, sub / S.freeShippingAbove * 100)}%"></em></i></div>
        <div class="dr-body">${items.map((i, n) => { const p = byId(i.id); return `
          <div class="cl">
            <a class="cl-img" href="${purl(p)}">${img(p, 0, i.hex)}</a>
            <div class="cl-info"><a href="${purl(p)}"><b>${esc(p.name)}</b></a>
              <span class="muted">${[i.colour, i.opt].filter(Boolean).map(esc).join(" · ")}</span>
              ${i.note ? `<span class="note">“${esc(i.note)}”</span>` : ""}
              <div class="cl-row"><div class="qty sm"><button data-cq="-1" data-n="${n}" aria-label="Fewer">−</button><span>${i.qty}</span><button data-cq="1" data-n="${n}" aria-label="More">+</button></div><b>${inr(Cart.line(i))}</b></div>
              <button class="link" data-crm="${n}">Remove</button></div>
          </div>`; }).join("")}</div>
        <div class="dr-foot"><div class="sum-row"><span>Subtotal</span><b>${inr(sub)}</b></div><p class="muted small">Shipping and gift wrap are added at checkout.</p>
          <a class="btn primary block" href="cart.html">Checkout</a><button class="btn ghost block" data-close>Continue shopping</button></div>`
        : `<div class="dr-body empty-dr"><div class="empty-ic">${icon.bag}</div><p>Your cart is empty.</p><a class="btn primary" href="shop.html">Start shopping</a></div>`}`;
    };
    render(); document.addEventListener("cart:change", render);
    d.addEventListener("click", e => {
      const c = Cart.items(), q = e.target.closest("[data-cq]"), rm = e.target.closest("[data-crm]");
      if (q) { const it = c[+q.dataset.n]; it.qty = Math.max(1, it.qty + +q.dataset.cq); Cart.save(c); }
      if (rm) { c.splice(+rm.dataset.crm, 1); Cart.save(c); }
      if (e.target.closest("[data-close]")) closeAll();
    });
  }

  /* ---------------- quick view ---------------- */
  function quickView(id) {
    const p = byId(id); if (!p) return;
    let m = $("#qv-modal"); if (!m) { m = document.createElement("div"); m.className = "modal"; m.id = "qv-modal"; m.setAttribute("role", "dialog"); m.setAttribute("aria-modal", "true"); document.body.appendChild(m); }
    m.innerHTML = `<button class="icon-btn mclose" data-close aria-label="Close">${icon.close}</button>
      <div class="qv-grid"><div class="qv-img">${img(p)}</div>
      <div class="qv-info"><span class="pcat">${esc(cat(p.cat)?.name)}</span><h2>${esc(p.name)}</h2><div class="prate">${stars(p.rating, p.reviews)}</div>${priceHtml(p)}
        <p class="muted">${esc(p.short)}</p>${buyBox(p, "qv")}<a class="link-u" href="${purl(p)}">View full details →</a></div></div>`;
    m.addEventListener("click", e => { if (e.target.closest("[data-close]")) closeAll(); }, { once: true });
    wireBuyBox(m, p); open(m);
  }

  /* ---------------- buy box (shared by quick view + product page) ---------------- */
  function buyBox(p, ctx) {
    if (p.status === "soon") return `<form class="buy notify" data-notify><p><b>Coming soon.</b> Leave your email and we'll tell you when it launches.</p><div class="row"><input type="email" required placeholder="Your email" aria-label="Email"><button class="btn primary">Notify me</button></div></form>`;
    if (p.status === "quote") return `<div class="buy"><p class="muted">Made in bulk for events. Minimum order applies.</p><a class="btn primary block" href="organisers.html?product=${p.id}">Get a quote for your event</a></div>`;
    return `<form class="buy" data-buy>
      ${p.colours?.length ? `<fieldset class="sw"><legend>Colour: <b data-cname>${esc(p.colours[0].name)}</b></legend>${p.colours.map((s, i) => `<label><input type="radio" name="colour" value="${i}" ${i ? "" : "checked"}><span style="--c:${s.hex}" title="${esc(s.name)}"></span></label>`).join("")}</fieldset>` : ""}
      ${p.options ? `<label class="fld">${esc(p.options.label)}<select name="opt">${p.options.values.map((v, i) => `<option value="${i}">${esc(v)}</option>`).join("")}</select></label>` : ""}
      ${p.personal && ctx !== "qv" ? `<label class="fld">Your event &amp; details <small class="muted">— we'll ask for the GPX / Strava link on WhatsApp</small><textarea name="note" rows="2" placeholder="e.g. Pune Half Marathon 2026 · Your name · 1:52:30"></textarea></label>` : ""}
      ${p.tiers && ctx !== "qv" ? `<div class="tiers"><p>Buy more, pay less</p><div>${p.tiers.map(t => `<span data-tier="${t.min}"><small>${t.min}+ pcs</small><b>${inr(t.price)}</b></span>`).join("")}</div></div>` : ""}
      <div class="row"><div class="qty"><button type="button" data-q="-1" aria-label="Fewer">−</button><input name="qty" value="1" inputmode="numeric" aria-label="Quantity"><button type="button" data-q="1" aria-label="More">+</button></div>
        <button class="btn primary grow" type="submit">Add to cart · <span data-total>${inr(unit(p))}</span></button>
        <button type="button" class="icon-btn boxed ${Wish.has(p.id) ? "on" : ""}" data-wish="${p.id}" aria-label="Save to wishlist">${icon.heart}</button></div>
      ${ctx !== "qv" ? `<button type="button" class="btn dark block" data-buynow>Buy it now</button>` : ""}
    </form>`;
  }
  function wireBuyBox(root, p) {
    const f = $("[data-buy]", root);
    const n = $("[data-notify]", root);
    if (n) n.addEventListener("submit", e => { e.preventDefault(); n.innerHTML = `<p><b>Thanks!</b> We'll email you when ${esc(p.name)} launches.</p>`; });
    if (!f) return;
    const sync = () => {
      const q = Math.max(1, parseInt(f.qty.value) || 1), oi = +(f.opt?.value || 0), ci = +(f.colour?.value || 0);
      $("[data-total]", f).textContent = inr(unit(p, q, oi) * q);
      if (p.colours?.length) { $("[data-cname]", f).textContent = p.colours[ci].name; document.dispatchEvent(new CustomEvent("colour:change", { detail: { id: p.id, hex: p.colours[ci].hex } })); }
      $$("[data-tier]", f).forEach(t => t.classList.toggle("on", +t.dataset.tier === Math.max(...p.tiers.filter(x => q >= x.min).map(x => x.min))));
    };
    f.addEventListener("click", e => { const b = e.target.closest("[data-q]"); if (b) { f.qty.value = Math.max(1, (parseInt(f.qty.value) || 1) + +b.dataset.q); sync(); } });
    f.addEventListener("input", sync); f.addEventListener("change", sync); sync();
    const add = () => {
      const ci = +(f.colour?.value || 0), oi = +(f.opt?.value || 0);
      Cart.add({ id: p.id, qty: Math.max(1, parseInt(f.qty.value) || 1), colour: p.colours?.[ci]?.name || "", hex: p.colours?.[ci]?.hex || "", opt: p.options ? p.options.values[oi] : "", optIdx: oi, note: f.note?.value.trim() || "" });
    };
    f.addEventListener("submit", e => { e.preventDefault(); add(); open($("#cart-drawer")); });
    $("[data-buynow]", f)?.addEventListener("click", () => { add(); location.href = "cart.html"; });
  }

  /* ---------------- newsletter popup + side tab ---------------- */
  function popup() {
    const cfg = S.popup; if (!cfg?.active) return;
    const m = document.createElement("div"); m.className = "modal pop"; m.id = "pop"; m.setAttribute("role", "dialog"); m.setAttribute("aria-modal", "true"); m.setAttribute("aria-label", cfg.title);
    m.innerHTML = `<button class="icon-btn mclose" data-close aria-label="Close">${icon.close}</button>
      <div class="pop-grid"><div class="pop-img">${art("frame", "#2B2A28", 77)}</div>
      <form class="pop-body"><h2>${esc(cfg.title)}</h2><p class="muted">${esc(cfg.text)}</p>
        <input type="email" required placeholder="Enter your email" aria-label="Email"><button class="btn primary block">Get 10% off</button>
        <p class="small muted">PLACEHOLDER — connect a newsletter service (e.g. Mailchimp) before launch.</p></form></div>`;
    document.body.appendChild(m);
    m.addEventListener("click", e => { if (e.target.closest("[data-close]")) { closeAll(); store.set("tap_pop", 1); } });
    $("form", m).addEventListener("submit", e => { e.preventDefault(); store.set("tap_pop", 2); $(".pop-body", m).innerHTML = `<h2>You're in!</h2><p>Use code <b class="code">${esc(cfg.code)}</b> at checkout.</p><button class="btn primary block" type="button" data-close>Start shopping</button>`; });
    const tab = document.createElement("button"); tab.className = "side-tab"; tab.innerHTML = `${icon.gift}<span>Special offers for you</span>`; tab.addEventListener("click", () => open(m));
    document.body.appendChild(tab);
    if (!store.get("tap_pop", 0) && document.body.dataset.page !== "cart") setTimeout(() => { if (!$(".drawer.on, .modal.on")) open(m); }, cfg.delaySec * 1000);
  }

  /* ---------------- footer ---------------- */
  function footer() {
    const live = liveCats();
    $("#site-footer").innerHTML = `
      <div class="trust"><div class="wrap trust-in">
        <div>${icon.truck}<span><b>Free shipping</b><small>On orders above ${inr(S.freeShippingAbove)}</small></span></div>
        <div>${icon.lock}<span><b>Secure payments</b><small>UPI, cards, netbanking via Razorpay</small></span></div>
        <div>${icon.spark}<span><b>Made in Pune</b><small>Printed and finished by hand</small></span></div>
        <div>${icon.chat}<span><b>Preview first</b><small>We send a preview before printing</small></span></div>
      </div></div>
      <div class="wrap foot">
        <div class="f-brand"><a class="logo" href="index.html"><img src="assets/img/logo.svg" alt="${S.name} — a unit of The Artful Company" width="378" height="62"></a>
          <p class="muted">${esc(S.tagline)} Designed and 3D-printed in ${esc(S.city)}.</p>
          <div class="f-soc"><a href="${S.social.instagram}" target="_blank" rel="noopener" aria-label="Instagram">${icon.ig}</a><a href="${S.social.youtube}" target="_blank" rel="noopener" aria-label="YouTube">${icon.yt}</a></div>
          <form class="f-news" onsubmit="event.preventDefault();this.innerHTML='<p><b>Thanks — you\\'re on the list.</b></p>'"><input type="email" required placeholder="Your email" aria-label="Email for newsletter"><button class="btn primary">Subscribe</button></form></div>
        <div><h4>Shop</h4>${live.map(c => `<a href="shop.html?cat=${c.id}">${c.name}</a>`).join("")}${hasSale() ? `<a class="hot" href="shop.html?sale=1">On Sale</a>` : ""}</div>
        <div><h4>Help</h4><a href="faq.html">FAQ</a><a href="shipping.html">Shipping policy</a><a href="refunds.html">Cancellations &amp; refunds</a><a href="contact.html">Contact us</a></div>
        <div><h4>Company</h4><a href="about.html">About us</a><a href="organisers.html">For organisers</a><a href="privacy.html">Privacy policy</a><a href="terms.html">Terms &amp; conditions</a></div>
        <div><h4>Contact</h4><a href="https://wa.me/${S.whatsapp}" target="_blank" rel="noopener">WhatsApp ${esc(S.phone)}</a><a href="mailto:${S.email}">${esc(S.email)}</a><span class="muted">${esc(S.city)}</span></div>
      </div>
      <div class="wrap fine"><span>© ${new Date().getFullYear()} ${S.name}. All rights reserved.</span><span class="pay"><i>UPI</i><i>VISA</i><i>Mastercard</i><i>RuPay</i><i>Razorpay</i></span></div>`;
    const top = document.createElement("button"); top.className = "to-top"; top.setAttribute("aria-label", "Back to top"); top.innerHTML = icon.chev;
    top.addEventListener("click", () => scrollTo({ top: 0, behavior: "smooth" })); document.body.appendChild(top);
    addEventListener("scroll", () => top.classList.toggle("on", scrollY > 900), { passive: true });
  }

  /* ---------------- carousels (scroll-snap + arrows) ---------------- */
  function carousels(root = document) {
    $$("[data-carousel]", root).forEach(c => {
      if (c.dataset.wired) return; c.dataset.wired = 1;
      const track = $(".track", c), step = () => track.clientWidth * 0.8;
      $(".prev", c)?.addEventListener("click", () => track.scrollBy({ left: -step(), behavior: "smooth" }));
      $(".next", c)?.addEventListener("click", () => track.scrollBy({ left: step(), behavior: "smooth" }));
    });
  }

  /* ---------------- global clicks ---------------- */
  document.addEventListener("click", e => {
    const w = e.target.closest("[data-wish]"); if (w) { e.preventDefault(); Wish.toggle(w.dataset.wish); return; }
    const qv = e.target.closest("[data-quickview]"); if (qv) { e.preventDefault(); quickView(qv.dataset.quickview); return; }
    const qa = e.target.closest("[data-quickadd]"); if (qa) {
      e.preventDefault(); const p = byId(qa.dataset.quickadd);
      if (p.personal || p.options) { quickView(p.id); return; }
      Cart.add({ id: p.id, qty: 1, colour: p.colours?.[0]?.name || "", hex: p.colours?.[0]?.hex || "", opt: "", optIdx: 0, note: "" }); open($("#cart-drawer")); return;
    }
    const o = e.target.closest("[data-open]"); if (o) { open($(o.dataset.open === "cart" ? "#cart-drawer" : "#menu-drawer")); return; }
    if (e.target.closest(".drawer [data-close]")) closeAll();
  });

  /* ---------------- boot ---------------- */
  window.TAP = { $, $$, inr, esc, param, byId, cat, liveCats, liveSports, hasSale, isBig, featured, store, icon, art, img, unit, purl, priceHtml, stars, Cart, Wish, Recent, card, toast, open, closeAll, buyBox, wireBuyBox, carousels, seedOf };
  document.addEventListener("DOMContentLoaded", () => {
    header(); footer(); cartDrawer(); popup(); refreshCounts();
    const fn = window.TAP_PAGES?.[document.body.dataset.page]; if (fn) fn();
    carousels();
  });
})();
