# Hand-over: where the project stands (19 Nov 2026)

Read this first when continuing on another computer or in a new Claude session. Technical guide: `README.md`.

## Live
- **https://theartfulproducts.com**, on MilesWeb **mPanel** (not cPanel). Same account hosts theartfulcompany.com /
  theartfulcompany.in in `public_html`, which must never be touched.
- Site folder: `/var/www/2d9a505e-7ba3-4e07-aad5-3f5880073fd8/theartfulproducts.com`.
  Private settings: `/var/www/2d9a505e-…/artful-config.php` (DB, admin password, Razorpay keys, emails). Never in git or chat.
- Server runs **PHP 7.4**: keep PHP code 7.4-compatible (polyfills for `str_starts_with` etc. live in `site/api/_lib.php`).

## How to publish a change
1. Edit (products/prices/contact in `site/assets/js/data.js`; page text in `tools/build_pages.py` / `tools/content_pages.py`).
2. `python tools/build_pages.py` (rebuilds pages, product pages, share images, sitemap, server price list).
3. Commit, then `python tools/publish.py`. It pushes `main`.
4. GitHub Actions (`.github/workflows/deploy.yml`) uploads `site/` by FTP to the site folder within 1–2 minutes.
   (FTP account directory = `/ theartfulproducts.com`; secrets FTP_SERVER / FTP_USERNAME / FTP_PASSWORD are in GitHub.)

## What's built
- **Storefront**: Hyper-style layout, brand logo and colours, video banner (The Great Himalayan), 4 products:
  3D Trail Fridge Magnet, 3D Trail Keychain, Ridge Medal Holder, Terrain Award Frame (real photos + video).
  Pages: home, shop, product pages, cart, wishlist, For Organisers (featured event + bulk form), FAQ, contact,
  About, Shipping / Refunds / Privacy / Terms, 404, **My account**.
- **Payments**: Razorpay (TEST key `rzp_test_U20L0ZHQXXOCAc` in data.js), priced on the server, signature check +
  webhook. Free shipping at **₹1,799+**, else ₹79 (weight-based shipping planned: Soham will send packed weights + rate slabs).
- **Admin** `/admin`: orders (stages, tracking, WhatsApp templates, timeline, archive/restore/delete), + New order
  (website / custom / one-off items), **Customers** (repeat buyers matched by phone OR email, consent, CSV),
  Custom products (admin-only), Enquiries (archive/delete), CSV export.
- **Customer accounts**: passwordless (emailed 6-digit code), order tracking, checkout auto-fill.
- **Email**: orders@theartfulproducts.com via the host's mail (multipart text+HTML). Owner alerts go to soham@theartfulcompany.com.
- Contact: WhatsApp **+91 75881 30344**, orders@theartfulproducts.com.

## Still to do
- [ ] Razorpay KYC as **Sole Proprietor, The Artful Company** (brand: The Artful Products) → then live keys `rzp_live_…`
- [ ] Fill remaining yellow blanks in policies (`tools/content_pages.py`): legal name, registered address, courier, GSTIN
- [ ] Weight-based shipping (needs packed weights + courier rate slabs)
- [ ] Instagram / YouTube links in `data.js`; switch the domain to PHP 8.x in mPanel (recommended)
- [ ] Permission from Inspire India / riders for The Great Himalayan photos
- [ ] Clean up in File Manager: stray `var` folder and unused `deploys` folder in the account root; delete website `theartful-nov-19-2026-1355`
- [ ] Make the GitHub repo private (optional)

## Setting up on a new computer
1. Install **Git** and **Python 3**. Then: `pip install playwright pymupdf pillow` and `python -m playwright install chromium`.
2. `git clone https://github.com/theartfulcameraman-cmd/theartfulproducts.git` and open that folder in Claude.
   (Pushing asks you to sign in to GitHub once.)
3. Preview the shop: `python -m http.server 8130 --directory site` → http://localhost:8130
4. To test the order system locally: PHP 8.x zip from windows.php.net (enable curl, mbstring, openssl, pdo_sqlite,
   pdo_mysql in php.ini) + a local test `artful-config.php` in the project root (mock_razorpay, SQLite, mail_log_dir;
   see README). Run `php -S localhost:8140 -t site`, then `python tools/test_backend.py` (91 checks).
5. Don't work on two computers at once: always `git pull` before starting, and publish before switching.
