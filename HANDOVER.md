# Hand-over: where the project stands (25 Nov 2026)

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
  Orders list: **All** tab first and default; **To do** = every unshipped order, marked Paid / Not paid.
  Payment status **Advance paid**: enter the advance amount, balance due is shown live (new order + order detail).
- **SKUs**: `TAP-<category>-<product>-<colour>` (e.g. `TAP-FRM-TER-OAK`), custom products `TAP-CUS-<cat>-<n>`,
  one-off items `TAP-ONEOFF`. Each product in `data.js` has a `sku` (3-letter codes); rules in `site/api/_lib.php`.
  Shown in admin, CSV export, product pages and Google product data.
- **Instagram auto-posting** (free, Graph API): schedule posts in `social/queue.json` (image / carousel / reel,
  India time, `"hold": true` to pause); media in `site/social/`. GitHub job `.github/workflows/instagram.yml`
  runs every 15 min and records posts in `social/posted.json`. Guide: `social/README.md`.
  Check a queue with `python tools/ig_publish.py --check`; tests: `python tools/test_ig_publish.py` (27 checks).
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
- [ ] Instagram: Meta setup (professional account, Facebook Page, developer app, Page token) and GitHub secrets
      `IG_PAGE_TOKEN` + `IG_USER_ID` (steps in `social/README.md`); then add posts to `social/queue.json`
- [ ] Make the GitHub repo private (optional)

## Setting up on a new computer
1. Install **Git** and **Python 3**. Then: `pip install playwright pymupdf pillow` and `python -m playwright install chromium`.
2. `git clone https://github.com/theartfulcameraman-cmd/theartfulproducts.git` and open that folder in Claude.
   (Pushing asks you to sign in to GitHub once.)
3. Preview the shop: `python -m http.server 8130 --directory site` → http://localhost:8130
4. To test the order system locally: PHP 8.x zip from windows.php.net (enable curl, mbstring, openssl, pdo_sqlite,
   pdo_mysql in php.ini) + a local test `artful-config.php` in the project root (mock_razorpay, SQLite, mail_log_dir;
   see README). Run `php -S localhost:8140 -t site`, then `python tools/test_backend.py` (105 checks).
   Delete `.local/test.sqlite` and `.local/mail` first: data left from an earlier run makes a Customers check fail.
   On Windows, run Python tests with `PYTHONIOENCODING=utf-8` (the console can't print "→" otherwise).
5. Don't work on two computers at once: always `git pull` before starting, and publish before switching.
6. Each computer draws the share images (`site/assets/img/og/*.png`) slightly differently. If you didn't change a
   product, undo them after a build with `git checkout -- site/assets/img/og` so they aren't re-uploaded for nothing.

Home PC (set up 19 Nov): project at `E:\Ai video editor\Banh\theartfulproducts`, PHP at `C:\php\8.3`.
