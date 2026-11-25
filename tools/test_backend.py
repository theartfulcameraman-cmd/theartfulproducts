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
# expected totals from site/assets/js/pricing.js rules (magnet 349, keychain 299, holder 1499; free ship >= 1799, else 79; wrap 49)
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
s, b, _ = req("/admin/index.php?view=unpaid"); check("abandoned/failed checkouts listed under Unpaid", "Not paid" in b)
s, b, _ = req("/admin/enquiries.php"); check("enquiry listed", "Test Marathon" in b)
s, b, _ = req("/admin/export.php?view=all"); check("CSV export", b.lstrip("﻿").startswith("Order,Date") and order["order_no"] in b)
s, b, _ = req("/admin/new-order.php"); token = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
s, b, _ = req("/admin/new-order.php", form={"csrf": token, "item[0][id]": "route-keychain", "item[0][qty]": "5", "item[0][colour]": "Ember", "item[0][note]": "Expo order",
    "name": "Expo Buyer", "phone": "9000011111", "payment_status": "paid", "method": "UPI", "ship": "0", "disc": "95"})
check("manual expo order added (5 × 299 − 95 = 1,400)", "₹1,400" in b and "Expo order" in b, b[:200])
s, b, _ = req("/admin/new-order.php"); token = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
s, b, _ = req("/admin/new-order.php", form={"csrf": token, "item[0][id]": "trail-magnet", "item[0][qty]": "2", "name": "Owes Money", "phone": "9000022222", "payment_status": "pending", "ship": "0"})
s, b, _ = req("/admin/index.php"); check("All is the first tab and the default view", b.find(">All <") < b.find(">To do <") and 'href="?view=all" class="on"' in b)
s, b, _ = req("/admin/index.php?view=todo")
check("To do lists unpaid manual orders with Not paid", "Owes Money" in b and "Not paid" in b and "Awaiting payment" in b, b[-1500:])
check("To do leaves out shipped and abandoned orders", order["order_no"] not in b)
s, b, _ = req("/admin/new-order.php"); token = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
s, b, _ = req("/admin/new-order.php", form={"csrf": token, "item[0][id]": "terrain-frame", "item[0][qty]": "1", "name": "Half Paid", "phone": "9000033333", "payment_status": "advance", "advance_paid": "1500", "method": "UPI", "ship": "0"})
check("advance order saved with amount and balance", "Advance paid" in b and "₹1,500 paid" in b and "₹1,999 due" in b, b[:300])
s, b, _ = req("/admin/index.php?view=todo"); check("To do shows the advance and what's due", "Half Paid" in b and "Advance ₹1,500" in b and "₹1,999 due" in b)
s, b, _ = req("/admin/index.php?view=all&q=Half%20Paid"); hid = re.findall(r"order\.php\?id=(\d+)", b)[0]
s, b, _ = req(f"/admin/order.php?id={hid}"); token = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
base = {"csrf": token, "action": "update", "stage": "new", "payment_status": "advance", "courier": "", "tracking_no": "", "tracking_url": "", "admin_notes": ""}
s, b, _ = req(f"/admin/order.php?id={hid}", form={**base, "advance_paid": "2500"}); check("advance amount can be changed", "₹2,500 paid" in b and "₹999 due" in b)
s, b, _ = req(f"/admin/order.php?id={hid}", form={**base, "advance_paid": "3499"}); check("advance covering the total becomes Paid", "Advance covers the full amount" in b and "b-pay-paid" in b and " paid · " not in b)
s, b, _ = req("/admin/new-order.php"); token = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
s, b, _ = req("/admin/new-order.php", form={"csrf": token, "item[0][id]": "trail-magnet", "item[0][qty]": "1", "name": "No Amount", "payment_status": "advance", "advance_paid": ""})
check("advance without an amount is refused", "enter the advance amount" in b)
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
check("retired product shown as Archived", "Archived" in b)
s, b, _ = req("/admin/new-order.php"); check("retired product no longer offered", "Corporate Trek Trophy" not in b)

print("\n8. Customer accounts (email code, no password)")
def cust_opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def acct(op, data):
    r = urllib.request.Request(BASE + "/api/account.php", data=json.dumps(data).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with op.open(r) as resp: return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read().decode() or "{}")
def latest_code(to):
    for f in sorted(MAIL.glob("*.html"), reverse=True):
        head = f.read_text(encoding="utf-8").splitlines()[0]
        if f"To: {to}" in head and "login code" in head: return re.search(r"(\d{6})", head).group(1)
