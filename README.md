# The Artful Products — website

A ready-to-host online store. No database, no build step: upload the `site` folder to any web host.

- **Preview locally:** open the Browser pane in Claude ("artful-products" preview), or run
  `python -m http.server 8130 --directory site` and visit http://localhost:8130
- **Everything you edit day to day is in one file:** `site/assets/js/data.js`

---

## Add a new product (5 minutes)

1. **Photos** — save them in `site/assets/img/products/`, named after the product, e.g.
   `summit-lamp-1.jpg`, `summit-lamp-2.jpg`. Square photos (1:1, about 1200 × 1200 px) look best.
2. **Open `site/assets/js/data.js`**, scroll to `PRODUCTS`, copy one product block and paste it below the last one.
3. **Change the fields:**

```js
{ id: "summit-lamp",                 // short name, lowercase, no spaces — used in the page link
  name: "Summit Table Lamp",
  cat: "home-desk",                  // must match a category id (see step 4)
  price: 2499,
  images: ["assets/img/products/summit-lamp-1.jpg", "assets/img/products/summit-lamp-2.jpg"],
  colours: [COLOURS.charcoal, COLOURS.white],   // optional
  personal: false,                   // true = shows the "your event & details" box
  isNew: true,                       // optional "New" badge
  short: "One line for the product card.",
  desc: "A paragraph for the product page.",
  specs: ["Size", "Material", "Dispatch time"] },
```

4. **New kind of product?** Add a category to `CATEGORIES` first:
   `{ id: "home-desk", name: "Home & Desk", art: "lamp", blurb: "One line about it." }`
   It appears in the menu automatically once a product uses it.
5. Save and refresh the site. Done.

**Not ready to sell yet?** Add `status: "soon"` — the product shows with a "Coming soon" badge and a "Notify me" box instead of Add to cart.
**Bulk / event-only item?** Add `status: "quote"` and `from: 149` — it shows "From ₹149/piece" and a quote button.

## The site grows with you

| Turns on automatically when… | What appears |
|---|---|
| a category has its first product | it shows in the menu, footer and shop pills |
| 3+ categories (and `showCategoryIcons: true`) | round category icons below the home-page banner |
| 4+ categories | "Shop by category" tiles |
| 9+ products | shop filters sidebar, "Shop by sport", tabbed product carousels |
| a product has `compareAt` (old price) | sale badge, "On Sale" menu link and filter |
| a product has `rating` + `reviews` | stars on cards and a Reviews tab |
| you add entries to `TESTIMONIALS` | the "Loved by finishers" section |
| `flashSale.active: true` | the countdown strip with a discount code |
| `popup.active: true` | the email popup and "Special offers" side tab |

After adding products, run `python tools/build_pages.py` (or ask Claude). New products work straight away
without it, but the build gives each one its own page (`product-<id>.html`) with a share preview for
WhatsApp/Instagram, Google product data, and a sitemap entry.

## Going live on MilesWeb (cPanel + GitHub, with Razorpay payments)

**How updates flow:** edit here (with Claude) → push to GitHub → cPanel → Git Version Control →
**Update from Remote**, then **Deploy HEAD Commit**. `.cpanel.yml` copies the `site/` folder into
**theartfulproducts.com's own folder only**. Nobody edits files on the server directly.

