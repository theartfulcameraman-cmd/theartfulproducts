"""End-to-end test of the order system against the local PHP server.
Run the "artful-products-php" preview (php -S localhost:8140 -t site) with the local
artful-config.php (mock Razorpay, SQLite, emails saved to .local/mail), then:
    python tools/test_backend.py
Never run against the live site."""
import hmac, hashlib, json, re, sys, urllib.request, urllib.error, http.cookiejar, urllib.parse
from pathlib import Path

BASE = "http://localhost:8140"
ROOT = Path(__file__).resolve().parent.parent
CFG = {"key_secret": "local_test_secret", "webhook_secret": "local_webhook_secret", "admin_password": "local-admin-pass"}
MAIL = ROOT / ".local/mail"
ok = fail = 0

def check(name, cond, extra=""):
    global ok, fail
    if cond: ok += 1; print("  PASS", name)
    else: fail += 1; print("  FAIL", name, extra)

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def req(path, data=None, headers=None, form=None, raw=None):
    h = dict(headers or {})
    body = None
    if data is not None: body = json.dumps(data).encode(); h["Content-Type"] = "application/json"
    if form is not None: body = urllib.parse.urlencode(form).encode(); h["Content-Type"] = "application/x-www-form-urlencoded"
    if raw is not None: body = raw
    r = urllib.request.Request(BASE + path, data=body, headers=h, method="POST" if body is not None else "GET")
    try:
        with opener.open(r) as resp: return resp.status, resp.read().decode("utf-8", "replace"), resp.geturl()
    except urllib.error.HTTPError as e: return e.code, e.read().decode("utf-8", "replace"), path

def js(path, data=None, **kw):
    s, b, _ = req(path, data, **kw)
    try: return s, json.loads(b)
    except Exception: return s, {"_raw": b[:300]}

customer = {"name": "Test Runner", "phone": "9876543210", "email": "runner@example.com", "address": "1 Test Lane", "city": "Pune", "pin": "411001"}
mails_before = len(list(MAIL.glob("*.html"))) if MAIL.exists() else 0

print("\n1. Pricing on the server matches the website")
# expected totals from site/assets/js/pricing.js rules (magnet 349, keychain 299, holder 1499; free ship >= 999, else 79; wrap 49)
cases = [
    ([{"id": "trail-magnet", "qty": 1}], {}, 349 + 79),
    ([{"id": "route-keychain", "qty": 1}], {"wrap": True}, 299 + 79 + 49),
    ([{"id": "trail-magnet", "qty": 2}, {"id": "medal-holder", "qty": 1}], {}, 2197),
    ([{"id": "trail-magnet", "qty": -4, "price": 1}], {}, 349 + 79),   # bad qty clamped, sent price ignored
]
for items, opts, expected in cases:
    s, r = js("/api/create-order.php", {"items": items, "customer": customer, **opts})
    check(f"{[i['id'] for i in items]} {opts} = Rs{expected}", s == 200 and r.get("amount") == expected * 100, (s, r))

s, r = js("/api/create-order.php", {"items": [{"id": "nope", "qty": 1}], "customer": customer}); check("unknown product rejected", s == 400, r)
s, r = js("/api/create-order.php", {"items": [], "customer": customer}); check("empty cart rejected", s == 400, r)
s, r = js("/api/create-order.php", {"items": [{"id": "trail-magnet", "qty": 1}], "customer": {**customer, "pin": "12"}}); check("bad PIN rejected", s == 400, r)

print("\n2. Checkout → verified payment → order paid + emails")
s, order = js("/api/create-order.php", {"items": [{"id": "terrain-frame", "qty": 1, "colour": "Oak", "note": "Pune Half 2026, 1:52:30"}], "customer": customer, "note": "Gift"})
check("order created with an order number", s == 200 and str(order.get("order_no", "")).startswith("TAP"), order)
pid = "pay_TEST" + order["id"][-6:]
sig = hmac.new(CFG["key_secret"].encode(), f"{order['id']}|{pid}".encode(), hashlib.sha256).hexdigest()
s, r = js("/api/verify-payment.php", {"razorpay_order_id": order["id"], "razorpay_payment_id": pid, "razorpay_signature": "0" * 64})
check("forged signature rejected", s == 400, r)
s, r = js("/api/verify-payment.php", {"razorpay_order_id": order["id"], "razorpay_payment_id": pid, "razorpay_signature": sig})
check("genuine signature accepted", s == 200 and r.get("order_no") == order["order_no"], r)
mails = sorted(MAIL.glob("*.html"))[mails_before:] if MAIL.exists() else []
check("customer + owner emails written", len(mails) == 2, [m.name for m in mails])
check("confirmation asks for the route file", any("send us your route" in m.read_text(encoding="utf-8") for m in mails))

