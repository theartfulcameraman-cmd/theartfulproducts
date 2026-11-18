# Hand-over: where the project stands (18 Nov 2026)

Read this first when continuing on another computer or in a new Claude session.
Full technical guide: `README.md`.

## What's built
- **Website** (`site/`): Hyper-style storefront in The Artful Products brand (logo + yellow→red "A" gradient).
  4 real products with placeholder drawings: 3D Trail Fridge Magnet, 3D Trail Keychain, Ridge Medal Holder,
  Terrain Award Frame. Menu: Shop all · 3D Trail Fridge Magnets · 3D Trail Keychains · Terrain Frames ·
  Medal Display · For Organisers. About is in the footer only. Sections/filters appear automatically as products grow.
- **Pages**: home, shop, product pages (`product-<id>.html`, with share images + Google data), cart/checkout,
  wishlist, For Organisers (bulk quote form), FAQ, contact, About, Shipping / Refunds / Privacy / Terms, 404.
- **Payments**: Razorpay, priced on the server (`site/api/*.php`), signature-checked, plus a webhook backup.
- **Admin** (`/admin`): orders dashboard, order detail (stages, tracking, WhatsApp templates, timeline),
  manual orders, **custom products** (admin-only, never on the website), enquiries, CSV export, emails.
- **Hosting**: MilesWeb (cPanel). GitHub repo `theartfulcameraman-cmd/theartfulproducts` is connected in
  cPanel → Git Version Control. `.cpanel.yml` copies `site/` → `public_html`.

## Not done yet / waiting on Soham
- [ ] `.cpanel.yml`: replace `CPANEL_USER` with the cPanel username (from the repo path `/home/<user>/…`)
- [ ] MilesWeb one-time setup (README → "Order system → One-time setup"): MySQL database, `orders@` mailbox,
      `/home/<user>/artful-config.php` with Razorpay keys + DB + admin password, Razorpay webhook
- [ ] Razorpay account + test keys → put Key ID in `site/assets/js/data.js` → `razorpayKey`
- [ ] Domain: set `SITE_URL` in `tools/build_pages.py`, rebuild; then un-comment the HTTPS lines in `site/.htaccess`
- [ ] Real product photos, final prices, colours (see launch checklist), WhatsApp number, email, social links in `data.js`
- [ ] Fill the yellow blanks in the policy pages (`tools/content_pages.py`)
- [ ] Consider making the GitHub repo **private** (Settings → General → Danger Zone → Change visibility)

## Setting up on a new computer
1. Install **Git** and **Python 3** (python.org). Then: `pip install playwright pymupdf` and `python -m playwright install chromium`.
2. `git clone https://github.com/theartfulcameraman-cmd/theartfulproducts.git` and open that folder in Claude.
3. Preview the shop: `python -m http.server 8130 --directory site` → http://localhost:8130
4. After changing products/prices/text: `python tools/build_pages.py` (rebuilds pages, share images, sitemap, server price list).
5. To test the order system locally you also need PHP 8.3 (windows.php.net, x64 non-thread-safe zip) and a local
   test `artful-config.php` in the project root (mock Razorpay + SQLite) — see README → "Testing changes locally".
   Then `python tools/test_backend.py` (52 checks).
6. Publish: commit, `git push`, then cPanel → Git Version Control → **Update from Remote** → **Deploy HEAD Commit**.

Not in GitHub on purpose: the local test config and database, the printable launch checklist (PDF/MD), the PHP tools.
