<?php
/* POST /api/verify-payment.php
   Checks Razorpay's signature, so "payment received" is only shown for genuine payments,
   then marks the saved order as paid and sends the confirmation emails.
   Signature = HMAC-SHA256(order_id . "|" . payment_id, key_secret) */
require __DIR__ . '/_app.php';

$body = require_post();
[, $keySecret] = razorpay_keys();

$orderId = (string)($body['razorpay_order_id'] ?? '');
$paymentId = (string)($body['razorpay_payment_id'] ?? '');
$signature = (string)($body['razorpay_signature'] ?? '');
if ($orderId === '' || $paymentId === '' || $signature === '') send_json(400, ['error' => 'Missing payment details']);

$expected = hash_hmac('sha256', $orderId . '|' . $paymentId, $keySecret);
if (!hash_equals($expected, $signature)) {
  error_log("Razorpay signature mismatch $orderId $paymentId");
  send_json(400, ['error' => 'Payment could not be verified']);
}

$orderNo = null;
if (db_configured()) {
  try {
    $o = order_by_rzp($orderId);
    if ($o) $orderNo = order_mark_paid($o, $paymentId, 'checkout')['order_no'];
    else error_log("Verified payment for unknown order $orderId");
  } catch (Throwable $e) { error_log('Order update failed: ' . $e->getMessage()); }
}
send_json(200, ['ok' => true, 'payment_id' => $paymentId, 'order_id' => $orderId, 'order_no' => $orderNo]);
