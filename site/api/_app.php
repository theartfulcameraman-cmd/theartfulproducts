<?php
/* ------------------------------------------------------------------
   The Artful Products — order system core (MilesWeb / cPanel PHP + MySQL)
   Config, database, orders, events, enquiries and emails.
   Used by the payment endpoints in /api and the admin dashboard in /admin.

   Private settings live OUTSIDE public_html in /home/<cpanel-user>/artful-config.php
   (see README → "Order system setup"). Nothing secret is stored in this code.
------------------------------------------------------------------- */
if (basename($_SERVER['SCRIPT_FILENAME'] ?? '') === basename(__FILE__)) { http_response_code(404); exit; }
require_once __DIR__ . '/_lib.php';
date_default_timezone_set('Asia/Kolkata');

/* ---------------- config ---------------- */
function config(): array {
  static $c = null;
  if ($c !== null) return $c;
  $home = getenv('HOME') ?: '';
  // the cPanel home folder (/home/<user>), worked out from this file's own path, so it is found
  // whether the site's folder is /home/<user>/theartfulproducts.com or /home/<user>/public_html/<domain>
  $cpHome = preg_match('#^(/home\d*/[^/]+)/#', str_replace('\\', '/', __DIR__), $m) ? $m[1] : '';
  $candidates = array_filter([
    getenv('ARTFUL_CONFIG') ?: '',
    $home ? $home . '/artful-config.php' : '',
    $cpHome ? $cpHome . '/artful-config.php' : '',
    dirname(__DIR__, 2) . '/artful-config.php',   // one level above the site folder (also used for local testing)
  ]);
  // never read a settings file from inside a public web folder
  $candidates = array_filter($candidates, fn($f) => !preg_match('#/public_html/#', str_replace('\\', '/', $f)));
  foreach ($candidates as $f) {
    if (is_file($f)) { $c = include $f; if (is_array($c)) return $c; }
  }
  return $c = [];
}
function cfg(string $key, $default = null) { return config()[$key] ?? $default; }

function razorpay_keys(): array {
  $id = cfg('key_id'); $secret = cfg('key_secret');
  if (!$id || !$secret) send_json(503, ['error' => 'Payments are not configured yet']);
  return [$id, $secret];
}

/* ---------------- labels ---------------- */
const STAGES = [
  'new' => 'New', 'awaiting_route' => 'Awaiting route file', 'preview_sent' => 'Preview sent',
  'approved' => 'Approved', 'printing' => 'Printing', 'packed' => 'Packed', 'shipped' => 'Shipped',
  'delivered' => 'Delivered', 'cancelled' => 'Cancelled',
];
const PAYMENT = ['pending' => 'Pending', 'paid' => 'Paid', 'advance' => 'Advance paid', 'failed' => 'Failed', 'refunded' => 'Refunded', 'cod' => 'Cash on delivery'];
const ENQUIRY_STATUS = ['new' => 'New', 'contacted' => 'Contacted', 'quoted' => 'Quote sent', 'won' => 'Won', 'lost' => 'Lost'];

function now(): string { return date('Y-m-d H:i:s'); }
function inr($n): string {
  $n = (int)$n; $s = (string)abs($n);
  if (strlen($s) > 3) { $last3 = substr($s, -3); $rest = substr($s, 0, -3); $rest = preg_replace('/\B(?=(\d{2})+(?!\d))/', ',', $rest); $s = $rest . ',' . $last3; }
  return ($n < 0 ? '-' : '') . '₹' . $s;
}
function e($s): string { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }

/* ---------------- database ---------------- */
function db_configured(): bool { return (bool)cfg('db'); }

function db(): PDO {
  static $pdo = null;
  if ($pdo) return $pdo;
  $d = cfg('db');
  if (!$d) throw new RuntimeException('Database is not configured');
  $pdo = new PDO($d['dsn'], $d['user'] ?? null, $d['pass'] ?? null, [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
  ]);
  migrate($pdo);
  return $pdo;
}

