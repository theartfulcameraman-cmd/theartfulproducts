<?php
/* Download orders as a CSV file (opens in Excel / Google Sheets). Uses the same filter as the orders list. */
require __DIR__ . '/_admin.php';
if (admin_ready()) { header('Location: login.php'); exit; }
require_login();

$views = order_views();
$where = ($views[$_GET['view'] ?? 'all'] ?? $views['all'])[1]; $args = [];
$q = trim((string)($_GET['q'] ?? ''));
if ($q !== '') { $where .= ' AND (order_no LIKE ? OR name LIKE ? OR phone LIKE ? OR email LIKE ? OR city LIKE ?)'; $args = array_fill(0, 5, "%$q%"); }
$s = db()->prepare("SELECT * FROM orders WHERE $where ORDER BY id DESC"); $s->execute($args);

header('Content-Type: text/csv; charset=utf-8');
header('Content-Disposition: attachment; filename="artful-orders-' . date('Y-m-d') . '.csv"');
$out = fopen('php://output', 'w');
fwrite($out, "\xEF\xBB\xBF");   // so Excel reads ₹ and Indian names correctly
fputcsv($out, ['Order', 'Date', 'Source', 'Payment', 'Method', 'Stage', 'Name', 'Phone', 'Email', 'Address', 'City', 'PIN', 'Items', 'Personalisation', 'Subtotal', 'Discount', 'Code', 'Shipping', 'Gift wrap', 'Total', 'Courier', 'Tracking', 'Razorpay payment', 'Notes']);
// guard against spreadsheet formula injection from customer-typed text
$safe = fn($v) => is_string($v) && preg_match('/^[=+\-@]/', $v) ? "'" . $v : $v;
while ($o = $s->fetch()) {
  $items = order_items($o);
  fputcsv($out, array_map($safe, [
    $o['order_no'], $o['created_at'], $o['source'], PAYMENT[$o['payment_status']] ?? $o['payment_status'], $o['payment_method'], STAGES[$o['stage']] ?? $o['stage'],
    $o['name'], $o['phone'], $o['email'], $o['address'], $o['city'], $o['pin'],
    implode('; ', array_map(fn($l) => $l['name'] . ' x' . $l['qty'] . (array_filter([$l['colour'] ?? '', $l['opt'] ?? '']) ? ' (' . implode(', ', array_filter([$l['colour'] ?? '', $l['opt'] ?? ''])) . ')' : ''), $items)),
    implode(' | ', array_filter(array_column($items, 'note'))),
    $o['sub'], $o['disc'], $o['code'], $o['ship'], $o['wrap'], $o['total'], $o['courier'], $o['tracking_no'], $o['rzp_payment_id'], $o['admin_notes'],
  ]));
}
fclose($out);
