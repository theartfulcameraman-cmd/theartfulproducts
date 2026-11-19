<?php
/* Shared code for the admin dashboard: login, sessions, CSRF protection, page layout. */
if (basename($_SERVER['SCRIPT_FILENAME'] ?? '') === basename(__FILE__)) { http_response_code(404); exit; }
require_once dirname(__DIR__) . '/api/_app.php';

header('X-Robots-Tag: noindex, nofollow');
header('Cache-Control: no-store');
header('X-Frame-Options: DENY');

$https = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');
session_name('tap_admin');
session_set_cookie_params(['lifetime' => 0, 'path' => '/admin', 'secure' => $https, 'httponly' => true, 'samesite' => 'Strict']);
session_start();

const SESSION_HOURS = 12;

function admin_ready(): ?string {
  if (!cfg('admin_password')) return 'The admin password is not set yet. Add \'admin_password\' to artful-config.php (see README).';
  if (!db_configured()) return 'The database is not connected yet. Add the \'db\' settings to artful-config.php (see README).';
  try { db(); } catch (Throwable $e) { return 'Could not connect to the database: ' . $e->getMessage(); }
  return null;
}

function logged_in(): bool {
  return !empty($_SESSION['admin']) && ($_SESSION['at'] ?? 0) > time() - SESSION_HOURS * 3600;
}
function require_login(): void {
  if (!logged_in()) { header('Location: login.php'); exit; }
  $_SESSION['at'] = time();
}

function check_password(string $given): bool {
  $real = (string)cfg('admin_password');
  return str_starts_with($real, '$2y$') ? password_verify($given, $real) : hash_equals($real, $given);
}

function client_ip(): string { return substr($_SERVER['REMOTE_ADDR'] ?? 'unknown', 0, 64); }
function too_many_attempts(): bool {
  $s = db()->prepare('SELECT COUNT(*) FROM login_attempts WHERE ip = ? AND at > ?');
  $s->execute([client_ip(), time() - 900]);
  return (int)$s->fetchColumn() >= 5;
}
function record_failed_login(): void {
  db()->prepare('INSERT INTO login_attempts (ip, at) VALUES (?, ?)')->execute([client_ip(), time()]);
  db()->prepare('DELETE FROM login_attempts WHERE at < ?')->execute([time() - 86400]);
}

function csrf(): string {
  if (empty($_SESSION['csrf'])) $_SESSION['csrf'] = bin2hex(random_bytes(16));
  return $_SESSION['csrf'];
}
function csrf_field(): string { return '<input type="hidden" name="csrf" value="' . e(csrf()) . '">'; }
function check_csrf(): void {
  if (!hash_equals($_SESSION['csrf'] ?? '', (string)($_POST['csrf'] ?? ''))) { http_response_code(400); exit('Session expired — please go back and try again.'); }
}

function flash(?string $msg = null): ?string {
  if ($msg !== null) { $_SESSION['flash'] = $msg; return null; }
  $m = $_SESSION['flash'] ?? null; unset($_SESSION['flash']); return $m;
}

function badge(string $kind, string $value): string {
  $labels = $kind === 'pay' ? PAYMENT : ($kind === 'enq' ? ENQUIRY_STATUS : STAGES);
  return '<span class="b b-' . e($kind) . '-' . e($value) . '">' . e($labels[$value] ?? $value) . '</span>';
}

function page_start(string $title, string $active = ''): void {
  $nav = ['index.php' => 'Orders', 'new-order.php' => '+ New order', 'customers.php' => 'Customers', 'products.php' => 'Custom products', 'enquiries.php' => 'Enquiries'];
  echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow"><title>' . e($title) . ' · Admin · The Artful Products</title>
  <link rel="icon" href="../assets/img/mark.svg"><link rel="stylesheet" href="admin.css?v=5"></head><body>
  <header class="top"><a class="brand" href="index.php"><img src="../assets/img/logo-main.svg" alt="The Artful Products"><span>Admin</span></a>';
  if (logged_in()) {
    echo '<nav>';
    foreach ($nav as $href => $label) echo '<a href="' . $href . '"' . ($active === $href ? ' class="on"' : '') . '>' . $label . '</a>';
    echo '<a href="../" target="_blank">View shop ↗</a><a href="logout.php" class="out">Log out</a></nav>';
  }
  echo '</header><main class="wrap">';
  if ($m = flash()) echo '<div class="flash">' . e($m) . '</div>';
}
function page_end(): void { echo '</main></body></html>'; }