function migrate(PDO $p): void {
  $sqlite = $p->getAttribute(PDO::ATTR_DRIVER_NAME) === 'sqlite';
  $id = $sqlite ? 'INTEGER PRIMARY KEY AUTOINCREMENT' : 'INT AUTO_INCREMENT PRIMARY KEY';
  $tail = $sqlite ? '' : ' ENGINE=InnoDB DEFAULT CHARSET=utf8mb4';
  $p->exec("CREATE TABLE IF NOT EXISTS orders (
    id $id,
    order_no VARCHAR(20),
    created_at VARCHAR(20), updated_at VARCHAR(20),
    source VARCHAR(20) DEFAULT 'website',
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(40) DEFAULT '',
    stage VARCHAR(20) DEFAULT 'new',
    rzp_order_id VARCHAR(40), rzp_payment_id VARCHAR(40),
    name VARCHAR(120), phone VARCHAR(30), email VARCHAR(160),
    address TEXT, city VARCHAR(80), pin VARCHAR(10),
    items TEXT, note TEXT, code VARCHAR(30),
    sub INT DEFAULT 0, disc INT DEFAULT 0, ship INT DEFAULT 0, wrap INT DEFAULT 0, total INT DEFAULT 0,
    courier VARCHAR(60) DEFAULT '', tracking_no VARCHAR(80) DEFAULT '', tracking_url VARCHAR(255) DEFAULT '',
    admin_notes TEXT,
    confirm_emails_sent INT DEFAULT 0, shipped_email_sent INT DEFAULT 0
  )$tail");
  $p->exec("CREATE TABLE IF NOT EXISTS order_events (
    id $id, order_id INT, at VARCHAR(20), kind VARCHAR(30), message TEXT
  )$tail");
  $p->exec("CREATE TABLE IF NOT EXISTS enquiries (
    id $id, created_at VARCHAR(20), kind VARCHAR(20), name VARCHAR(120), phone VARCHAR(30), email VARCHAR(160),
    data TEXT, status VARCHAR(20) DEFAULT 'new', notes TEXT
  )$tail");
  $p->exec("CREATE TABLE IF NOT EXISTS login_attempts (id $id, ip VARCHAR(64), at INT)$tail");
  // customer login codes (passwordless "My account": a 6-digit code is emailed, stored only as a hash)
  $p->exec("CREATE TABLE IF NOT EXISTS customer_codes (
    id $id, email VARCHAR(160), code_hash VARCHAR(255), expires INT, attempts INT DEFAULT 0, ip VARCHAR(64), created_at INT
  )$tail");
  try { $p->exec('CREATE INDEX idx_codes_email ON customer_codes (email)'); } catch (PDOException $e) {}
  // newsletter / "notify me" sign-ups
  $p->exec("CREATE TABLE IF NOT EXISTS subscribers (
    id $id, email VARCHAR(160), source VARCHAR(40), created_at VARCHAR(20), unsubscribed INT DEFAULT 0
  )$tail");
  // marketing consent ticked at checkout (DPDP: only message customers who agreed)
  try { $p->exec('ALTER TABLE orders ADD COLUMN marketing_ok INT DEFAULT 0'); } catch (PDOException $e) {}
  // archive = hidden from admin lists and totals, restorable; delete is only allowed once archived
  try { $p->exec('ALTER TABLE orders ADD COLUMN archived INT DEFAULT 0'); } catch (PDOException $e) {}
  try { $p->exec('ALTER TABLE enquiries ADD COLUMN archived INT DEFAULT 0'); } catch (PDOException $e) {}
  // part payment taken up front (payment_status 'advance'); balance due = total - advance_paid
  try { $p->exec('ALTER TABLE orders ADD COLUMN advance_paid INT DEFAULT 0'); } catch (PDOException $e) {}
  // admin-only products for custom / offline orders — never shown on the website
  $p->exec("CREATE TABLE IF NOT EXISTS custom_products (
    id $id, created_at VARCHAR(20), name VARCHAR(160), price INT DEFAULT 0, category VARCHAR(80) DEFAULT '',
    description TEXT, personal INT DEFAULT 0, active INT DEFAULT 1
  )$tail");
  try { $p->exec("ALTER TABLE custom_products ADD COLUMN sku VARCHAR(40) DEFAULT ''"); } catch (PDOException $e) {}
  // indexes (ignore "already exists")
  foreach (['CREATE INDEX idx_orders_rzp ON orders (rzp_order_id)', 'CREATE INDEX idx_events_order ON order_events (order_id)'] as $sql) {
    try { $p->exec($sql); } catch (PDOException $e) {}
  }
}

