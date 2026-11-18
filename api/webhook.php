<?php
/* POST /api/webhook.php — Razorpay webhook (Razorpay dashboard → Webhooks).
   Razorpay calls this directly when a payment succeeds or fails, so orders are marked
   paid even if the customer closes their browser right after paying.
   Events to tick: payment.captured, payment.failed, order.paid
   Secret: the same value as 'webhook_secret' in artful-config.php */
require __DIR__ . '/_app.php';

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') send_json(405, ['error' => 'Use POST']);
$secret = cfg('webhook_secret');
if (!$secret) send_json(503, ['error' => 'Webhook not configured']);

$raw = file_get_contents('php://input') ?: '';
$sig = $_SERVER['HTTP_X_RAZORPAY_SIGNATURE'] ?? '';
if (!hash_equals(hash_hmac('sha256', $raw, $secret), $sig)) send_json(400, ['error' => 'Bad signature']);

$event = json_decode($raw, true) ?: [];
$type = $event['event'] ?? '';
$pay = $event['payload']['payment']['entity'] ?? [];
$rzpOrderId = $pay['order_id'] ?? ($event['payload']['order']['entity']['id'] ?? '');

if (!db_configured() || !$rzpOrderId) send_json(200, ['ok' => true, 'ignored' => true]);

try {
  $o = order_by_rzp($rzpOrderId);
  if (!$o) send_json(200, ['ok' => true, 'unknown_order' => true]);
  if ($type === 'payment.captured' || $type === 'order.paid') {
    order_mark_paid($o, (string)($pay['id'] ?? ''), 'webhook', (string)($pay['method'] ?? ''));
  } elseif ($type === 'payment.failed') {
    order_mark_failed($o, (string)($pay['error_description'] ?? 'failed'));
  }
} catch (Throwable $e) {
  error_log('Webhook error: ' . $e->getMessage());
  send_json(500, ['error' => 'Server error']);   // Razorpay retries automatically
}
send_json(200, ['ok' => true]);