print("\n3. Razorpay webhook (backup) is safe to receive twice")
evt = json.dumps({"event": "payment.captured", "payload": {"payment": {"entity": {"id": pid, "order_id": order["id"], "method": "upi"}}}}).encode()
s, r = js("/api/webhook.php", raw=evt, headers={"X-Razorpay-Signature": "bad", "Content-Type": "application/json"}); check("webhook with bad signature rejected", s == 400, r)
wsig = hmac.new(CFG["webhook_secret"].encode(), evt, hashlib.sha256).hexdigest()
s, r = js("/api/webhook.php", raw=evt, headers={"X-Razorpay-Signature": wsig, "Content-Type": "application/json"}); check("webhook accepted", s == 200, r)
mails2 = sorted(MAIL.glob("*.html"))[mails_before:]
check("no duplicate emails after webhook", len(mails2) == 2, len(mails2))

# webhook-only path: customer closed the browser before verify ran
s, order2 = js("/api/create-order.php", {"items": [{"id": "trail-magnet", "qty": 3}], "customer": customer})
evt2 = json.dumps({"event": "payment.captured", "payload": {"payment": {"entity": {"id": "pay_WEBHOOKONLY", "order_id": order2["id"], "method": "card"}}}}).encode()
s, r = js("/api/webhook.php", raw=evt2, headers={"X-Razorpay-Signature": hmac.new(CFG["webhook_secret"].encode(), evt2, hashlib.sha256).hexdigest()})
check("webhook alone marks an order paid", s == 200, r)
evt3 = json.dumps({"event": "payment.failed", "payload": {"payment": {"entity": {"id": "pay_F", "order_id": js("/api/create-order.php", {"items": [{"id": "trail-magnet", "qty": 1}], "customer": customer})[1]["id"], "error_description": "Card declined"}}}}).encode()
s, r = js("/api/webhook.php", raw=evt3, headers={"X-Razorpay-Signature": hmac.new(CFG["webhook_secret"].encode(), evt3, hashlib.sha256).hexdigest()})
check("failed payment recorded", s == 200, r)

print("\n4. Enquiries")
s, r = js("/api/enquiry.php", {"kind": "organiser", "data": {"name": "Race Org", "phone": "9000000000", "event": "Test Marathon", "interested": "3D Trail Fridge Magnets"}})
check("organiser enquiry saved", s == 200 and r.get("saved"), r)
s, r = js("/api/enquiry.php", {"kind": "contact", "website": "spam.com", "data": {"name": "Bot", "phone": "1"}})
check("honeypot spam silently dropped", s == 200 and "saved" not in r, r)

print("\n5. Private files are not reachable")
for p in ["/api/_app.php", "/api/_lib.php", "/admin/_admin.php"]:
    s, b, _ = req(p); check(f"{p} blocked", s == 404 and "<?php" not in b, s)

print("\n6. Admin dashboard")
s, b, url = req("/admin/index.php"); check("dashboard redirects to login when logged out", url.endswith("login.php") or "Admin login" in b)
s, b, _ = req("/admin/login.php"); token = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
s, b, _ = req("/admin/login.php", form={"csrf": token, "password": "wrong"}); check("wrong password refused", "not right" in b)
s, b, _ = req("/admin/login.php", form={"csrf": "bad", "password": CFG["admin_password"]}); check("login without valid CSRF token refused", s == 400)
s, b, url = req("/admin/login.php", form={"csrf": token, "password": CFG["admin_password"]}); check("correct password logs in", "Orders" in b and order["order_no"] in b, url)
check("paid personalised order shows as 'Awaiting route file'", "Awaiting route file" in b)
oid = re.search(r'order\.php\?id=(\d+)"[^>]*>\s*<span><b>' + order["order_no"], b)
oid = oid.group(1) if oid else re.findall(r"order\.php\?id=(\d+)", b)[0]
s, b, _ = req(f"/admin/order.php?id={oid}"); check("order page shows personalisation note", "Pune Half 2026" in b)
check("order timeline shows payment", "Payment received" in b)
token = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
before = len(list(MAIL.glob("*.html")))
s, b, _ = req(f"/admin/order.php?id={oid}", form={"csrf": token, "action": "update", "stage": "shipped", "payment_status": "paid", "courier": "Shiprocket", "tracking_no": "SR123456", "tracking_url": "", "email_customer": "1", "admin_notes": "Packed with care"})
check("marked shipped", "Shipped" in b and "SR123456" in b)
check("tracking link built for Shiprocket", "shiprocket.co/tracking/SR123456" in b)
check("shipping email sent to customer", len(list(MAIL.glob("*.html"))) == before + 1)
s, b, _ = req("/admin/index.php?view=unpaid"); check("abandoned/failed checkouts listed under Unpaid", "Failed" in b or "Pending" in b)
s, b, _ = req("/admin/enquiries.php"); check("enquiry listed", "Test Marathon" in b)
s, b, _ = req("/admin/export.php?view=all"); check("CSV export", b.lstrip("﻿").startswith("Order,Date") and order["order_no"] in b)
s, b, _ = req("/admin/new-order.php"); token = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
s, b, _ = req("/admin/new-order.php", form={"csrf": token, "item[0][id]": "route-keychain", "item[0][qty]": "5", "item[0][colour]": "Ember", "item[0][note]": "Expo order",
    "name": "Expo Buyer", "phone": "9000011111", "payment_status": "paid", "method": "UPI", "ship": "0", "disc": "95"})