/* ---------------- orders ---------------- */
function order_get(int $id): ?array {
  $s = db()->prepare('SELECT * FROM orders WHERE id = ?'); $s->execute([$id]);
  return $s->fetch() ?: null;
}
function order_by_rzp(string $rzpOrderId): ?array {
  $s = db()->prepare('SELECT * FROM orders WHERE rzp_order_id = ?'); $s->execute([$rzpOrderId]);
  return $s->fetch() ?: null;
}
function order_items(array $o): array {
  $items = json_decode($o['items'] ?: '[]', true) ?: [];
  foreach ($items as &$l) if (empty($l['sku'])) $l['sku'] = line_sku($l);   // orders saved before SKUs existed
  return $items;
}

/* SKU for an order line, worked out from what it is (website / custom / one-off) */
function line_sku(array $l): string {
  $id = (string)($l['id'] ?? '');
  if ($id === 'oneoff') return 'TAP-ONEOFF';
  if (str_starts_with($id, 'c:')) { $cp = custom_product((int)substr($id, 2)); return $cp ? custom_sku($cp) : 'TAP-CUS-' . str_pad(substr($id, 2), 3, '0', STR_PAD_LEFT); }
  foreach (catalog()['products'] as $p) if ($p['id'] === $id) return product_sku($p, (string)($l['colour'] ?? ''));
  return 'TAP-' . strtoupper($id);
}
function custom_sku(array $cp): string {
  if (!empty($cp['sku'])) return $cp['sku'];
  $cat = strtoupper(substr(preg_replace('/[^a-z]/i', '', (string)$cp['category']), 0, 3)) ?: 'GEN';
  return 'TAP-CUS-' . str_pad($cat, 3, 'X') . '-' . str_pad((string)(int)$cp['id'], 3, '0', STR_PAD_LEFT);
}

function add_event(int $orderId, string $kind, string $message): void {
  db()->prepare('INSERT INTO order_events (order_id, at, kind, message) VALUES (?,?,?,?)')->execute([$orderId, now(), $kind, $message]);
}
function order_events(int $orderId): array {
  $s = db()->prepare('SELECT * FROM order_events WHERE order_id = ? ORDER BY id DESC'); $s->execute([$orderId]);
  return $s->fetchAll();
}

/* $t = result of compute_order(); $c = customer fields;
   $createdAt = order date for a past order recorded by hand ('Y-m-d H:i:s'), null = now */
function order_create(array $t, array $c, string $note, string $source, ?string $rzpOrderId, string $payment = 'pending', string $method = '', bool $marketing = false, ?string $createdAt = null): array {
  $pdo = db();
  $pdo->prepare('INSERT INTO orders (created_at, updated_at, source, payment_status, payment_method, stage, rzp_order_id,
      name, phone, email, address, city, pin, items, note, code, sub, disc, ship, wrap, total, admin_notes)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)')->execute([
    $createdAt ?: now(), now(), $source, $payment, $method, 'new', $rzpOrderId,
    clip($c['name'] ?? '', 120), clip($c['phone'] ?? '', 30), clip($c['email'] ?? '', 160),
    clip($c['address'] ?? '', 500), clip($c['city'] ?? '', 80), clip($c['pin'] ?? '', 10),
    json_encode($t['lines'], JSON_UNESCAPED_UNICODE), clip($note, 1000), $t['code'],
    $t['sub'], $t['disc'], $t['ship'], $t['wrap'], $t['total'], '',
  ]);
  $id = (int)$pdo->lastInsertId();
  $no = 'TAP' . (1000 + $id);
  $pdo->prepare('UPDATE orders SET order_no = ?, marketing_ok = ? WHERE id = ?')->execute([$no, $marketing ? 1 : 0, $id]);
  add_event($id, 'created', $source === 'manual' ? 'Order added by hand' : 'Checkout started on the website');
  return order_get($id);
}

