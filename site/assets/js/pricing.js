/* ==================================================================
   The Artful Products — pricing (shared by the website AND the payment server)
   The server re-calculates every order with this same code, so a customer
   can't change prices in their browser. Edit prices in data.js, not here.
   ================================================================== */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;   // Node (payment server)
  else root.TAP_PRICING = api;                                               // browser
})(typeof self !== "undefined" ? self : this, function () {

  // price of one piece, after quantity tiers and the chosen option's extra cost
  function unit(p, qty, optIdx) {
    qty = qty || 1; optIdx = optIdx || 0;
    let base = p.price || 0;
    if (p.tiers) for (const t of p.tiers) if (qty >= t.min) base = t.price;
    return base + ((p.options && p.options.extra && p.options.extra[optIdx]) || 0);
  }

  // discount rate (0–1) for a code: the flash-sale code while it runs, or any code in SITE.discountCodes
  function discountRate(code, site, now) {
    if (!code) return 0;
    code = String(code).trim().toUpperCase();
    now = now || Date.now();
    const fs = site.flashSale;
    if (fs && fs.active && fs.code && code === String(fs.code).toUpperCase() && now < Date.parse(fs.ends)) return (fs.percent || 10) / 100;
    const extra = (site.discountCodes || {})[code];
    return extra ? extra / 100 : 0;
  }

  // full order: validates every line against the catalogue and returns the totals
  function compute(items, opts, site, products) {
    opts = opts || {};
    const byId = id => products.find(p => p.id === id);
    const lines = [];
    for (const it of items || []) {
      const p = byId(it.id);
      if (!p) throw new Error("Unknown product: " + it.id);
      if ((p.status || "live") !== "live" || !p.price) throw new Error(p.name + " can't be bought online");
      const qty = Math.max(1, Math.min(999, parseInt(it.qty, 10) || 1));
      const nOpt = p.options ? p.options.values.length : 1;
      const optIdx = Math.max(0, Math.min(nOpt - 1, parseInt(it.optIdx, 10) || 0));
      const colours = (p.colours || []).map(c => c.name);
      const u = unit(p, qty, optIdx);
      lines.push({
        id: p.id, name: p.name, qty, optIdx,
        opt: p.options ? p.options.values[optIdx] : "",
        colour: colours.includes(it.colour) ? it.colour : (colours[0] || ""),
        note: String(it.note || "").slice(0, 300),
        unit: u, total: u * qty
      });
    }
    if (!lines.length) throw new Error("The cart is empty");
    const sub = lines.reduce((n, l) => n + l.total, 0);
    const rate = discountRate(opts.code, site);
    const disc = Math.round(sub * rate);
    const physical = lines.some(l => byId(l.id).art !== "giftcard");
    const ship = !physical || sub >= site.freeShippingAbove ? 0 : site.shippingFlat;
    const wrap = opts.wrap ? site.giftWrap : 0;
    return { lines, sub, rate, code: rate ? String(opts.code).trim().toUpperCase() : "", disc, ship, wrap, total: sub - disc + ship + wrap };
  }

  return { unit, discountRate, compute };
});