check("manual expo order added (5 × 299 − 95 = 1,400)", "₹1,400" in b and "Expo order" in b, b[:200])
print("\n7. Custom products (admin only, never on the website)")
s, b, _ = req("/admin/products.php"); token = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
s, b, _ = req("/admin/products.php", form={"csrf": token, "id": "0", "name": "Corporate Trek Trophy", "price": "2500", "category": "Awards", "description": "Walnut base", "personal": "1", "active": "1"})
check("custom product added", "Corporate Trek Trophy" in b and "₹2,500" in b)
cpid = re.search(r"\?edit=(\d+)", b).group(1)
s, b, _ = req("/admin/new-order.php"); check("custom product offered in + New order", "Corporate Trek Trophy" in b and "not on website" in b)
check("one-off item option offered", "One-off item" in b)
for page in ["/index.html", "/shop.html", "/api/catalog.json", "/assets/js/data.js", "/sitemap.xml"]:
    s, body, _ = req(page); check(f"not on website: {page}", "Corporate Trek Trophy" not in body)
s, r = js("/api/create-order.php", {"items": [{"id": "c:" + cpid, "qty": 1}], "customer": customer})
check("custom product can't be bought through the website checkout", s == 400, r)
token = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
s, b, _ = req("/admin/new-order.php", form={"csrf": token,
    "item[0][id]": "c:" + cpid, "item[0][qty]": "3", "item[0][price]": "2200", "item[0][note]": "Infosys trek 2026",   # price changed for this order
    "item[1][id]": "oneoff", "item[1][name]": "Custom engraved plaque", "item[1][qty]": "1", "item[1][price]": "800",
    "item[2][id]": "terrain-frame", "item[2][qty]": "1", "item[2][price]": "", "item[2][colour]": "Oak",          # empty price = website price 3,499
    "name": "Corporate Client", "phone": "9000022222", "source_label": "Corporate", "payment_status": "pending", "method": "Invoice", "ship": "150", "disc": "0", "stage": "new"})
check("mixed custom order total (3×2,200 + 800 + 3,499 + 150 = 11,049)", "₹11,049" in b, b[:300])
check("custom item names on the order", "Corporate Trek Trophy" in b and "Custom engraved plaque" in b and "Infosys trek 2026" in b)
check("order source recorded", "Order from: Corporate" in b)
s, b, _ = req("/admin/new-order.php"); token = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
s, b, _ = req("/admin/new-order.php", form={"csrf": token, "item[0][id]": "oneoff", "item[0][name]": "", "item[0][qty]": "1", "name": "X", "payment_status": "paid"})
check("one-off item without a name is refused", "Please name the one-off item" in b)
s, b, _ = req(f"/admin/products.php?edit={cpid}"); token = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
s, b, _ = req("/admin/products.php", form={"csrf": token, "id": cpid, "name": "Corporate Trek Trophy", "price": "2500", "category": "Awards", "description": "", "personal": "1"})
check("retired product shown as Retired", "Retired" in b)
s, b, _ = req("/admin/new-order.php"); check("retired product no longer offered", "Corporate Trek Trophy" not in b)

s, b, url = req("/admin/logout.php"); s, b, url = req("/admin/index.php"); check("logged out", "Admin login" in b)

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