alice = cust_opener()
s, r = acct(alice, {"action": "me"}); check("not logged in at first", s == 401, (s, r))
s, r = acct(alice, {"action": "request_code", "email": "Runner@Example.com"}); check("code requested", s == 200, r)
code = latest_code("runner@example.com"); check("code emailed", bool(code), code)
s, r = acct(alice, {"action": "verify_code", "email": "runner@example.com", "code": "000000" if code != "000000" else "111111"}); check("wrong code refused", s == 400, r)
s, r = acct(alice, {"action": "verify_code", "email": "runner@example.com", "code": code})
check("right code logs in", s == 200 and r.get("ok"), r)
check("sees own paid orders", order["order_no"] in [o["order_no"] for o in r.get("orders", [])], [o["order_no"] for o in r.get("orders", [])])
check("unpaid checkouts hidden", all(o["payment"] in ("paid", "cod", "refunded") for o in r.get("orders", [])))
check("profile for checkout prefill", (r.get("profile") or {}).get("pin") == "411001", r.get("profile"))
s, r = acct(alice, {"action": "verify_code", "email": "runner@example.com", "code": code}); check("code can't be reused", s == 400, r)
bob = cust_opener()
s, r = acct(bob, {"action": "request_code", "email": "bob@example.com"}); bcode = latest_code("bob@example.com")
s, r = acct(bob, {"action": "verify_code", "email": "bob@example.com", "code": bcode})
check("another customer sees none of runner's orders", s == 200 and r.get("orders") == [], r.get("orders"))
s, r = acct(alice, {"action": "me"}); check("session remembered", s == 200 and r.get("email") == "runner@example.com", s)
s, r = acct(alice, {"action": "logout"}); s, r = acct(alice, {"action": "me"}); check("logout works", s == 401, s)
eve = cust_opener()
codes = [acct(eve, {"action": "request_code", "email": "flood@example.com"})[0] for _ in range(4)]
check("max 3 codes per 15 minutes", codes[:3] == [200, 200, 200] and codes[3] == 429, codes)

print("\n9. Customers page: repeat buyers matched by phone OR email, consent, sign-ups")
s, r = js("/api/create-order.php", {"items": [{"id": "trail-magnet", "qty": 1}], "customer": {**customer, "email": "consent@example.com", "phone": "9111111111"}, "marketing": True})
cs = hmac.new(CFG["key_secret"].encode(), f"{r['id']}|pay_C1".encode(), hashlib.sha256).hexdigest()
js("/api/verify-payment.php", {"razorpay_order_id": r["id"], "razorpay_payment_id": "pay_C1", "razorpay_signature": cs})
s, r = js("/api/subscribe.php", {"email": "Fan@Example.com", "source": "footer"}); check("newsletter sign-up saved", s == 200 and r.get("saved"), r)
s, r = js("/api/subscribe.php", {"email": "bot@example.com", "website": "spam"}); check("sign-up honeypot drops bots", s == 200 and "saved" not in r, r)
s, b, _ = req("/admin/login.php")
m = re.search(r'name="csrf" value="([^"]+)"', b)
if m and "Admin login" in b: req("/admin/login.php", form={"csrf": m.group(1), "password": CFG["admin_password"]})   # (already logged in otherwise)
def manual(email, phone, name):
    s, b, _ = req("/admin/new-order.php"); t = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
    req("/admin/new-order.php", form={"csrf": t, "item[0][id]": "route-keychain", "item[0][qty]": "1", "name": name, "email": email, "phone": phone, "payment_status": "paid", "method": "UPI", "ship": "0", "disc": "0", "stage": "new"})
manual("chain-a@example.com", "+91 98888 77777", "Chain One")     # A
manual("chain-b@example.com", "9888877777", "Chain One")          # same phone as A (different format), new email
manual("chain-b@example.com", "9000000001", "Chain One")          # same email as B, new phone → all three are one customer
manual("", "9000000001", "Chain One")                             # phone only, matches C
s, b, _ = req("/admin/customers.php?view=all&export=1")
rows = list(__import__("csv").reader(b.lstrip("﻿").splitlines()))
chain = [r for r in rows if "chain-a@example.com" in r[2]]
check("4 orders linked via phone OR email = 1 customer", len(chain) == 1 and chain[0][4] == "4", chain)
check("both emails shown for that customer", chain and "chain-b@example.com" in chain[0][2], chain)
check("consent at checkout recorded", any("consent@example.com" in r[2] and r[8] == "Yes" for r in rows))
check("no consent = No", any("runner@example.com" in r[2] and r[8] == "No" for r in rows))
s, b, _ = req("/admin/customers.php?view=repeat"); check("repeat customers view lists the chain", "Chain One" in b and "Repeat" in b)
s, b, _ = req("/admin/customers.php?view=subscribers"); check("newsletter sign-ups listed", "fan@example.com" in b)


print("\n10. Archive / restore / delete")
def tok(page):
    s, b, _ = req(page); return re.search(r'name="csrf" value="([^"]+)"', b).group(1), b