**This hosting account also runs theartfulcompany.com** (its files are in `public_html`). To keep the two apart:
- In cPanel → *Domains*, theartfulproducts.com should have its **own document root outside `public_html`**,
  e.g. `/home/<user>/theartfulproducts.com`. (A folder inside `public_html` also works, but then
  theartfulcompany.com's `.htaccess` rules can leak into this site.)
- On this account it is `theartfulproducts.com` (i.e. `/home/<user>/theartfulproducts.com`), already set in
  `.cpanel.yml`. The deploy stops (copying nothing) if that folder is missing or the target is inside
  `public_html`, so it can never overwrite theartfulcompany.com / theartfulcompany.in.
- The Git repository's *clone path* (e.g. `/home/<user>/repositories/theartfulproducts`) is a separate,
  private folder; it is not the website folder.
- `artful-config.php` goes in `/home/<user>/` (never inside `public_html`); the site finds it there
  whichever folder layout is used.

One-time setup:
1. `.cpanel.yml` deploys to `$HOME/theartfulproducts.com/` — theartfulproducts.com's document root (already set).
2. In Razorpay → Account & Settings → API Keys, generate a **test** key pair.
3. In cPanel → File Manager, create the file `/home/<your-cpanel-user>/artful-config.php`
   (**outside** `public_html`, so it can never be downloaded) containing:
   ```php
   <?php return ['key_id' => 'rzp_test_…', 'key_secret' => 'your secret'];
   ```
   The secret only ever lives in this file — never in the website code, GitHub or chat.
4. Put the same Key ID in `data.js` → `razorpayKey`, push and deploy.
5. Test a payment with Razorpay's test UPI / card details. Check the order in the Razorpay dashboard:
   customer, address, items and personalisation details are all in the order's **Notes**.
6. When Razorpay activates your account, change both keys to the **live** ones (`rzp_live_…`).
7. Once the free SSL certificate is active (cPanel → SSL/TLS Status), remove the two `#` in
   `site/.htaccess` to force HTTPS, and set `SITE_URL` in `tools/build_pages.py` to your domain, then rebuild.

How payments are protected: `site/api/create-order.php` re-prices every order from `api/catalog.json`
(rebuilt from `data.js` by `tools/build_pages.py`) using the same rules as `pricing.js`, so prices can't be
changed in the browser. After payment, `api/verify-payment.php` checks Razorpay's signature before the
"payment received" page is shown. **After changing prices or products, always rebuild before pushing**,
so the server's price list matches the website.


### Deploying (GitHub Actions → FTP → theartfulproducts.com)
The hosting is MilesWeb **mPanel** (not cPanel; `.cpanel.yml` is unused there). Deploys work like this:
1. Changes are committed on `main` and pushed (`python tools/publish.py`).
2. GitHub Actions (`.github/workflows/deploy.yml`) uploads the `site/` folder by FTP into theartfulproducts.com's
   own folder. You can also run it by hand: GitHub → *Actions* → *Deploy website* → *Run workflow*.
3. It uses an **FTP account limited to the theartfulproducts.com folder**, so it can never touch
   theartfulcompany.com / theartfulcompany.in in `public_html`.

One-time setup:
- mPanel → *FTP Accounts* → create an account whose directory is **only** the theartfulproducts.com folder.
- GitHub → repository → *Settings → Secrets and variables → Actions* → add `FTP_SERVER`, `FTP_USERNAME`,
  `FTP_PASSWORD`. (Typed into GitHub only, never into chat or files.) Until they exist, the workflow does nothing.
- The earlier MilesWeb "GitHub deploy" website (`theartful-nov-19-2026-1355`) and the `live` branch are no longer used.

## Order system (admin dashboard)

Every website order is saved, and you manage it at **`https://<your-domain>/admin`**:
orders list (To do · Awaiting route · Preview sent · Printing · Shipped · Delivered · Unpaid · Cancelled),
search, today/week/month sales, order detail with personalisation notes, one-tap WhatsApp messages
(ask for route · preview ready · shipped), stage + payment + courier/tracking updates, private notes,
a timeline of everything that happened, manual orders (expo / WhatsApp / phone / corporate), organiser & contact
enquiries, and CSV export for Excel.

**Custom products** (admin → *Custom products*): products for orders you get outside the website — custom
awards, corporate gifts, one-off frames. They are stored only in the admin database and **never appear on the
website or in its checkout**. They show up in *+ New order* next to the website products. For a one-time item,
pick *One-off item* in *+ New order* and type its name and price. Prices can be changed per order, and you can
note where each order came from (expo, Instagram, corporate…).

Emails sent automatically: order confirmation to the customer (asks for the route file on personalised
orders), a "new order" alert to you, and a "your order has shipped" email with the tracking link.

### One-time setup on MilesWeb
1. **Database** — cPanel → *MySQL Database Wizard*: create a database and a user, give the user
   **All Privileges**. Note the three names (they start with your cPanel username, e.g. `abcd1234_artful`).
   The tables are created automatically on first use.
2. **Order email address** — cPanel → *Email Accounts*: create e.g. `orders@<your-domain>`.
   Then cPanel → *Email Deliverability* → make sure SPF and DKIM show as valid (so emails don't land in spam).
3. **Private settings file** — cPanel → *File Manager* → your home folder (one level **above** `public_html`)
   → create `artful-config.php`:
   ```php
   <?php return [
     'key_id'         => 'rzp_test_…',          // Razorpay key ID
     'key_secret'     => '…',                   // Razorpay key secret
     'webhook_secret' => '…',                   // any long random text; same as in step 4
     'db'             => ['dsn' => 'mysql:host=localhost;dbname=abcd1234_artful;charset=utf8mb4',
                          'user' => 'abcd1234_artful', 'pass' => '…'],
     'admin_password' => '…',                   // your admin login — long and unique
     'owner_email'    => 'you@…',               // where new-order alerts go
     'mail_from'      => 'orders@<your-domain>',
     'site_url'       => 'https://<your-domain>',
   ];
   ```
   This file holds every secret. It is outside the website folder, so it can't be downloaded,
   and it is never in GitHub or chat.
4. **Razorpay webhook** — Razorpay dashboard → *Accounts & Settings → Webhooks → Add*:
   URL `https://<your-domain>/api/webhook.php`, the same secret as `webhook_secret`, and tick
   `payment.captured`, `payment.failed`, `order.paid`. Also check *Payment Capture* is set to **Automatic**.
   (The webhook marks orders paid even if a customer closes the browser right after paying.)
5. Open `https://<your-domain>/admin`, log in, and place a Razorpay **test** order to see it arrive.

### Testing changes locally
`tools/test_backend.py` runs 52 checks of the whole flow (pricing, payment signatures, webhook, emails,
enquiries, admin login, shipping, manual orders, CSV) against the local PHP preview
(`artful-products-php`, port 8140), using the local test `artful-config.php` (mock Razorpay, SQLite,
emails saved to `.local/mail`). Neither file is ever uploaded.

## Text pages
`about.html`, `shipping.html`, `refunds.html`, `privacy.html`, `terms.html` and `404.html` are written in
`tools/content_pages.py`. Blanks are highlighted in yellow on the site (`<mark class="ph">`) until you fill them in.

## Before launch — placeholders to replace
- `SITE.whatsapp`, `email`, `phone`, `social` links in `data.js`
- Product prices (marked PLACEHOLDER) and real photos
- `razorpayKey` in `data.js` and `artful-config.php` on the server (see above)
- Yellow-highlighted blanks in the policy pages (`tools/content_pages.py`)
- `SITE_URL` in `tools/build_pages.py` once the domain is bought
- About page photo (studio or founder)
- Newsletter sign-up boxes currently just say "thanks"; connect a service such as Mailchimp

## Files
- `site/assets/js/data.js` — products, categories, prices, contact details, banners
- `site/assets/js/store.js` — shared engine: header, menus, search, cart, wishlist, quick view, footer
- `site/assets/js/pages.js` — what each page shows
- `site/assets/css/style.css` — colours and fonts are at the top (`:root`)
- `site/assets/js/pricing.js` — price, discount and shipping calculation, shared with the payment server
- `tools/build_pages.py` — regenerates all pages, product pages, share images, sitemap; edit page text here, then run `python tools/build_pages.py`
- `tools/content_pages.py` — About, policies and 404 text
- `site/api/` — PHP order system: `create-order`, `verify-payment`, `webhook`, `enquiry`, shared `_app.php`
  (database, orders, emails) and `_lib.php` (pricing), plus the price list `catalog.json`
- `site/admin/` — admin dashboard (orders, order detail, manual orders, enquiries, CSV export)
- `tools/test_backend.py` — end-to-end test of the order system (local only)
- `site/.htaccess` — server settings (404 page, HTTPS, caching, security headers)
- `.cpanel.yml` — tells cPanel to copy `site/` into `public_html` on deploy