function order_update(int $id, array $fields): void {
  if (!$fields) return;
  $fields['updated_at'] = now();
  $set = implode(', ', array_map(fn($k) => "$k = ?", array_keys($fields)));
  db()->prepare("UPDATE orders SET $set WHERE id = ?")->execute([...array_values($fields), $id]);
}

/* Called by verify-payment (browser) AND the Razorpay webhook — whichever comes first. Safe to call twice. */
function order_mark_paid(array $o, string $paymentId, string $via, string $method = ''): array {
  if ($o['payment_status'] !== 'paid') {
    $needsRoute = array_filter(order_items($o), fn($l) => !empty($l['personal']));
    $stage = $o['stage'] === 'new' && $needsRoute ? 'awaiting_route' : $o['stage'];
    order_update((int)$o['id'], ['payment_status' => 'paid', 'rzp_payment_id' => $paymentId, 'stage' => $stage, 'payment_method' => $method ?: $o['payment_method']]);
    add_event((int)$o['id'], 'paid', "Payment received ($via) · $paymentId");
    $o = order_get((int)$o['id']);
  }
  if (!(int)$o['confirm_emails_sent']) {
    db()->prepare('UPDATE orders SET confirm_emails_sent = 1 WHERE id = ? AND confirm_emails_sent = 0')->execute([(int)$o['id']]);
    email_order_confirmation($o);
    email_owner_new_order($o);
  }
  return order_get((int)$o['id']);
}

function order_mark_failed(array $o, string $reason): void {
  if ($o['payment_status'] === 'pending') {
    order_update((int)$o['id'], ['payment_status' => 'failed']);
    add_event((int)$o['id'], 'failed', 'Payment failed: ' . clip($reason, 200));
  }
}

/* ---------------- custom products (admin only) ---------------- */
function custom_products(bool $activeOnly = true): array {
  return db()->query('SELECT * FROM custom_products' . ($activeOnly ? ' WHERE active = 1' : '') . ' ORDER BY active DESC, name')->fetchAll();
}
function custom_product(int $id): ?array {
  $s = db()->prepare('SELECT * FROM custom_products WHERE id = ?'); $s->execute([$id]);
  return $s->fetch() ?: null;
}

/* ---------------- enquiries ---------------- */
function enquiry_create(string $kind, array $data): int {
  db()->prepare('INSERT INTO enquiries (created_at, kind, name, phone, email, data, status, notes) VALUES (?,?,?,?,?,?,?,?)')->execute([
    now(), $kind, clip($data['name'] ?? '', 120), clip($data['phone'] ?? '', 30), clip($data['email'] ?? '', 160),
    json_encode($data, JSON_UNESCAPED_UNICODE), 'new', '',
  ]);
  return (int)db()->lastInsertId();
}

/* ---------------- email ----------------
   Uses PHP mail() through the host's mail server. Sent as a proper multipart message
   (plain text + HTML, Date and Message-ID headers) so spam filters don't penalise it.
   For local testing, set 'mail_log_dir' in the config: the HTML is saved as a .html file
   and the full raw message as raw/*.eml, instead of being sent. */
function html_to_text(string $html): string {
  $t = preg_replace('#<(script|style)\b.*?</\1>#is', '', $html);
  $t = preg_replace_callback('#<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>#is', function ($m) {
    $label = trim(strip_tags($m[2])); $url = html_entity_decode($m[1]);
    return $label && $label !== $url ? "$label ($url)" : $url;
  }, $t);
  $t = preg_replace('#<br\s*/?>|</(p|div|h[1-6]|tr|li|table)>#i', "\n", $t);
  $t = preg_replace('#</t[dh]>#i', "  ", $t);
  $t = html_entity_decode(strip_tags($t), ENT_QUOTES, 'UTF-8');
  $t = preg_replace("/[ \t]+/", ' ', $t);
  $t = preg_replace("/ *\n */", "\n", $t);
  return trim(preg_replace("/\n{3,}/", "\n\n", $t));
}