# --- orders ---
s, b, _ = req("/admin/index.php?view=all&q=Expo%20Buyer"); ex_id = re.findall(r"order\.php\?id=(\d+)", b)[0]
s, b, _ = req(f"/admin/order.php?id={ex_id}"); ex_no = re.search(r"<h1>(TAP\d+)</h1>", b).group(1)
before = re.search(r"<small>This month</small><b>(₹[\d,]+)</b>", req("/admin/index.php")[1]).group(1)
t, _ = tok(f"/admin/order.php?id={ex_id}")
s, b, _ = req(f"/admin/order.php?id={ex_id}", form={"csrf": t, "action": "delete", "confirm": ex_no}); 
check("can't delete an order that isn't archived", "Archive the order first" in b)
t, _ = tok(f"/admin/order.php?id={ex_id}")
s, b, _ = req(f"/admin/order.php?id={ex_id}", form={"csrf": t, "action": "archive"})
check("order archived", "archived" in b.lower())
s, b, _ = req("/admin/index.php?view=all"); check("archived order hidden from All", ex_no not in b)
after = re.search(r"<small>This month</small><b>(₹[\d,]+)</b>", b).group(1)
check("archived order left out of sales totals", before != after, (before, after))
s, b, _ = req("/admin/index.php?view=archived"); check("archived order in Archived tab", ex_no in b)
s, b, _ = req("/admin/customers.php?view=all"); check("archived order left out of Customers", "Expo Buyer" not in b)
t, _ = tok(f"/admin/order.php?id={ex_id}")
s, b, _ = req(f"/admin/order.php?id={ex_id}", form={"csrf": t, "action": "restore"})
s, b, _ = req("/admin/index.php?view=all"); check("restored order back in All", ex_no in b)
t, _ = tok(f"/admin/order.php?id={ex_id}"); req(f"/admin/order.php?id={ex_id}", form={"csrf": t, "action": "archive"})
t, _ = tok(f"/admin/order.php?id={ex_id}")
s, b, _ = req(f"/admin/order.php?id={ex_id}", form={"csrf": t, "action": "delete", "confirm": "WRONG"})
check("delete needs the order number typed", "Type the order number" in b)
t, _ = tok(f"/admin/order.php?id={ex_id}")
s, b, _ = req(f"/admin/order.php?id={ex_id}", form={"csrf": t, "action": "delete", "confirm": ex_no.lower()})
check("archived order deleted", "deleted permanently" in b)
s, b, _ = req(f"/admin/order.php?id={ex_id}"); check("deleted order is gone", s == 404)
# --- enquiries ---
s, b, _ = req("/admin/enquiries.php"); en_id = re.search(r'name="id" value="(\d+)"', b).group(1); t = re.search(r'name="csrf" value="([^"]+)"', b).group(1)
s, b, _ = req("/admin/enquiries.php", form={"csrf": t, "id": en_id, "action": "delete"}); check("can't delete an unarchived enquiry", "Archive the enquiry first" in b)
s, b, _ = req("/admin/enquiries.php", form={"csrf": t, "id": en_id, "action": "archive"}); check("enquiry archived", "Test Marathon" not in b)
s, b, _ = req("/admin/enquiries.php?s=archived"); check("enquiry in Archived tab", "Test Marathon" in b)
s, b, _ = req("/admin/enquiries.php?s=archived", form={"csrf": t, "id": en_id, "action": "delete"})
s, b, _ = req("/admin/enquiries.php?s=archived"); check("archived enquiry deleted", "Test Marathon" not in b)
# --- custom products ---
t, b = tok("/admin/products.php"); pid = re.search(r"\?edit=(\d+)", b).group(1)
s, b, _ = req("/admin/products.php", form={"csrf": t, "id": pid, "action": "restore"}); check("custom product restored", "restored" in b)
s, b, _ = req("/admin/products.php", form={"csrf": t, "id": pid, "action": "delete"}); check("can't delete an active product", "Archive the product first" in b)
s, b, _ = req("/admin/products.php", form={"csrf": t, "id": pid, "action": "archive"})
s, b, _ = req("/admin/products.php", form={"csrf": t, "id": pid, "action": "delete"}); check("archived product deleted", "deleted permanently" in b and f"?edit={pid}" not in b)
s, b, _ = req("/admin/index.php?view=all&q=Corporate%20Client"); oid2 = re.findall(r"order\.php\?id=(\d+)", b)[0]
s, b, _ = req(f"/admin/order.php?id={oid2}"); check("past order still shows the deleted product's name", "Corporate Trek Trophy" in b)

s, b, url = req("/admin/logout.php"); s, b, url = req("/admin/index.php"); check("logged out", "Admin login" in b)

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
