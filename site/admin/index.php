<?php
require __DIR__ . '/_admin.php';
if ($p = admin_ready()) { header('Location: login.php'); exit; }
require_login();

/* filters: "all" is the default; "todo" = every live order not shipped yet, paid or not; archived orders only in "Archived" */
$views = order_views();
$view = isset($views[$_GET['view'] ?? '']) ? $_GET['view'] : 'all';

/* simple Paid / Not paid tag, with the detail underneath */
function paid_tag(array $o): string {
  $st = $o['payment_status'];
  if ($st === 'paid') return '<span class="b b-pay-paid">Paid</span>';
  if ($st === 'refunded') return '<span class="b b-pay-refunded">Refunded</span>';
  if ($st === 'advance') return '<span class="b b-pay-advance">Advance ' . inr($o['advance_paid']) . '</span><small>' . inr(max(0, $o['total'] - $o['advance_paid'])) . ' due</small>';
  $why = ['cod' => 'Cash on delivery', 'failed' => 'Payment failed', 'pending' => 'Awaiting payment'][$st] ?? $st;
  return '<span class="b b-pay-unpaid">Not paid</span><small>' . e($why) . '</small>';
}
$q = trim((string)($_GET['q'] ?? ''));

$where = $views[$view][1]; $args = [];
if ($q !== '') {
  $where .= ' AND (order_no LIKE ? OR name LIKE ? OR phone LIKE ? OR email LIKE ? OR city LIKE ?)';
  $like = '%' . $q . '%'; $args = [$like, $like, $like, $like, $like];
}
$page = max(1, (int)($_GET['p'] ?? 1)); $per = 50;
$total = db()->prepare("SELECT COUNT(*) FROM orders WHERE $where"); $total->execute($args); $count = (int)$total->fetchColumn();
$s = db()->prepare("SELECT * FROM orders WHERE $where ORDER BY created_at DESC, id DESC LIMIT $per OFFSET " . (($page - 1) * $per));
$s->execute($args); $orders = $s->fetchAll();

/* view counts + headline numbers */
$counts = [];
foreach ($views as $k => [, $w]) { $c = db()->query("SELECT COUNT(*) FROM orders WHERE $w"); $counts[$k] = (int)$c->fetchColumn(); }
$sum = function (string $since) {
  $s = db()->prepare("SELECT COUNT(*) n, COALESCE(SUM(total),0) t FROM orders WHERE payment_status IN ('paid','advance','cod') AND stage <> 'cancelled' AND COALESCE(archived,0) = 0 AND created_at >= ?");
  $s->execute([$since]); return $s->fetch();
};
$today = $sum(date('Y-m-d 00:00:00'));
$week = $sum(date('Y-m-d 00:00:00', strtotime('monday this week')));
$month = $sum(date('Y-m-01 00:00:00'));
$notPaid = (int)db()->query("SELECT COUNT(*) FROM orders WHERE {$views['todo'][1]} AND payment_status NOT IN ('paid','refunded')")->fetchColumn();
$newEnq = (int)db()->query("SELECT COUNT(*) FROM enquiries WHERE status = 'new' AND COALESCE(archived,0) = 0")->fetchColumn();

page_start('Orders', 'index.php');
?>
<div class="stats">
  <div><small>Today</small><b><?= inr($today['t']) ?></b><span><?= (int)$today['n'] ?> orders</span></div>
  <div><small>This week</small><b><?= inr($week['t']) ?></b><span><?= (int)$week['n'] ?> orders</span></div>
  <div><small>This month</small><b><?= inr($month['t']) ?></b><span><?= (int)$month['n'] ?> orders</span></div>
  <a href="?view=todo"><small>To do</small><b><?= $counts['todo'] ?></b><span><?= $counts['awaiting_route'] ?> awaiting route · <?= $notPaid ?> with money due</span></a>
  <a href="enquiries.php"><small>New enquiries</small><b><?= $newEnq ?></b><span>bulk &amp; contact</span></a>
</div>

<div class="bar">
  <div class="tabs">
    <?php foreach ($views as $k => [$label]): ?>
      <a href="?view=<?= $k ?>" class="<?= $k === $view ? 'on' : '' ?>"><?= e($label) ?> <em><?= $counts[$k] ?></em></a>
    <?php endforeach; ?>
  </div>
  <form class="search" method="get">
    <input type="hidden" name="view" value="<?= e($view) ?>">
    <input name="q" value="<?= e($q) ?>" placeholder="Search order no, name, phone, email, city">
    <button class="btn">Search</button>
    <a class="btn ghost" href="export.php?view=<?= e($view) ?>&q=<?= e(urlencode($q)) ?>">Export CSV</a>
  </form>
</div>

<?php if (!$orders): ?>
  <div class="empty"><?= $q ? 'No orders match your search.' : 'No orders here yet.' ?></div>
<?php else: ?>
<div class="table">
  <div class="tr th"><span>Order</span><span>Customer</span><span>Items</span><span>Total</span><span>Paid?</span><span>Status</span></div>
  <?php foreach ($orders as $o):
    $items = order_items($o);
    $summary = implode(', ', array_map(fn($l) => $l['name'] . ($l['qty'] > 1 ? ' ×' . $l['qty'] : ''), $items));
  ?>
  <a class="tr" href="order.php?id=<?= (int)$o['id'] ?>">
    <span><b><?= e($o['order_no']) ?></b><small><?= e(date('d M, g:ia', strtotime($o['created_at']))) ?><?= $o['source'] === 'manual' ? ' · manual' : '' ?></small></span>
    <span><b><?= e($o['name']) ?></b><small><?= e(implode(' · ', array_filter([$o['city'], $o['phone']]))) ?></small></span>
    <span class="items"><?= e($summary) ?></span>
    <span class="num"><?= inr($o['total']) ?></span>
    <span><?= paid_tag($o) ?></span>
    <span><?= badge('stage', $o['stage']) ?></span>
  </a>
  <?php endforeach; ?>
</div>
<?php if ($count > $per): ?>
  <div class="pager">
    <?php if ($page > 1): ?><a class="btn ghost" href="?view=<?= e($view) ?>&q=<?= e(urlencode($q)) ?>&p=<?= $page - 1 ?>">← Newer</a><?php endif; ?>
    <span>Page <?= $page ?> of <?= (int)ceil($count / $per) ?></span>
    <?php if ($page * $per < $count): ?><a class="btn ghost" href="?view=<?= e($view) ?>&q=<?= e(urlencode($q)) ?>&p=<?= $page + 1 ?>">Older →</a><?php endif; ?>
  </div>
<?php endif; ?>
<?php endif; ?>
<?php page_end();