function send_mail(string $to, string $subject, string $html, string $replyTo = ''): bool {
  if (!$to || !filter_var($to, FILTER_VALIDATE_EMAIL)) return false;
  $from = cfg('mail_from') ?: ('orders@' . ($_SERVER['HTTP_HOST'] ?? 'localhost'));
  $domain = substr(strrchr($from, '@'), 1) ?: 'localhost';
  $boundary = 'tap_' . bin2hex(random_bytes(12));
  $headers = [
    'MIME-Version: 1.0',
    'Date: ' . date('r'),
    'Message-ID: <' . bin2hex(random_bytes(16)) . '@' . $domain . '>',
    'From: The Artful Products <' . $from . '>',
    'Content-Type: multipart/alternative; boundary="' . $boundary . '"',
  ];
  if ($replyTo && filter_var($replyTo, FILTER_VALIDATE_EMAIL) && strcasecmp($replyTo, $to) !== 0) $headers[] = 'Reply-To: ' . $replyTo;
  $part = fn($type, $content) => "--$boundary\r\nContent-Type: $type; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($content)) . "\r\n";
  $body = $part('text/plain', html_to_text($html)) . $part('text/html', $html) . "--$boundary--\r\n";
  $encSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';

  $logDir = cfg('mail_log_dir');
  if ($logDir) {
    @mkdir($logDir . '/raw', 0777, true);
    $name = date('Ymd-His') . '-' . substr(md5($to . $subject . microtime()), 0, 6);
    file_put_contents("$logDir/$name.html", "<!-- To: $to | Subject: $subject -->\n" . $html);
    file_put_contents("$logDir/raw/$name.eml", "To: $to\r\nSubject: $encSubject\r\n" . implode("\r\n", $headers) . "\r\n\r\n" . $body);
    return true;
  }
  return @mail($to, $encSubject, $body, implode("\r\n", $headers), '-f' . $from);
}

function email_wrap(string $title, string $body): string {
  $site = cfg('site_url', '');
  return '<!doctype html><html><body style="margin:0;background:#f4f2ee;font-family:Arial,Helvetica,sans-serif;color:#111">
  <div style="max-width:560px;margin:0 auto;padding:24px">
    <div style="background:#111;color:#fff;padding:18px 22px;border-radius:12px 12px 0 0;font-weight:bold;font-size:18px">The Artful Products</div>
    <div style="height:5px;background:#EC683B"></div>
    <div style="background:#fff;padding:24px 22px;border-radius:0 0 12px 12px">
      <h2 style="margin:0 0 14px;font-size:20px">' . e($title) . '</h2>' . $body . '
    </div>
    <p style="font-size:12px;color:#777;text-align:center;margin-top:16px">The Artful Products · A unit of The Artful Company · Pune' . ($site ? ' · <a href="' . e($site) . '" style="color:#777">' . e(preg_replace('#^https?://#', '', $site)) . '</a>' : '') . '</p>
  </div></body></html>';
}

function email_items_table(array $o): string {
  $rows = '';
  foreach (order_items($o) as $l) {
    $extra = array_filter([$l['colour'] ?? '', $l['opt'] ?? '']);
    $rows .= '<tr><td style="padding:8px 0;border-bottom:1px solid #eee">' . e($l['name']) . ($extra ? '<br><span style="color:#777;font-size:13px">' . e(implode(' · ', $extra)) . '</span>' : '')
      . (!empty($l['note']) ? '<br><span style="color:#777;font-size:13px;font-style:italic">“' . e($l['note']) . '”</span>' : '')
      . '</td><td style="padding:8px 0;border-bottom:1px solid #eee;text-align:center">×' . (int)$l['qty'] . '</td><td style="padding:8px 0;border-bottom:1px solid #eee;text-align:right">' . inr($l['total']) . '</td></tr>';
  }
  $sum = fn($k, $v) => '<tr><td colspan="2" style="padding:4px 0;color:#555">' . $k . '</td><td style="padding:4px 0;text-align:right">' . $v . '</td></tr>';
  return '<table style="width:100%;border-collapse:collapse;font-size:14px">' . $rows
    . $sum('Subtotal', inr($o['sub'])) . ((int)$o['disc'] ? $sum('Discount (' . e($o['code']) . ')', '−' . inr($o['disc'])) : '')
    . $sum('Shipping', (int)$o['ship'] ? inr($o['ship']) : 'Free') . ((int)$o['wrap'] ? $sum('Gift wrap', inr($o['wrap'])) : '')
    . '<tr><td colspan="2" style="padding:10px 0;font-weight:bold;border-top:2px solid #111">Total</td><td style="padding:10px 0;text-align:right;font-weight:bold;border-top:2px solid #111">' . inr($o['total']) . '</td></tr></table>';
}

