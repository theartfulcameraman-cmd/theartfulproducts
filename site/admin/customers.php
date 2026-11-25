<?php
/* Customers: everyone who has ordered (website or manual), grouped by email — or by phone when
   there's no email — with order count, total spent, first/last order and marketing consent.
   Plus newsletter sign-ups. Only message people marked "Agreed" (consent at checkout / sign-up). */
require __DIR__ . '/_admin.php';
if (admin_ready()) { header('Location: login.php'); exit; }
require_login();

$view = in_array($_GET['view'] ?? '', ['all', 'repeat', 'consent', 'subscribers'], true) ? $_GET['view'] : 'all';
$q = trim((string)($_GET['q'] ?? ''));

/* One row per customer. Two orders belong to the same customer if they share the EMAIL or the PHONE
   (either one is enough, and it chains: A~B by phone, B~C by email → A, B, C are one customer). */
$rows = db()->query("SELECT id, name, phone, email, city, total, created_at, marketing_ok, order_no FROM orders
                     WHERE payment_status IN ('paid','advance','cod') AND stage <> 'cancelled' AND COALESCE(archived,0) = 0 ORDER BY id ASC")->fetchAll();
function norm_phone(string $p): string {
  $d = preg_replace('/\D/', '', $p);
  if (strlen($d) === 12 && str_starts_with($d, '91')) $d = substr($d, 2);
  if (strlen($d) === 11 && $d[0] === '0') $d = substr($d, 1);
  return strlen($d) >= 8 ? $d : '';
}
// union-find over orders, joined through shared email / phone
$parent = [];
$find = function ($x) use (&$parent, &$find) { return $parent[$x] === $x ? $x : ($parent[$x] = $find($parent[$x])); };
$owner = [];   // 'e:email' / 'p:phone' → first order id seen with it
foreach ($rows as $o) {
  $id = (int)$o['id']; $parent[$id] = $id;
  foreach (array_filter(['e:' . strtolower(trim($o['email'])) => trim($o['email']) !== '', 'p:' . norm_phone($o['phone']) => norm_phone($o['phone']) !== '']) as $k => $_) {
    if (isset($owner[$k])) { $a = $find($id); $b = $find($owner[$k]); if ($a !== $b) $parent[$a] = $b; }
    else $owner[$k] = $id;
  }
}
$cust = [];
foreach ($rows as $o) {
  $key = $find((int)$o['id']);
  if (!isset($cust[$key])) $cust[$key] = ['name' => '', 'phones' => [], 'emails' => [], 'city' => '', 'orders' => 0, 'spent' => 0, 'first' => $o['created_at'], 'last' => '', 'consent' => 0, 'last_no' => ''];
  $c = &$cust[$key];
  $c['name'] = $o['name'] ?: $c['name']; $c['city'] = $o['city'] ?: $c['city'];
  if ($p = norm_phone($o['phone'])) $c['phones'][$p] = $o['phone'];
  if ($e = strtolower(trim($o['email']))) $c['emails'][$e] = $e;
  $c['orders']++; $c['spent'] += (int)$o['total']; $c['last'] = $o['created_at']; $c['last_no'] = $o['order_no'];
  $c['consent'] = max($c['consent'], (int)$o['marketing_ok']);
  unset($c);
}
$subs = db()->query('SELECT * FROM subscribers WHERE unsubscribed = 0 ORDER BY id DESC')->fetchAll();
$subEmails = array_flip(array_map(fn($s) => strtolower($s['email']), $subs));
foreach ($cust as &$c) {
  foreach ($c['emails'] as $e) if (isset($subEmails[$e])) $c['consent'] = 1;   // also signed up to the newsletter
  $c['phone'] = implode(' / ', array_values($c['phones']));                     // the latest details come last
  $c['email'] = implode(' / ', array_values($c['emails']));
  $c['wa_phone'] = $c['phones'] ? end($c['phones']) : '';
  $c['mail_to'] = $c['emails'] ? end($c['emails']) : '';
}
unset($c);

$list = array_values($cust);
if ($view === 'repeat') $list = array_values(array_filter($list, fn($c) => $c['orders'] >= 2));
if ($view === 'consent') $list = array_values(array_filter($list, fn($c) => $c['consent']));
if ($q !== '') { $needle = strtolower($q); $list = array_values(array_filter($list, fn($c) => str_contains(strtolower($c['name'] . ' ' . $c['email'] . ' ' . $c['phone'] . ' ' . $c['city']), $needle))); }
usort($list, fn($a, $b) => strcmp($b['last'], $a['last']));

/* CSV export of the current view */
if (isset($_GET['export'])) {
  header('Content-Type: text/csv; charset=utf-8');
  header('Content-Disposition: attachment; filename="artful-customers-' . $view . '-' . date('Y-m-d') . '.csv"');
  $out = fopen('php://output', 'w'); fwrite($out, "\xEF\xBB\xBF");
  $safe = fn($v) => is_string($v) && preg_match('/^[=+\-@]/', $v) ? "'" . $v : $v;
  if ($view === 'subscribers') {
    fputcsv($out, ['Email', 'Signed up', 'From']);
    foreach ($subs as $s) fputcsv($out, array_map($safe, [$s['email'], $s['created_at'], $s['source']]));
  } else {
    fputcsv($out, ['Name', 'Phone', 'Email', 'City', 'Orders', 'Total spent', 'First order', 'Last order', 'Agreed to offers']);
    foreach ($list as $c) fputcsv($out, array_map($safe, [$c['name'], $c['phone'], $c['email'], $c['city'], $c['orders'], $c['spent'], $c['first'], $c['last'], $c['consent'] ? 'Yes' : 'No']));
  }
  exit;
}

$all = count($cust);
$repeat = count(array_filter($cust, fn($c) => $c['orders'] >= 2));
$consent = count(array_filter($cust, fn($c) => $c['consent']));
$wa = function ($phone) { $d = preg_replace('/\D/', '', $phone); if (strlen($d) === 10) $d = '91' . $d; return $d ? 'https://wa.me/' . $d : ''; };

page_start('Customers', 'customers.php');
?>
<h1>Customers</h1>
<p class="muted">Everyone who has paid for an order (website and manual), plus newsletter sign-ups.
  Orders are matched to the same customer when <b>either</b> the phone number or the email is the same.
  Only send offers to people marked <b>Agreed</b>: they ticked the box at checkout or signed up.</p>

<div class="stats" style="grid-template-columns:repeat(4,1fr)">
  <a href="?view=all"><small>Customers</small><b><?= $all ?></b><span>with a paid order</span></a>
  <a href="?view=repeat"><small>Repeat customers</small><b><?= $repeat ?></b><span><?= $all ? round($repeat / $all * 100) : 0 ?>% ordered again</span></a>
  <a href="?view=consent"><small>Agreed to offers</small><b><?= $consent ?></b><span>OK to message</span></a>
  <a href="?view=subscribers"><small>Newsletter</small><b><?= count($subs) ?></b><span>email sign-ups</span></a>
</div>

<div class="bar">
  <div class="tabs">
    <?php foreach (['all' => 'All customers', 'repeat' => 'Repeat customers', 'consent' => 'Agreed to offers', 'subscribers' => 'Newsletter sign-ups'] as $k => $label): ?>
      <a href="?view=<?= $k ?>" class="<?= $k === $view ? 'on' : '' ?>"><?= $label ?></a>
    <?php endforeach; ?>
  </div>
  <form class="search" method="get">
    <input type="hidden" name="view" value="<?= e($view) ?>">
    <?php if ($view !== 'subscribers'): ?><input name="q" value="<?= e($q) ?>" placeholder="Search name, email, phone, city"><button class="btn">Search</button><?php endif; ?>
    <a class="btn ghost" href="?view=<?= e($view) ?>&q=<?= e(urlencode($q)) ?>&export=1">Export CSV</a>
  </form>
</div>

<?php if ($view === 'subscribers'): ?>
  <?php if (!$subs): ?><div class="empty">No sign-ups yet. Emails entered in the website's newsletter boxes appear here.</div><?php else: ?>
  <div class="table">
    <div class="tr th cust-sub"><span>Email</span><span>Signed up</span><span>From</span></div>
    <?php foreach ($subs as $s): ?>
      <div class="tr cust-sub"><span><a href="mailto:<?= e($s['email']) ?>"><?= e($s['email']) ?></a></span><span><?= e(date('d M Y', strtotime($s['created_at']))) ?></span><span class="muted"><?= e($s['source']) ?></span></div>
    <?php endforeach; ?>
  </div>
  <?php endif; ?>
<?php elseif (!$list): ?>
  <div class="empty"><?= $q ? 'No customers match your search.' : 'No customers here yet.' ?></div>
<?php else: ?>
  <div class="table">
    <div class="tr th cust"><span>Customer</span><span>Contact</span><span>Orders</span><span>Spent</span><span>Last order</span><span>Offers</span><span></span></div>
    <?php foreach ($list as $c): $w = $wa($c['wa_phone']); ?>
      <div class="tr cust">
        <span><b><?= e($c['name']) ?></b><small><?= e($c['city']) ?></small></span>
        <span><small><?= e($c['phone']) ?></small><small><?= e($c['email']) ?></small></span>
        <span class="num"><?= (int)$c['orders'] ?><?= $c['orders'] >= 2 ? ' <span class="tag">Repeat</span>' : '' ?></span>
        <span class="num"><?= inr($c['spent']) ?></span>
        <span><small><?= e(date('d M Y', strtotime($c['last']))) ?> · <a href="index.php?view=all&q=<?= e(urlencode($c['last_no'])) ?>"><?= e($c['last_no']) ?></a></small></span>
        <span><?= $c['consent'] ? '<span class="b b-pay-paid">Agreed</span>' : '<span class="b">No</span>' ?></span>
        <span class="actions"><?php if ($w): ?><a class="btn wa sm" href="<?= e($w) ?>" target="_blank" rel="noopener">WhatsApp</a><?php endif; ?><?php if ($c['mail_to']): ?><a class="btn ghost sm" href="mailto:<?= e($c['mail_to']) ?>">Email</a><?php endif; ?></span>
      </div>
    <?php endforeach; ?>
  </div>
<?php endif; ?>
<?php page_end();
