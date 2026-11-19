<?php
/* POST /api/create-order.php
   Re-prices the cart on the server, creates a Razorpay order for that amount,
   and saves the order (payment pending) so it shows in the admin dashboard.
   The browser never decides the price. */
require __DIR__ . '/_app.php';

$body = require_post();
[$keyId, $keySecret] = razorpay_keys();
$cat = catalog();

try {
  $t = compute_order((array)($body['items'] ?? []), ['code' => $body['code'] ?? '', 'wrap' => !empty($body['wrap'])], $cat['site'], $cat['products']);
} catch (InvalidArgumentException $e) {
  send_json(400, ['error' => $e->getMessage()]);
}

$c = (array)($body['customer'] ?? []);
if (empty($c['name']) || empty($c['phone']) || empty($c['address']) || !preg_match('/^\d{6}$/', (string)($c['pin'] ?? '')))
  send_json(400, ['error' => 'Please fill in your delivery details']);
if (!empty($c['email']) && !filter_var($c['email'], FILTER_VALIDATE_EMAIL)) send_json(400, ['error' => 'Please check your email address']);
$note = (string)($body['note'] ?? '');

// Razorpay notes (max 15 fields × 256 chars): also visible on the payment in the Razorpay dashboard
$items = implode('; ', array_map(function ($l) {
  $extra = array_filter([$l['colour'], $l['opt']]);
  return $l['name'] . ($extra ? ' (' . implode(', ', $extra) . ')' : '') . ' x' . $l['qty'];
}, $t['lines']));
$notes = [
  'customer' => clip("{$c['name']} · {$c['phone']} · " . ($c['email'] ?? '')),
  'address' => clip("{$c['address']}, " . ($c['city'] ?? '') . " {$c['pin']}"),
  'items' => clip($items),
  'personalisation' => clip(implode(' | ', array_filter(array_column($t['lines'], 'note')))) ?: '-',
  'extras' => clip(implode(' · ', array_filter([$t['code'] ? "code {$t['code']} -Rs{$t['disc']}" : '', $t['wrap'] ? 'gift wrap' : '', $note ? "note: $note" : '']))) ?: '-',
];

if (cfg('mock_razorpay')) {
  // LOCAL TESTING ONLY — never set mock_razorpay on the live server
  $order = ['id' => 'order_MOCK' . bin2hex(random_bytes(6)), 'amount' => $t['total'] * 100, 'currency' => 'INR'];
} else {
  $ch = curl_init('https://api.razorpay.com/v1/orders');
  curl_setopt_array($ch, [
    CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 20,
    CURLOPT_USERPWD => "$keyId:$keySecret",
    CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
    CURLOPT_POSTFIELDS => json_encode(['amount' => (int)round($t['total'] * 100), 'currency' => 'INR', 'receipt' => 'tap_' . time(), 'notes' => $notes]),
  ]);
  $raw = curl_exec($ch);
  $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
  curl_close($ch);
  $order = json_decode($raw ?: '', true);
  if ($status < 200 || $status >= 300 || empty($order['id'])) {
    error_log('Razorpay order error ' . $status . ' ' . $raw);
    send_json(502, ['error' => "Couldn't start the payment. Please try again."]);
  }
}

$orderNo = null;
if (db_configured()) {
  try { $orderNo = order_create($t, $c, $note, 'website', $order['id'], 'pending', '', !empty($body['marketing']))['order_no']; }
  catch (Throwable $e) { error_log('Order save failed: ' . $e->getMessage()); }   // payment still goes ahead; Razorpay keeps the details
}

send_json(200, ['id' => $order['id'], 'amount' => $order['amount'], 'currency' => $order['currency'] ?? 'INR', 'key' => $keyId, 'order_no' => $orderNo]);