function email_order_confirmation(array $o): void {
  $personal = array_filter(order_items($o), fn($l) => !empty($l['personal']));
  $waNum = cfg('whatsapp') ?: (catalog()['site']['whatsapp'] ?? '');
  $wa = $waNum ? 'https://wa.me/' . $waNum . '?text=' . rawurlencode('Hi! My order ' . $o['order_no'] . ' — here is my route file:') : '';
  $body = '<p>Hi ' . e(strtok($o['name'], ' ')) . ', thank you for your order! Your order number is <b>' . e($o['order_no']) . '</b>.</p>'
    . ($personal ? '<p style="background:#FFF6D6;padding:12px 14px;border-radius:8px"><b>Next step:</b> send us your route — a GPX file, a Strava/Garmin link, or just the event name. We\'ll send you a digital preview to approve before we print.'
      . ($wa ? '<br><a href="' . e($wa) . '" style="display:inline-block;margin-top:10px;background:#111;color:#fff;padding:10px 16px;border-radius:999px;text-decoration:none">Send route on WhatsApp</a>' : '') . '</p>' : '')
    . email_items_table($o)
    . '<p style="margin-top:18px;font-size:14px"><b>Delivering to</b><br>' . e($o['name']) . '<br>' . nl2br(e($o['address'])) . ', ' . e($o['city']) . ' ' . e($o['pin']) . '<br>' . e($o['phone']) . '</p>'
    . '<p style="font-size:14px;color:#555">We\'ll email you the tracking link as soon as your order ships. You can also follow your order any time in '
    . '<a href="' . e(rtrim(cfg('site_url', ''), '/') . '/account.html') . '">My account</a> (log in with this email, no password needed).</p>';
  send_mail($o['email'], 'Order confirmed · ' . $o['order_no'], email_wrap('Thank you — your order is confirmed', $body));
}

function email_owner_new_order(array $o): void {
  $owner = cfg('owner_email'); if (!$owner) return;
  $admin = rtrim(cfg('site_url', ''), '/') . '/admin/order.php?id=' . (int)$o['id'];
  $body = '<p><b>' . e($o['name']) . '</b> · ' . e($o['phone']) . ' · ' . e($o['email']) . '<br>' . e($o['city']) . ' ' . e($o['pin']) . '</p>'
    . email_items_table($o) . ($o['note'] ? '<p><b>Order note:</b> ' . e($o['note']) . '</p>' : '')
    . '<p><a href="' . e($admin) . '" style="display:inline-block;background:#111;color:#fff;padding:10px 16px;border-radius:999px;text-decoration:none">Open in admin</a></p>';
  send_mail($owner, 'New order ' . $o['order_no'] . ' · ' . inr($o['total']), email_wrap('New paid order', $body), $o['email']);
}

function email_shipped(array $o): void {
  $track = $o['tracking_url'] ?: '';
  $body = '<p>Hi ' . e(strtok($o['name'], ' ')) . ', good news — your order <b>' . e($o['order_no']) . '</b> is on its way!</p>'
    . '<p style="font-size:14px">' . ($o['courier'] ? 'Courier: <b>' . e($o['courier']) . '</b><br>' : '') . ($o['tracking_no'] ? 'Tracking number: <b>' . e($o['tracking_no']) . '</b>' : '') . '</p>'
    . ($track ? '<p><a href="' . e($track) . '" style="display:inline-block;background:#111;color:#fff;padding:10px 16px;border-radius:999px;text-decoration:none">Track your parcel</a></p>' : '')
    . email_items_table($o);
  send_mail($o['email'], 'Your order ' . $o['order_no'] . ' has shipped', email_wrap('Your order has shipped', $body));
}
