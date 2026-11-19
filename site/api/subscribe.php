<?php
/* POST /api/subscribe.php {email, source, website(honeypot)} — saves newsletter / "notify me" sign-ups
   so they appear in Admin → Customers. Signing up is explicit consent to receive updates. */
require __DIR__ . '/_app.php';

$body = require_post();
if (!empty($body['website'])) send_json(200, ['ok' => true]);           // spam bot
$email = strtolower(trim((string)($body['email'] ?? '')));
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) send_json(400, ['error' => 'Please enter a valid email address']);
$source = preg_replace('/[^a-z0-9_-]/', '', strtolower((string)($body['source'] ?? 'website'))) ?: 'website';
if (!db_configured()) send_json(200, ['ok' => true, 'saved' => false]);
try {
  $s = db()->prepare('SELECT id FROM subscribers WHERE email = ?'); $s->execute([$email]);
  if ($id = $s->fetchColumn()) db()->prepare('UPDATE subscribers SET unsubscribed = 0 WHERE id = ?')->execute([$id]);
  else db()->prepare('INSERT INTO subscribers (email, source, created_at, unsubscribed) VALUES (?,?,?,0)')->execute([$email, substr($source, 0, 40), now()]);
  send_json(200, ['ok' => true, 'saved' => true]);
} catch (Throwable $e) {
  error_log('Subscribe failed: ' . $e->getMessage());
  send_json(200, ['ok' => true, 'saved' => false]);
}
