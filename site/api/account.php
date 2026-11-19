<?php
/* POST /api/account.php — passwordless customer accounts ("My account").
   A customer enters their email, receives a 6-digit code, and then sees every order placed
   with that email (orders are linked by email, so guest checkouts appear automatically).
   Actions: request_code {email} · verify_code {email, code} · me · logout
   Codes: valid 10 minutes, 5 tries, max 3 per email per 15 minutes, stored only as a hash.
   The reply never reveals whether an email has orders. */
require __DIR__ . '/_app.php';

const CODE_MINUTES = 10;
const SESSION_DAYS = 30;

if (!db_configured()) send_json(503, ['error' => 'Accounts are not available yet']);

$https = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');
ini_set('session.gc_maxlifetime', (string)(SESSION_DAYS * 86400));
session_name('tap_cust');
session_set_cookie_params(['lifetime' => SESSION_DAYS * 86400, 'path' => '/', 'secure' => $https, 'httponly' => true, 'samesite' => 'Lax']);
session_start();

$body = require_post();
$action = (string)($body['action'] ?? '');
$ip = substr($_SERVER['REMOTE_ADDR'] ?? 'unknown', 0, 64);
$norm = fn($e) => strtolower(trim((string)$e));

function current_customer(): ?string {
  $e = $_SESSION['cust_email'] ?? null;
  if (!$e || ($_SESSION['cust_at'] ?? 0) < time() - SESSION_DAYS * 86400) return null;
  return $e;
}

function customer_payload(string $email): array {
  $s = db()->prepare("SELECT * FROM orders WHERE LOWER(email) = ? AND payment_status IN ('paid','cod','refunded') AND COALESCE(archived,0) = 0 ORDER BY id DESC LIMIT 50");
  $s->execute([$email]);
  $orders = []; $profile = null;
  foreach ($s->fetchAll() as $o) {
    if (!$profile) $profile = ['name' => $o['name'], 'phone' => $o['phone'], 'email' => $o['email'], 'address' => $o['address'], 'city' => $o['city'], 'pin' => $o['pin']];
    $orders[] = [
      'order_no' => $o['order_no'], 'date' => $o['created_at'], 'stage' => $o['stage'], 'stage_label' => STAGES[$o['stage']] ?? $o['stage'],
      'payment' => $o['payment_status'], 'payment_label' => PAYMENT[$o['payment_status']] ?? $o['payment_status'], 'total' => (int)$o['total'],
      'items' => array_map(fn($l) => ['name' => $l['name'], 'qty' => (int)$l['qty'], 'colour' => $l['colour'] ?? '', 'opt' => $l['opt'] ?? '', 'note' => $l['note'] ?? ''], order_items($o)),
      'courier' => $o['courier'], 'tracking_no' => $o['tracking_no'], 'tracking_url' => $o['tracking_url'],
    ];
  }
  return ['ok' => true, 'email' => $email, 'profile' => $profile, 'orders' => $orders];
}

try {
  if ($action === 'request_code') {
    $email = $norm($body['email'] ?? '');
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) send_json(400, ['error' => 'Please enter a valid email address']);
    $c = db()->prepare('SELECT COUNT(*) FROM customer_codes WHERE email = ? AND created_at > ?'); $c->execute([$email, time() - 900]);
    if ((int)$c->fetchColumn() >= 3) send_json(429, ['error' => 'Too many codes requested. Please wait 15 minutes.']);
    $c = db()->prepare('SELECT COUNT(*) FROM customer_codes WHERE ip = ? AND created_at > ?'); $c->execute([$ip, time() - 3600]);
    if ((int)$c->fetchColumn() >= 10) send_json(429, ['error' => 'Too many requests. Please try again later.']);
    $code = (string)random_int(100000, 999999);
    db()->prepare('INSERT INTO customer_codes (email, code_hash, expires, attempts, ip, created_at) VALUES (?,?,?,?,?,?)')
      ->execute([$email, password_hash($code, PASSWORD_DEFAULT), time() + CODE_MINUTES * 60, 0, $ip, time()]);
    db()->prepare('DELETE FROM customer_codes WHERE created_at < ?')->execute([time() - 86400]);
    send_mail($email, "Your login code: $code", email_wrap('Your login code',
      '<p>Use this code to open your account on The Artful Products:</p>'
      . '<p style="font-size:32px;font-weight:bold;letter-spacing:6px;margin:18px 0">' . e($code) . '</p>'
      . '<p style="color:#555;font-size:14px">It works for ' . CODE_MINUTES . ' minutes. If you didn\'t ask for it, you can ignore this email.</p>'));
    send_json(200, ['ok' => true]);
  }

  if ($action === 'verify_code') {
    $email = $norm($body['email'] ?? '');
    $code = preg_replace('/\D/', '', (string)($body['code'] ?? ''));
    $s = db()->prepare('SELECT * FROM customer_codes WHERE email = ? AND expires > ? ORDER BY id DESC LIMIT 1');
    $s->execute([$email, time()]);
    $row = $s->fetch();
    if (!$row) send_json(400, ['error' => 'That code has expired. Please request a new one.']);
    if ((int)$row['attempts'] >= 5) send_json(400, ['error' => 'Too many wrong tries. Please request a new code.']);
    if (strlen($code) !== 6 || !password_verify($code, $row['code_hash'])) {
      db()->prepare('UPDATE customer_codes SET attempts = attempts + 1 WHERE id = ?')->execute([(int)$row['id']]);
      send_json(400, ['error' => 'That code is not right.']);
    }
    db()->prepare('DELETE FROM customer_codes WHERE email = ?')->execute([$email]);
    session_regenerate_id(true);
    $_SESSION['cust_email'] = $email; $_SESSION['cust_at'] = time();
    send_json(200, customer_payload($email));
  }

  if ($action === 'me') {
    $email = current_customer();
    if (!$email) send_json(401, ['error' => 'Not logged in']);
    send_json(200, customer_payload($email));
  }

  if ($action === 'logout') {
    $_SESSION = [];
    session_destroy();
    send_json(200, ['ok' => true]);
  }
} catch (Throwable $e) {
  error_log('Account error: ' . $e->getMessage());
  send_json(500, ['error' => 'Something went wrong. Please try again.']);
}
send_json(400, ['error' => 'Unknown action']);
