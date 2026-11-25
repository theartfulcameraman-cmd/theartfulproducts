/* ==================================================================
   The Artful Products — page renderers (one function per data-page)
   ================================================================== */
(function () {
  const T = () => window.TAP;
  const S = window.SITE, P = window.PRODUCTS, CATS = window.CATEGORIES, SPORTS = window.SPORTS;

  const carouselHtml = (inner, cls = "") => `<div class="carousel ${cls}" data-carousel>
      <button class="cbtn prev" aria-label="Previous">${T().icon.left}</button><div class="track">${inner}</div><button class="cbtn next" aria-label="Next">${T().icon.right}</button></div>`;
  const crumbs = list => `<nav class="crumbs" aria-label="Breadcrumb">${list.map(([l, h]) => h ? `<a href="${h}">${T().esc(l)}</a>` : `<span>${T().esc(l)}</span>`).join("<i>/</i>")}</nav>`;
  const recentBlock = (exclude) => {
    const { Recent, byId, card } = T(); const ids = Recent.ids().filter(id => id !== exclude);
    return ids.length ? `<section class="sec"><div class="wrap"><div class="sec-head"><h2>Recently viewed</h2></div>${carouselHtml(ids.map(id => card(byId(id))).join(""))}</div></section>` : "";
  };

  /* ================= HOME =================
     Sections show themselves only when there is content for them,
     so the page stays clean with a small catalogue and fills out as it grows. */
  function home() {
    const { $, $$, art, card, esc, byId, img, priceHtml, stars, seedOf, buyBox, wireBuyBox, carousels, liveCats, liveSports, isBig, featured } = T();
    const live = liveCats(), hide = sel => $(sel)?.remove();

    // category circles — only worth showing with 3+ categories
    if (S.showCategoryIcons && live.length >= 3) {
      $("#circles").innerHTML = `<div class="circ-row">` +
        `<a class="circ" href="shop.html"><span class="txt">All</span><b>All products</b></a>` +
        live.map(c => `<a class="circ" href="shop.html?cat=${c.id}"><span>${art(c.art, "#2B2A28", seedOf(c.id))}</span><b>${c.name}</b></a>`).join("") +
        `<a class="circ" href="organisers.html"><span>${art("trophy", "#5A3E2B", 12)}</span><b>For Organisers</b></a></div>`;
    } else hide("#circles-sec");

    // hero slideshow — one slide per category (max 3) + organisers
    const bgs = ["#FFF4D1", "#FDE6D6", "#F4F1EC", "#FBE1DE"];
    const slides = live.slice(0, 3).map((c, i) => {
      const p = P.find(x => x.cat === c.id && x.best) || P.find(x => x.cat === c.id);
      return { k: c.name, h: p.name, p: p.short, cta: `Shop ${c.name}`, href: `shop.html?cat=${c.id}`, art: [p.art, p.colours?.[0]?.hex || "#2B2A28"], prod: p, bg: bgs[i] };
    });
    slides.push({ k: "For organisers", h: "Finisher gifts in bulk", p: "Course-map keepsakes for every finisher, branded for your event.", cta: "Get a quote", href: "organisers.html", art: ["trophy", "#5A3E2B"], bg: bgs[3] });
    // optional video slide first (SITE.heroFeature in data.js)
    const hf = S.heroFeature;
    if (hf?.active && hf.video) slides.unshift({ k: hf.kicker, h: hf.title, p: hf.text, cta: hf.cta, href: hf.href, video: hf.video, bg: "#111" });
    $("#hero").innerHTML = `<div class="slides">${slides.map((s, i) => `
        <div class="slide ${i ? "" : "on"} ${s.video ? "vid" : ""}" style="--bg:${s.bg}" aria-hidden="${i ? "true" : "false"}">
          <div class="slide-art">${s.video ? `<video src="${esc(s.video)}" poster="${esc(s.video.replace(/\.mp4$/, ".jpg"))}" autoplay muted loop playsinline aria-hidden="true"></video>` : s.prod?.images?.length ? img(s.prod) : art(s.art[0], s.art[1], 40 + i, 0, s.bg)}</div>
          <div class="slide-txt"><span class="kick">${esc(s.k)}</span><h2>${esc(s.h)}</h2><p>${esc(s.p)}</p><a class="btn light" href="${s.href}" tabindex="${i ? -1 : 0}">${esc(s.cta)}</a></div>
        </div>`).join("")}</div>
      ${slides.length > 1 ? `<div class="sl-ctrl"><button class="prev" aria-label="Previous slide">${T().icon.left}</button>${slides.map((_, i) => `<button class="d ${i ? "" : "on"}" data-i="${i}" aria-label="Slide ${i + 1}"></button>`).join("")}<button class="next" aria-label="Next slide">${T().icon.right}</button></div>` : ""}`;
    let si = 0, timer;
    const go = n => { const ss = $$(".slide"), ds = $$(".sl-ctrl .d"); ss[si].classList.remove("on"); ss[si].setAttribute("aria-hidden", "true"); ds[si].classList.remove("on"); $("a", ss[si]).tabIndex = -1;
      si = (n + ss.length) % ss.length; ss[si].classList.add("on"); ss[si].setAttribute("aria-hidden", "false"); ds[si].classList.add("on"); $("a", ss[si]).tabIndex = 0; };
    const auto = () => { clearInterval(timer); timer = setInterval(() => go(si + 1), 6000); };
    $("#hero").addEventListener("click", e => { const b = e.target.closest(".sl-ctrl button"); if (!b) return; b.classList.contains("prev") ? go(si - 1) : b.classList.contains("next") ? go(si + 1) : go(+b.dataset.i); auto(); });
    if (slides.length > 1) auto();

    // products — a simple grid while the shop is small, tabbed carousels once it grows
    if (!isBig()) {
      $("#tabbed .sec-head h2").textContent = "Our products";
      $("#tabbed .tab-nav").remove();
      $("#tabbed .tab-body").innerHTML = `<div class="grid">${P.map(p => card(p)).join("")}</div>`;
    } else {
      const tabs = { "New Arrivals": P.filter(p => p.isNew), "Best Sellers": P.filter(p => p.best), "On Sale": P.filter(p => p.compareAt) };
      Object.keys(tabs).forEach(k => { if (!tabs[k].length) delete tabs[k]; });
      const drawTab = name => { $("#tabbed .tab-body").innerHTML = carouselHtml(tabs[name].map(p => card(p)).join("")); carousels($("#tabbed")); };
      $("#tabbed .tab-nav").innerHTML = Object.keys(tabs).map((k, i) => `<button class="${i ? "" : "on"}" data-tab="${k}">${k}</button>`).join("");
      $("#tabbed .tab-nav").addEventListener("click", e => { const b = e.target.closest("[data-tab]"); if (!b) return; $$("#tabbed .tab-nav button").forEach(x => x.classList.toggle("on", x === b)); drawTab(b.dataset.tab); });
      drawTab(Object.keys(tabs)[0]);
    }

    // flash sale countdown — only when switched on in data.js
    const fs = S.flashSale, fEl = $("#flash");
    if (fs?.active && new Date(fs.ends) > new Date()) {
      fEl.innerHTML = `<div class="wrap"><div class="flash-in"><b class="f-title">${esc(fs.title)} is on!</b>
        <div class="count" aria-label="Time left">${["Days", "Hrs", "Min", "Sec"].map(l => `<span><b data-u="${l}">00</b><small>${l}</small></span>`).join("<i>:</i>")}</div>
        <p>${esc(fs.text)}</p><button class="btn primary" data-copy="${esc(fs.code)}">Use code: ${esc(fs.code)}</button></div></div>`;
      const end = new Date(fs.ends).getTime();
      const tick = () => { let s = Math.max(0, Math.floor((end - Date.now()) / 1000)); const v = { Days: Math.floor(s / 86400), Hrs: Math.floor(s / 3600) % 24, Min: Math.floor(s / 60) % 60, Sec: s % 60 };
        for (const k in v) $(`[data-u="${k}"]`, fEl).textContent = String(v[k]).padStart(2, "0"); };
      tick(); setInterval(tick, 1000);
      fEl.addEventListener("click", e => { const b = e.target.closest("[data-copy]"); if (!b) return; navigator.clipboard?.writeText(b.dataset.copy).catch(() => {}); T().toast(`Code ${b.dataset.copy} copied`); });
    } else fEl.remove();

    // shop by category tiles — once there are 4+ categories
    if (live.length >= 4) {
      $("#catgrid").innerHTML = live.map(c => { const n = P.filter(p => p.cat === c.id).length; return `
        <a class="ctile" href="shop.html?cat=${c.id}"><span class="ct-img">${art(c.art, "#2B2A28", seedOf(c.id) + 3)}</span><span class="ct-txt"><b>${c.name}</b><small>${n} product${n === 1 ? "" : "s"}</small></span></a>`; }).join("");
    } else hide("#catgrid-sec");

    // favourite product spotlight
    const fp = featured();
    $("#spotlight").innerHTML = `<div class="spot-img" id="spot-img">${img(fp)}</div>
      <div class="spot-info"><span class="kick">Our signature piece</span><h2>${esc(fp.name)}</h2><div class="prate">${stars(fp.rating, fp.reviews)}</div>${priceHtml(fp)}
        <p class="muted">${esc(fp.desc)}</p>${buyBox(fp, "qv")}<a class="link-u" href="${T().purl(fp)}">View full details →</a></div>`;
    wireBuyBox($("#spotlight"), fp);
    document.addEventListener("colour:change", e => { if (e.detail.id === fp.id) $("#spot-img").innerHTML = img(fp, 0, e.detail.hex); });

    // lookbook — hotspots for whichever of these products exist
    const spots = [{ id: "terrain-frame", x: 30, y: 36, sx: 140, sy: 60, w: 330 }, { id: "medal-holder", x: 70, y: 30, sx: 560, sy: 40, w: 300 }, { id: "trail-magnet", x: 73, y: 64, sx: 640, sy: 290, w: 170 }, { id: "route-keychain", x: 36, y: 80, sx: 270, sy: 420, w: 150 }].filter(s => byId(s.id));
    if (spots.length >= 2) {
      $("#lookbook").innerHTML = `<div class="lb-scene">${lookScene(spots)}${spots.map(s => { const p = byId(s.id); return `
          <div class="hs" style="left:${s.x}%;top:${s.y}%"><button aria-label="Show ${esc(p.name)}" aria-expanded="false">+</button>
            <a class="hot-card ${s.x > 55 ? "l" : ""}" href="${T().purl(p)}"><span>${img(p)}</span><span><b>${esc(p.name)}</b>${priceHtml(p)}</span></a></div>`; }).join("")}</div>
        <div class="lb-txt"><span class="kick">Shop the wall</span><h2>A home for everything you've earned</h2><p class="muted">A frame for the big one, a rack for the rest, and your routes on the fridge. Tap the dots to shop.</p><a class="btn primary" href="shop.html">Shop all products</a></div>`;
      $("#lookbook").addEventListener("click", e => { const b = e.target.closest(".hs > button"); if (!b) return; const h = b.parentElement, on = !h.classList.contains("on"); $$("#lookbook .hs").forEach(x => { x.classList.remove("on"); $("button", x).setAttribute("aria-expanded", "false"); }); if (on) { h.classList.add("on"); b.setAttribute("aria-expanded", "true"); } });
    } else hide("#lookbook-sec");

    // shop by sport — once the shop grows
    const sp = $("#sports");
    if (isBig() && liveSports().length > 1) {
      $(".tab-nav", sp).innerHTML = liveSports().map((s, i) => `<button class="${i ? "" : "on"}" data-sp="${s.id}">${s.name}</button>`).join("");
      const drawSport = id => { $(".grid", sp).innerHTML = P.filter(p => p.sports?.includes(id) && p.status === "live").slice(0, 4).map(p => card(p)).join(""); $(".sp-all", sp).href = `shop.html?sport=${id}`; };
      $(".tab-nav", sp).addEventListener("click", e => { const b = e.target.closest("[data-sp]"); if (!b) return; $$(".tab-nav button", sp).forEach(x => x.classList.toggle("on", x === b)); drawSport(b.dataset.sp); });
      drawSport(liveSports()[0].id);
    } else sp.remove();

    // reviews — only when real ones are added in data.js
    const tests = (window.TESTIMONIALS || []).filter(t => t.text);
    if (tests.length) {
      $("#reviews").innerHTML = carouselHtml(tests.map(t => { const p = byId(t.product); return `
        <figure class="tcard"><div class="stars-only">${T().icon.star.repeat(5)}</div><blockquote>“${esc(t.text)}”</blockquote>
          <figcaption><b>${esc(t.name)}</b>${p ? `<a href="${T().purl(p)}"><span>${img(p)}</span>${esc(p.name)}</a>` : ""}</figcaption></figure>`; }).join(""));
    } else hide("#reviews-sec");

    // how it's made
    const steps = [["Your real route", "We rebuild the terrain from elevation data and your own GPX file — not a generic mountain.", "frame", "#2B2A28"], ["Preview before print", "You approve a digital preview on WhatsApp before anything is printed.", "magnet", "#2B2A28"], ["Printed in layers", "Fine layers on our printers in Pune, in matte, durable materials.", "keychain", "#EC683B"], ["Finished by hand", "Each piece is cleaned, checked, framed and packed by hand.", "holder", "#2B2A28"]];
    $("#details").innerHTML = steps.map(([h, p, a, c], i) => `<div class="dcol"><span class="d-img">${art(a, c, 60 + i)}</span><small>0${i + 1}</small><h3>${h}</h3><p class="muted">${p}</p></div>`).join("");

    $("#recent").outerHTML = recentBlock();
  }
  function lookScene(spots) {
    const { art, byId } = T();
    const piece = s => art(byId(s.id).art, "#2B2A28", 5, 0, "transparent").replace("PLACEHOLDER", "").replace("<svg ", `<svg x="${s.sx}" y="${s.sy}" width="${s.w}" height="${s.w}" `);
    return `<svg viewBox="0 0 1000 620" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <rect width="1000" height="620" fill="#E9E3D8"/><rect y="470" width="1000" height="150" fill="#CDBFA8"/>
      <rect x="0" y="465" width="1000" height="10" fill="#B9AA90"/>
      <rect x="600" y="250" width="260" height="215" rx="8" fill="#F4F2EE" stroke="#D6CFC2" stroke-width="3"/>
      ${spots.map(piece).join("")}
      <ellipse cx="300" cy="610" rx="160" ry="14" fill="#000" fill-opacity=".06"/></svg>`;
  }

  /* ================= COLLECTION ================= */
  function shop() {
    const { $, $$, card, esc, param, cat, carousels, liveCats, liveSports, isBig, hasSale } = T();
    const st = { cats: new Set(param("cat") ? [param("cat")] : []), sports: new Set(param("sport") ? [param("sport")] : []), colours: new Set(), avail: new Set(), sale: !!param("sale"), q: (param("q") || "").toLowerCase(), max: 0, sort: "featured" };
    const c1 = st.cats.size === 1 ? cat([...st.cats][0]) : null, sp1 = st.sports.size === 1 ? SPORTS.find(s => s.id === [...st.sports][0]) : null;
    const title = st.q ? `Search: “${param("q")}”` : st.sale ? "On Sale" : c1 ? c1.name : sp1 ? `For ${sp1.name}` : "Shop all";
    document.title = `${title} — ${S.name}`;
    $("#col-head").innerHTML = `${crumbs([["Home", "index.html"], ["Shop", c1 || sp1 || st.sale || st.q ? "shop.html" : null], ...(c1 || sp1 || st.sale || st.q ? [[title]] : [])])}<h1>${esc(title)}</h1><p class="muted">${esc(c1?.blurb || "Everything we make, designed and 3D-printed in Pune.")}</p>`;

    const colourNames = [...new Map(P.flatMap(p => p.colours || []).map(c => [c.name, c])).values()];
    const maxPrice = Math.max(...P.map(p => p.price || 0));
    const box = (group, val, label, n, on) => `<label class="chk"><input type="checkbox" data-g="${group}" value="${val}" ${on ? "checked" : ""}><span>${esc(label)}</span><em>${n}</em></label>`;
    $("#filters").innerHTML = `<div class="f-head only-m"><b>Filter</b><button class="icon-btn" data-fclose aria-label="Close filters">${T().icon.close}</button></div>
      <details open><summary>Category</summary>${liveCats().map(c => box("cats", c.id, c.name, P.filter(p => p.cat === c.id).length, st.cats.has(c.id))).join("")}</details>
      ${liveSports().length ? `<details open><summary>Sport</summary>${liveSports().map(s => box("sports", s.id, s.name, P.filter(p => p.sports?.includes(s.id)).length, st.sports.has(s.id))).join("")}</details>` : ""}
      ${new Set(P.map(p => p.status)).size > 1 ? `<details open><summary>Availability</summary>${[["live", "In stock"], ["quote", "Bulk / on quote"], ["soon", "Coming soon"]].filter(([k]) => P.some(p => p.status === k)).map(([k, l]) => box("avail", k, l, P.filter(p => p.status === k).length)).join("")}</details>` : ""}
      <details open><summary>Price</summary><div class="range"><input type="range" min="0" max="${maxPrice}" step="100" value="${maxPrice}" data-max aria-label="Maximum price"><p>Up to <b data-maxl>${T().inr(maxPrice)}</b></p></div></details>
      <details open><summary>Colour</summary><div class="sw-f">${colourNames.map(c => `<label title="${esc(c.name)}"><input type="checkbox" data-g="colours" value="${esc(c.name)}"><span style="--c:${c.hex}"></span></label>`).join("")}</div></details>
      ${hasSale() ? `<label class="chk tog"><input type="checkbox" data-sale ${st.sale ? "checked" : ""}><span>On sale only</span></label>` : ""}
      <button class="btn ghost block" data-clear>Clear all filters</button>
      <button class="btn primary block only-m" data-fclose>Show results</button>`;
    st.max = maxPrice;

    const draw = () => {
      let list = P.filter(p =>
        (!st.cats.size || st.cats.has(p.cat)) && (!st.sports.size || p.sports?.some(s => st.sports.has(s))) &&
        (!st.avail.size || st.avail.has(p.status)) && (!st.colours.size || p.colours?.some(c => st.colours.has(c.name))) &&
        (!st.sale || p.compareAt) && ((p.price || p.from || 0) <= st.max) &&
        (!st.q || (p.name + " " + p.short + " " + p.desc).toLowerCase().includes(st.q)));
      const pr = p => p.price || p.from || 0;
      if (st.sort === "low") list.sort((a, b) => pr(a) - pr(b));
      if (st.sort === "high") list.sort((a, b) => pr(b) - pr(a));
      if (st.sort === "rating") list.sort((a, b) => (b.rating || 0) - (a.rating || 0));
      if (st.sort === "new") list.sort((a, b) => (b.isNew ? 1 : 0) - (a.isNew ? 1 : 0));
      $("#count").textContent = `${list.length} product${list.length === 1 ? "" : "s"}`;
      $("#grid").innerHTML = list.length ? list.map(p => card(p)).join("") : `<div class="none"><p>No products match these filters.</p><button class="btn" data-clear>Clear filters</button></div>`;
      const chips = [...st.cats].map(v => ["cats", v, cat(v)?.name]).concat([...st.sports].map(v => ["sports", v, SPORTS.find(s => s.id === v)?.name]), [...st.colours].map(v => ["colours", v, v]), [...st.avail].map(v => ["avail", v, { live: "In stock", soon: "Coming soon", quote: "Bulk" }[v]]));
      $("#chips").innerHTML = chips.map(([g, v, l]) => `<button class="chip" data-unset="${g}|${esc(v)}">${esc(l)} ${T().icon.close}</button>`).join("") + (st.sale ? `<button class="chip" data-unsale>On sale ${T().icon.close}</button>` : "");
    };
    const f = $("#filters");
    f.addEventListener("change", e => {
      const t = e.target;
      if (t.dataset.g) t.checked ? st[t.dataset.g].add(t.value) : st[t.dataset.g].delete(t.value);
      if (t.hasAttribute("data-sale")) st.sale = t.checked;
      draw();
    });
    f.addEventListener("input", e => { if (e.target.hasAttribute("data-max")) { st.max = +e.target.value; $("[data-maxl]").textContent = T().inr(st.max); draw(); } });
    document.addEventListener("click", e => {
      if (e.target.closest("[data-clear]")) { ["cats", "sports", "colours", "avail"].forEach(k => st[k].clear()); st.sale = false; st.q = ""; st.max = maxPrice; $$("input[type=checkbox]", f).forEach(i => i.checked = false); $("[data-max]").value = maxPrice; $("[data-maxl]").textContent = T().inr(maxPrice); draw(); }
      const u = e.target.closest("[data-unset]"); if (u) { const [g, v] = u.dataset.unset.split("|"); st[g].delete(v); const i = $(`input[data-g="${g}"][value="${CSS.escape(v)}"]`, f); if (i) i.checked = false; draw(); }
      if (e.target.closest("[data-unsale]")) { st.sale = false; $("[data-sale]").checked = false; draw(); }
      if (e.target.closest("[data-fopen]")) T().open(f);
      if (e.target.closest("[data-fclose]")) T().closeAll();
    });
    $("#sort").addEventListener("change", e => { st.sort = e.target.value; draw(); });
    $$("[data-cols]").forEach(b => b.addEventListener("click", () => { $("#grid").dataset.cols = b.dataset.cols; $$("[data-cols]").forEach(x => x.classList.toggle("on", x === b)); }));
    // Small catalogue: no sidebar, just category pills. The full filter sidebar switches on at 9+ products.
    if (!isBig() && !st.q && !st.sale) {
      $(".col").classList.add("simple");
      $$(".colbtn, [data-fopen]").forEach(b => b.remove());
      const pills = `<a class="pill ${st.cats.size ? "" : "on"}" href="shop.html">All</a>` + liveCats().map(c => `<a class="pill ${st.cats.has(c.id) ? "on" : ""}" href="shop.html?cat=${c.id}">${esc(c.name)}</a>`).join("");
      $(".toolbar").insertAdjacentHTML("afterbegin", `<div class="pills">${pills}</div>`);
    }
    draw();
    const rec = recentBlock(); if (rec) $("#after").innerHTML = rec; carousels();
  }

  /* ================= PRODUCT ================= */
  function product() {
    const { $, $$, esc, inr, param, byId, cat, img, priceHtml, stars, buyBox, wireBuyBox, card, Recent, open } = T();
    const p = byId(param("id") || document.body.dataset.id) || P[0], c = cat(p.cat);
    document.title = `${p.name} — ${S.name}`;
    let hex = p.colours?.[0]?.hex, view = 0;
    const [d0, d1] = S.dispatchDays, add = n => { const d = new Date(); let k = 0; while (k < n) { d.setDate(d.getDate() + 1); if (d.getDay() % 6) k++; } return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" }); };
    const lowStock = p.status === "live" && p.stock && p.stock <= 15;
    // gallery: product photos (or placeholder drawings), plus the product video as the last item if there is one
    const nImg = p.images?.length || 4, nViews = nImg + (p.video ? 1 : 0), isVid = i => !!p.video && i === nImg;
    const poster = () => p.video.replace(/\.mp4$/, ".jpg");
    const slot = i => isVid(i) ? `<video src="${esc(p.video)}" poster="${esc(poster())}" autoplay muted loop playsinline aria-label="${esc(p.name)} video"></video>` : img(p, i, hex);
    const thumb = i => isVid(i) ? `<span class="vth"><img src="${esc(poster())}" alt="" loading="lazy"><b aria-hidden="true">▶</b></span>` : img(p, i, hex);
    $("#pdp").innerHTML =`${crumbs([["Home", "index.html"], [c.name, `shop.html?cat=${c.id}`], [p.name]])}
      <div class="pdp">
        <div class="gal">
          <div class="thumbs" role="tablist">${[...Array(nViews).keys()].map(i => `<button class="th ${i ? "" : "on"}" data-v="${i}" aria-label="${isVid(i) ? "Video" : "Image " + (i + 1)}">${thumb(i)}</button>`).join("")}</div>
          <div class="main" id="main" tabindex="0" aria-label="Product image — hover to zoom">${slot(0)}</div>
        </div>
        <div class="pinfo-l">
          <a class="pcat" href="shop.html?cat=${c.id}">${esc(c.name)}</a>
          <h1>${esc(p.name)}</h1>
          <div class="prate">${stars(p.rating, p.reviews)}${p.reviews ? `<a href="#tabs" class="muted small">${p.reviews} reviews</a>` : ""}</div>
          <div class="pprice">${priceHtml(p)}${p.compareAt ? `<span class="save">Save ${inr(p.compareAt - p.price)}</span>` : ""}</div>
          <p class="muted">${esc(p.short)}</p>
          ${p.sku ? `<p class="psku muted small">SKU <span data-sku>${esc(p.sku + (p.colours?.[0]?.code ? "-" + p.colours[0].code : ""))}</span></p>` : ""}
          ${lowStock ? `<div class="stock"><p>🔥 Hurry — only <b>${p.stock} left</b> in stock</p><i><em style="width:${p.stock / 15 * 100}%"></em></i></div>` : ""}
          ${buyBox(p, "pdp")}
          ${p.status === "live" ? `<ul class="perks"><li>${T().icon.truck}<span>Order today, dispatched by <b>${add(d1)}</b> · estimated delivery ${add(d1 + 2)}–${add(d1 + 5)}</span></li><li>${T().icon.lock}<span>Secure payment by UPI, cards or netbanking</span></li><li>${T().icon.chat}<span>Questions? <a href="https://wa.me/${S.whatsapp}?text=${encodeURIComponent("Hi! A question about " + p.name)}" target="_blank" rel="noopener">WhatsApp us</a></span></li></ul>` : ""}
        </div>
      </div>
      <div class="ptabs" id="tabs">
        <div class="tab-nav" role="tablist">${["Description", "Specifications", "Shipping & returns", ...(p.reviews ? ["Reviews"] : [])].map((t, i) => `<button class="${i ? "" : "on"}" data-pt="${i}" role="tab">${t}</button>`).join("")}</div>
        <div class="pt on"><p>${esc(p.desc)}</p>${p.personal ? `<h3>How personalisation works</h3><ol><li>Add your event, date, name and time when ordering.</li><li>We message you on WhatsApp for your GPX file or Strava link.</li><li>You approve a digital preview, then we print.</li></ol>` : ""}</div>
        <div class="pt"><ul class="spec">${p.specs.map(s => `<li>${esc(s)}</li>`).join("")}</ul></div>
        <div class="pt"><p>Ready-made items dispatch in ${d0}–${d1} working days; personalised pieces take longer (see specifications). Free shipping across India on orders above ${inr(S.freeShippingAbove)}, otherwise ${inr(S.shippingFlat)}.</p><p>If your piece arrives damaged, send us a photo within 48 hours and we'll reprint it free. Personalised items can't be returned.</p></div>
        ${p.reviews ? `<div class="pt"><p class="muted">Rated ${p.rating} / 5 from ${p.reviews} reviews.</p></div>` : ""}
      </div>`;

    // gallery + zoom
    const main = $("#main");
    const show = () => { main.innerHTML = slot(view); main.classList.toggle("is-video", isVid(view)); $$(".th").forEach((t, i) => { t.innerHTML = thumb(i); t.classList.toggle("on", i === view); }); };
    $(".thumbs").addEventListener("click", e => { const b = e.target.closest("[data-v]"); if (b) { view = +b.dataset.v; show(); } });
    main.addEventListener("mousemove", e => { if (isVid(view)) return; const r = main.getBoundingClientRect(); main.style.setProperty("--zx", ((e.clientX - r.left) / r.width * 100) + "%"); main.style.setProperty("--zy", ((e.clientY - r.top) / r.height * 100) + "%"); main.classList.add("zoom"); });
    main.addEventListener("mouseleave", () => main.classList.remove("zoom"));
    document.addEventListener("colour:change", e => { if (e.detail.id === p.id && e.detail.hex !== hex) { hex = e.detail.hex; show(); } });
    document.addEventListener("colour:change", e => { const c = e.detail.id === p.id && p.sku && p.colours?.find(x => x.hex === e.detail.hex), el = $("[data-sku]"); if (c && el) el.textContent = p.sku + (c.code ? "-" + c.code : ""); });
    wireBuyBox($("#pdp"), p);

    // tabs
    $(".ptabs .tab-nav").addEventListener("click", e => { const b = e.target.closest("[data-pt]"); if (!b) return; $$(".ptabs .tab-nav button").forEach(x => x.classList.toggle("on", x === b)); $$(".pt").forEach((x, i) => x.classList.toggle("on", i === +b.dataset.pt)); });

    // sticky add-to-cart bar
    const buy = $("#pdp [data-buy] button[type=submit]");
    if (buy) {
      const bar = document.createElement("div"); bar.className = "sticky-atc";
      bar.innerHTML = `<div class="wrap sa-in"><span class="sa-img">${img(p, 0, hex)}</span><span class="sa-name"><b>${esc(p.name)}</b>${priceHtml(p)}</span><button class="btn primary">Add to cart</button></div>`;
      document.body.appendChild(bar);
      $("button", bar).addEventListener("click", () => buy.click());
      new IntersectionObserver(([en]) => bar.classList.toggle("on", !en.isIntersecting && en.boundingClientRect.top < 0)).observe(buy);
    }

    const rel = P.filter(x => x.id !== p.id && (x.cat === p.cat || x.sports?.some(s => p.sports?.includes(s)))).slice(0, 8);
    $("#related").innerHTML = rel.length ? `<section class="sec"><div class="wrap"><div class="sec-head"><h2>You may also like</h2></div>${carouselHtml(rel.map(x => card(x)).join(""))}</div></section>` : "";
    $("#recent").innerHTML = recentBlock(p.id);
    Recent.push(p.id);
  }

  /* ================= CART ================= */
  function cart() {
    const { $, esc, inr, byId, img, Cart, store, param } = T();
    if (param("paid")) {
      const no = param("order");
      $("#cart").innerHTML = `<div class="done"><h2>Thank you — payment received.</h2>
        ${no ? `<p>Your order number is <b>${esc(no)}</b>. A confirmation email is on its way.</p>` : ""}
        <p class="muted">We'll message you on WhatsApp for your route file and confirm the dispatch date.<br><small>Payment ID ${esc(param("paid"))}</small></p>
        <a class="btn primary" href="shop.html">Keep browsing</a></div>`;
      return;
    }
    let opts = store.get("tap_cartopts", { wrap: false, note: "", code: "" });
    const render = () => {
      const items = Cart.items();
      if (!items.length) { $("#cart").innerHTML = `<div class="done"><p>Your cart is empty.</p><a class="btn primary" href="shop.html">Browse the shop</a></div>`; return; }
      let t;
      try { t = Cart.totals(opts); }
      catch (err) { $("#cart").innerHTML = `<div class="done"><p>${esc(err.message)}. Please remove it from your cart.</p></div>`; return; }
      if (opts.code && !t.code) { opts.code = ""; store.set("tap_cartopts", opts); }   // expired / removed code
      const { sub, disc, ship, wrap, total } = t, left = S.freeShippingAbove - sub;
      $("#cart").innerHTML = `
        <div class="c-lines">
          <div class="ship-bar big"><p>${left > 0 ? `Add <b>${inr(left)}</b> more for <b>free shipping</b>` : `🎉 You've unlocked <b>free shipping</b>`}</p><i><em style="width:${Math.min(100, sub / S.freeShippingAbove * 100)}%"></em></i></div>
          <div class="c-head"><span>Product</span><span>Quantity</span><span>Total</span></div>
          ${items.map((i, n) => { const p = byId(i.id); return `
          <div class="c-line">
            <a class="cl-img" href="${T().purl(p)}">${img(p, 0, i.hex)}</a>
            <div class="cl-info"><a href="${T().purl(p)}"><b>${esc(p.name)}</b></a><span class="muted">${[i.colour, i.opt].filter(Boolean).map(esc).join(" · ")}</span>${i.note ? `<span class="note">“${esc(i.note)}”</span>` : ""}<span class="muted small">${inr(T().unit(p, i.qty, i.optIdx || 0))} each</span><button class="link" data-rm="${n}">Remove</button></div>
            <div class="qty sm"><button data-d="-1" data-n="${n}" aria-label="Fewer">−</button><span>${i.qty}</span><button data-d="1" data-n="${n}" aria-label="More">+</button></div>
            <b class="cl-total">${inr(Cart.line(i))}</b>
          </div>`; }).join("")}
          <label class="chk tog wrap-opt"><input type="checkbox" data-wrap ${opts.wrap ? "checked" : ""}><span>${T().icon.gift} Add gift wrap and a handwritten note (+${inr(S.giftWrap)})</span></label>
          <label class="fld">Order note<textarea data-note rows="2" placeholder="Anything we should know? Delivery instructions, gift message…">${esc(opts.note)}</textarea></label>
        </div>
        <aside class="c-sum">
          <h3>Order summary</h3>
          <form class="codeform" data-code><input placeholder="Discount code" value="${esc(opts.code)}" aria-label="Discount code"><button class="btn">Apply</button></form>
          <div class="sum-row"><span>Subtotal</span><span>${inr(sub)}</span></div>
          ${disc ? `<div class="sum-row good"><span>Discount (${esc(opts.code)})</span><span>−${inr(disc)}</span></div>` : ""}
          <div class="sum-row"><span>Shipping</span><span>${ship ? inr(ship) : "Free"}</span></div>
          ${wrap ? `<div class="sum-row"><span>Gift wrap</span><span>${inr(wrap)}</span></div>` : ""}
          <div class="sum-row total"><span>Total</span><span>${inr(total)}</span></div>
          <form id="checkout" class="checkout">
            <h3>Delivery details</h3>
            <input name="name" placeholder="Full name" required autocomplete="name">
            <div class="row"><input name="phone" placeholder="Mobile" required inputmode="tel" autocomplete="tel"><input name="email" type="email" placeholder="Email" required autocomplete="email"></div>
            <textarea name="address" rows="2" placeholder="House, street, area" required autocomplete="street-address"></textarea>
            <div class="row"><input name="city" placeholder="City" required autocomplete="address-level2"><input name="pin" placeholder="PIN code" required inputmode="numeric" pattern="[0-9]{6}" autocomplete="postal-code"></div>
            <label class="chk consent"><input type="checkbox" name="marketing" value="1"><span>Send me new products and offers on WhatsApp / email. You can opt out any time.</span></label>
            <p class="muted small acct-hint" data-acct-hint><a href="account.html">Log in</a> to fill in your details from your last order.</p>
            <button class="btn primary block" type="submit">Pay ${inr(total)} securely</button>
            <p class="pay-note">${T().icon.lock}<span>Payments by Razorpay · UPI · Cards · Netbanking · Wallets</span></p>
            <p class="status" id="pay-status" hidden></p>
          </form>
        </aside>`;
      const c = $("#cart");
      c.onclick = e => {
        const it = Cart.items(), rm = e.target.closest("[data-rm]"), d = e.target.closest("[data-d]");
        if (rm) { it.splice(+rm.dataset.rm, 1); Cart.save(it); }
        if (d) { const x = it[+d.dataset.n]; x.qty = Math.max(1, x.qty + +d.dataset.d); Cart.save(x ? it : it); }
      };
      $("[data-wrap]", c).onchange = e => { opts.wrap = e.target.checked; store.set("tap_cartopts", opts); render(); };
      $("[data-note]", c).oninput = e => { opts.note = e.target.value; store.set("tap_cartopts", opts); };
      $("[data-code]", c).onsubmit = e => { e.preventDefault(); const v = $("input", e.target).value.trim().toUpperCase(); if (v && !window.TAP_PRICING.discountRate(v, S)) { T().toast("That code isn't valid"); return; } opts.code = v; store.set("tap_cartopts", opts); render(); if (v) T().toast("Code applied"); };
      $("#checkout").onsubmit = e => { e.preventDefault(); pay(Object.fromEntries(new FormData(e.target)), { ...t, items, opts }, e.target); };
      // logged-in customers: fill empty delivery fields from their last order
      profile.then(p => {
        const f = $("#checkout"); if (!f) return;
        const hint = $("[data-acct-hint]", f);
        if (!p) return;
        if (hint) hint.textContent = "Details filled in from your account.";
        ["name", "phone", "email", "address", "city", "pin"].forEach(k => { if (f[k] && !f[k].value && p[k]) f[k].value = p[k]; });
      });
    };
    const profile = (window.TAP_ACCOUNT ? window.TAP_ACCOUNT("me") : Promise.reject())
      .then(r => r.ok ? r.data.profile || null : null).catch(() => null);
    document.addEventListener("cart:change", render);
    render();
  }

  function orderText(d, o) {
    const { inr } = T();
    return `New order — ${S.name}\n\n` + o.lines.map(l => `• ${l.name}${[l.colour, l.opt].filter(Boolean).length ? " (" + [l.colour, l.opt].filter(Boolean).join(", ") + ")" : ""} × ${l.qty} — ${inr(l.total)}${l.note ? "\n   Details: " + l.note : ""}`).join("\n") +
      `\n\nSubtotal: ${inr(o.sub)}${o.disc ? `\nDiscount (${o.code}): −${inr(o.disc)}` : ""}\nShipping: ${o.ship ? inr(o.ship) : "Free"}${o.wrap ? `\nGift wrap: ${inr(o.wrap)}` : ""}\nTotal: ${inr(o.total)}` +
      `${o.opts.note ? `\n\nNote: ${o.opts.note}` : ""}\n\n${d.name}\n${d.phone} · ${d.email}\n${d.address}, ${d.city} ${d.pin}`;
  }
  /* Payment flow:
     1. the payment server (netlify/functions/create-order) re-prices the cart and creates a Razorpay order
     2. Razorpay Checkout takes the payment (UPI / cards / netbanking / wallets)
     3. the server (verify-payment) checks Razorpay's signature before we show "payment received"
     Until the Key ID is set, or if anything fails, the order can be sent on WhatsApp instead. */
  async function pay(d, o, form) {
    const { $, Cart, store, esc } = T(), st = $("#pay-status"), btn = $("button[type=submit]", form);
    const say = h => { st.hidden = false; st.innerHTML = h; };
    const wa = `https://wa.me/${S.whatsapp}?text=${encodeURIComponent(orderText(d, o))}`;
    const fallback = why => say(`${why} <a href="${wa}" target="_blank" rel="noopener">Send this order on WhatsApp</a> and we'll share a payment link.`);
    if (!S.razorpayKey || !S.razorpayOrderEndpoint) { fallback("Online payments are being set up."); return; }
    const post = (url, body) => fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
      .then(async r => { const j = await r.json().catch(() => ({})); if (!r.ok) throw new Error(j.error || "Server error"); return j; });
    const busy = on => { btn.disabled = on; btn.textContent = on ? "Opening secure payment…" : `Pay ${T().inr(o.total)} securely`; };
    busy(true);
    try {
      if (!window.Razorpay) await new Promise((ok, no) => { const s = document.createElement("script"); s.src = "https://checkout.razorpay.com/v1/checkout.js"; s.onload = ok; s.onerror = no; document.head.appendChild(s); });
      const order = await post(S.razorpayOrderEndpoint, { items: o.items, code: o.opts.code, wrap: o.opts.wrap, note: o.opts.note, customer: d, marketing: !!d.marketing });
      busy(false);
      new window.Razorpay({
        key: order.key || S.razorpayKey, amount: order.amount, currency: order.currency || "INR", order_id: order.id,
        name: S.name, description: o.lines.map(l => l.name).join(", ").slice(0, 250),
        prefill: { name: d.name, email: d.email, contact: d.phone },
        theme: { color: "#EC683B" },
        modal: { ondismiss: () => say("Payment cancelled. Your cart is saved — you can try again any time.") },
        handler: async r => {
          say("Confirming your payment…");
          try {
            const v = await post(S.razorpayVerifyEndpoint, r);
            Cart.save([]); store.set("tap_cartopts", { wrap: false, note: "", code: "" });
            const no = v.order_no || order.order_no || "";
            location.href = `cart.html?paid=${encodeURIComponent(r.razorpay_payment_id)}${no ? "&order=" + encodeURIComponent(no) : ""}`;
          } catch {
            say(`We received a payment response but couldn't confirm it. Please don't pay again — WhatsApp us with payment ID <b>${esc(r.razorpay_payment_id)}</b> and we'll check it right away.`);
          }
        }
      }).open();
    } catch (err) { busy(false); fallback(`Couldn't start the payment (${esc(err.message)}).`); }
  }

  /* ================= WISHLIST ================= */
  function wishlist() {
    const { $, Wish, byId, card } = T();
    const draw = () => { const ids = Wish.ids(); $("#wish").innerHTML = ids.length ? `<div class="grid">${ids.map(id => card(byId(id))).join("")}</div>` : `<div class="done"><p>Nothing saved yet. Tap the ♡ on any product to save it here.</p><a class="btn primary" href="shop.html">Browse the shop</a></div>`; };
    draw(); document.addEventListener("click", e => { if (e.target.closest("[data-wish]")) setTimeout(draw, 0); });
  }

  /* Saves organiser / contact enquiries to the admin dashboard (api/enquiry.php) in the background,
     while WhatsApp / email still opens for the customer. Fails silently if the server isn't there. */
  function saveEnquiry(kind, data, honeypot) {
    try {
      fetch("api/enquiry.php", { method: "POST", keepalive: true, headers: { "Content-Type": "application/json" }, body: JSON.stringify({ kind, data, website: honeypot || "" }) }).catch(() => {});
    } catch {}
  }

  /* ================= ORGANISERS ================= */
  function org() {
    const { $, art, byId, esc } = T();
    if (!$("#org-art").children.length) $("#org-art").innerHTML = art("trophy", "#5A3E2B", 12, 0, "#E9E3D8");
    document.querySelectorAll("[data-wa]").forEach(a => { a.href = `https://wa.me/${S.whatsapp}?text=${encodeURIComponent("Hi! I'd like a quote for my event.")}`; a.target = "_blank"; a.rel = "noopener"; });
    const pre = T().param("product"); if (pre) { const b = $(`input[name="want"][value="${pre}"]`); if (b) b.checked = true; }
    $("#org-form").addEventListener("submit", e => {
      e.preventDefault();
      const f = new FormData(e.target), want = f.getAll("want").map(id => byId(id)?.name || id).join(", ") || "Not sure yet";
      const msg = `Bulk enquiry — ${S.name}\n\nOrganisation: ${f.get("org")}\nEvent: ${f.get("event")}\nDate: ${f.get("date") || "-"}\nParticipants: ${f.get("count") || "-"}\nInterested in: ${want}\nBudget per piece: ${f.get("budget") || "-"}\n\n${f.get("notes") || ""}\n\nContact: ${f.get("name")}, ${f.get("phone")}, ${f.get("email")}`;
      saveEnquiry("organiser", { name: f.get("name"), phone: f.get("phone"), email: f.get("email"), organisation: f.get("org"), event: f.get("event"), date: f.get("date"), participants: f.get("count"), interested: want, budget: f.get("budget"), notes: f.get("notes") }, f.get("website"));
      if (e.submitter?.value === "email") location.href = `mailto:${S.email}?subject=${encodeURIComponent("Bulk enquiry: " + f.get("event"))}&body=${encodeURIComponent(msg)}`;
      else window.open(`https://wa.me/${S.whatsapp}?text=${encodeURIComponent(msg)}`, "_blank", "noopener");
    });
  }

  /* ================= FAQ ================= */
  function faq() {
    const { $, esc } = T(), ids = { 2: "shipping", 5: "returns" };
    $("#faq").innerHTML = window.FAQ.map(([q, a], i) => `<details ${ids[i] ? `id="${ids[i]}"` : ""} ${i ? "" : "open"}><summary>${esc(q)}</summary><p>${esc(a)}</p></details>`).join("");
    const h = location.hash && document.querySelector(location.hash); if (h?.tagName === "DETAILS") h.open = true;
  }

  /* ================= CONTACT ================= */
  function contact() {
    const { $ } = T();
    $("#c-wa").href = `https://wa.me/${S.whatsapp}`; $("#c-wa").textContent = S.phone;
    $("#c-mail").href = `mailto:${S.email}`; $("#c-mail").textContent = S.email;
    $("#contact-form").addEventListener("submit", e => {
      e.preventDefault(); const f = new FormData(e.target);
      const msg = `Hi, I'm ${f.get("name")} (${f.get("email")}${f.get("phone") ? ", " + f.get("phone") : ""}).\n\n${f.get("msg")}`;
      saveEnquiry("contact", { name: f.get("name"), phone: f.get("phone"), email: f.get("email"), topic: f.get("topic"), message: f.get("msg") }, f.get("website"));
      if (e.submitter?.value === "email") location.href = `mailto:${S.email}?subject=${encodeURIComponent(f.get("topic"))}&body=${encodeURIComponent(msg)}`;
      else window.open(`https://wa.me/${S.whatsapp}?text=${encodeURIComponent(f.get("topic") + "\n\n" + msg)}`, "_blank", "noopener");
    });
  }

  /* ================= MY ACCOUNT (passwordless: email → 6-digit code) ================= */
  const accountApi = (action, data) => fetch("api/account.php", { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action, ...(data || {}) }) })
    .then(async r => ({ ok: r.ok, status: r.status, data: await r.json().catch(() => ({})) }));

  function account() {
    const { $, esc, inr } = T(), box = $("#acct");
    const STEPS = [["paid", "Order placed"], ["preview_sent", "Preview"], ["printing", "Making"], ["shipped", "Shipped"], ["delivered", "Delivered"]];
    const RANK = { new: 0, awaiting_route: 0, preview_sent: 1, approved: 1, printing: 2, packed: 2, shipped: 3, delivered: 4 };

    const showLogin = (msg) => {
      box.innerHTML = `<div class="acct-login">
        <h1>My account</h1>
        <p class="muted">See your orders and their status. No password needed: we'll email you a 6-digit code.</p>
        <form id="acct-email" class="acct-form">
          <label class="fld">Email you ordered with<input type="email" name="email" required autocomplete="email" placeholder="you@example.com"></label>
          <button class="btn primary block">Email me a code</button>
        </form>
        <form id="acct-code" class="acct-form" hidden>
          <p>We sent a code to <b data-email></b>. It works for 10 minutes. Check spam if you don't see it.</p>
          <label class="fld">6-digit code<input name="code" inputmode="numeric" autocomplete="one-time-code" maxlength="6" pattern="[0-9]{6}" required placeholder="123456"></label>
          <button class="btn primary block">Log in</button>
          <button type="button" class="link" data-back>Use a different email</button>
        </form>
        <p class="status" id="acct-msg" ${msg ? "" : "hidden"}>${msg ? esc(msg) : ""}</p>
      </div>`;
      const say = m => { const s = $("#acct-msg"); s.hidden = !m; s.textContent = m || ""; };
      let email = "";
      $("#acct-email").onsubmit = async e => {
        e.preventDefault(); email = e.target.email.value.trim(); say("");
        const btn = $("button", e.target); btn.disabled = true;
        const r = await accountApi("request_code", { email }).catch(() => ({ ok: false, data: {} }));
        btn.disabled = false;
        if (!r.ok) { say(r.data.error || "Couldn't send the code. Please try again."); return; }
        e.target.hidden = true; $("#acct-code").hidden = false; $("[data-email]").textContent = email; $("#acct-code").code.focus();
      };
      $("#acct-code").onsubmit = async e => {
        e.preventDefault(); say("");
        const r = await accountApi("verify_code", { email, code: e.target.code.value.trim() }).catch(() => ({ ok: false, data: {} }));
        if (!r.ok) { say(r.data.error || "Couldn't log in. Please try again."); return; }
        showAccount(r.data);
      };
      $("[data-back]").onclick = () => { $("#acct-code").hidden = true; $("#acct-email").hidden = false; say(""); };
    };

    const showAccount = (d) => {
      const p = d.profile || {}, first = (p.name || "").split(" ")[0];
      const orderCard = o => {
        const rank = o.stage === "cancelled" ? -1 : (RANK[o.stage] ?? 0);
        return `<article class="acct-order">
          <header><div><b>${esc(o.order_no)}</b><span class="muted small">${esc(new Date(o.date.replace(" ", "T")).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }))}</span></div>
            <div class="acct-status ${o.stage === "cancelled" ? "x" : ""}">${esc(o.stage_label)}</div></header>
          ${o.stage === "cancelled" ? "" : `<ol class="acct-steps">${STEPS.map(([, label], i) => `<li class="${i <= rank ? "reached" : ""}">${label}</li>`).join("")}</ol>`}
          ${o.stage === "awaiting_route" ? `<p class="acct-note">Next step: send us your route (GPX file, Strava link or event name). <a href="https://wa.me/${S.whatsapp}?text=${encodeURIComponent("Hi! Here is the route for my order " + o.order_no + ":")}" target="_blank" rel="noopener">Send it on WhatsApp →</a></p>` : ""}
          <ul class="acct-items">${o.items.map(i => `<li><span>${esc(i.name)} ×${i.qty}${[i.colour, i.opt].filter(Boolean).length ? ` <span class="muted">· ${esc([i.colour, i.opt].filter(Boolean).join(" · "))}</span>` : ""}${i.note ? `<br><span class="muted small">“${esc(i.note)}”</span>` : ""}</span></li>`).join("")}</ul>
          <footer><b>${inr(o.total)}</b>
            ${o.tracking_url ? `<a class="btn primary sm" href="${esc(o.tracking_url)}" target="_blank" rel="noopener">Track parcel</a>` : o.tracking_no ? `<span class="muted small">${esc(o.courier)} · ${esc(o.tracking_no)}</span>` : ""}
          </footer></article>`;
      };
      box.innerHTML = `<div class="acct-head"><div><h1>${first ? `Hi ${esc(first)}` : "My account"}</h1><p class="muted">${esc(d.email)}</p></div>
          <button class="btn ghost sm" data-logout>Log out</button></div>
        <div class="acct-grid">
          <section><h2>My orders</h2>
            ${d.orders.length ? d.orders.map(orderCard).join("") : `<div class="acct-empty"><p>No orders with this email yet.</p><a class="btn primary" href="shop.html">Browse the shop</a></div>`}
          </section>
          <aside class="acct-side">
            ${p.name ? `<div class="acct-card"><h3>Delivery details</h3><p>${esc(p.name)}<br>${esc(p.address)}<br>${esc(p.city)} ${esc(p.pin)}<br>${esc(p.phone)}</p><p class="muted small">Filled in for you at checkout.</p></div>` : ""}
            <div class="acct-card"><h3>Need help with an order?</h3><p class="muted small">Message us with your order number.</p>
              <a class="btn ghost sm" href="https://wa.me/${S.whatsapp}" target="_blank" rel="noopener">WhatsApp us</a></div>
          </aside>
        </div>`;
      $("[data-logout]").onclick = async () => { await accountApi("logout").catch(() => {}); showLogin("You're logged out."); };
    };

    box.innerHTML = `<p class="muted">Loading…</p>`;
    accountApi("me").then(r => r.ok ? showAccount(r.data) : showLogin()).catch(() => showLogin());
  }
  window.TAP_ACCOUNT = accountApi;

  window.TAP_PAGES = { home, shop, product, cart, wishlist, org, faq, contact, account };
})();
