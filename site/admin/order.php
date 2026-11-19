<?php
require __DIR__ . '/_admin.php';
if (admin_ready()) { header('Location: login.php'); exit; }
require_login();

$o = order_get((int)($_GET['id'] ?? 0));
if (!$o) { http_response_code(404); page_start('Not found'); echo '<div class="empty">Order not found. <a href="index.php">Back to orders</a></div>'; page_end(); exit; }
$id = (int)$o['id'];

const COURIERS = [
  'Shiprocket' => 'https://shiprocket.co/tracking/%s',
  'Delhivery' => 'https://www.delhivery.com/track-v2/package/%s',
  'India Post' => '', 'DTDC' => '', 'Blue Dart' => '', 'Hand delivered' => '', 'Other' => '',
];

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
  check_csrf();
  $action = $_POST['action'] ?? '';
  if ($action === 'update') {
    $changes = []; $log = [];
    $stage = $_POST['stage'] ?? $o['stage'];
    if (isset(STAGES[$stage]) && $stage !== $o['stage']) { $changes['stage'] = $stage; $log[] = 'Stage: ' . STAGES[$o['stage']] . ' → ' . STAGES[$stage]; }
    $pay = $_POST['payment_status'] ?? $o['payment_status'];
    if (isset(PAYMENT[$pay]) && $pay !== $o['payment_status']) { $changes['payment_status'] = $pay; $log[] = 'Payment: ' . PAYMENT[$o['payment_status']] . ' → ' . PAYMENT[$pay]; }
    foreach (['courier' => 60, 'tracking_no' => 80, 'tracking_url' => 255] as $f => $max) {
      $v = clip($_POST[$f] ?? '', $max);
      if ($v !== (string)$o[$f]) { $changes[$f] = $v; $log[] = ucfirst(str_replace('_', ' ', $f)) . ': ' . ($v ?: '—'); }
    }
    // build the tracking link automatically for couriers we know
    $courier = $changes['courier'] ?? $o['courier']; $trk = $changes['tracking_no'] ?? $o['tracking_no'];
    if ($trk && !($changes['tracking_url'] ?? $o['tracking_url']) && !empty(COURIERS[$courier])) $changes['tracking_url'] = sprintf(COURIERS[$courier], rawurlencode($trk));
    $notes = (string)($_POST['admin_notes'] ?? '');
    if ($notes !== (string)$o['admin_notes']) $changes['admin_notes'] = mb_substr($notes, 0, 5000);
    order_update($id, $changes);
    foreach ($log as $l) add_event($id, 'update', $l);

    $o = order_get($id);
    if (($changes['stage'] ?? '') === 'shipped' && !empty($_POST['email_customer']) && !(int)$o['shipped_email_sent']) {
      email_shipped($o);
      order_update($id, ['shipped_email_sent' => 1]);
      add_event($id, 'email', 'Shipping email sent to ' . $o['email']);
    }
    flash($changes ? 'Saved.' : 'Nothing changed.');
  } elseif ($action === 'resend') {
    email_order_confirmation($o);
    add_event($id, 'email', 'Order confirmation re-sent to ' . $o['email']);
    flash('Confirmation email sent again.');
  } elseif ($action === 'shipped_email') {
    email_shipped($o);
    order_update($id, ['shipped_email_sent' => 1]);
    add_event($id, 'email', 'Shipping email sent to ' . $o['email']);
    flash('Shipping email sent.');
  } elseif ($action === 'customer') {
    $f = [];
    foreach (['name' => 120, 'phone' => 30, 'email' => 160, 'address' => 500, 'city' => 80, 'pin' => 10] as $k => $max) $f[$k] = clip($_POST[$k] ?? '', $max);
    order_update($id, $f);
    add_event($id, 'update', 'Customer details edited');
    flash('Customer details saved.');
  } elseif ($action === 'archive' || $action === 'restore') {
    $arch = $action === 'archive' ? 1 : 0;
    order_update($id, ['archived' => $arch]);
    add_event($id, 'update', $arch ? 'Archived' : 'Restored from archive');
    flash($o['order_no'] . ($arch ? ' archived. It no longer appears in your lists or totals; find it under Archived.' : ' restored.'));
    if ($arch) { header('Location: index.php'); exit; }
  } elseif ($action === 'delete') {
    // permanent: only allowed for archived orders, and the order number must be typed to confirm
    if (!(int)$o['archived']) { flash('Archive the order first; only archived orders can be deleted.'); }
    elseif (strtoupper(trim((string)($_POST['confirm'] ?? ''))) !== strtoupper($o['order_no'])) { flash('Type the order number exactly to delete it.'); }
    else {
      db()->prepare('DELETE FROM order_events WHERE order_id = ?')->execute([$id]);
      db()->prepare('DELETE FROM orders WHERE id = ?')->execute([$id]);
      flash($o['order_no'] . ' deleted permanently.');
      header('Location: index.php?view=archived'); exit;
    }
  }
  header('Location: order.php?id=' . $id); exit;
}

$items = order_items($o);
$events = order_events($id);
$phone = preg_replace('/\D/', '', $o['phone']);
if (strlen($phone) === 10) $phone = '91' . $phone;
$first = strtok($o['name'], ' ');
$wa = fn($text) => 'https://wa.me/' . $phone . '?text=' . rawurlencode($text);
$templates = [
  'Ask for route' => "Hi $first! Thank you for your order {$o['order_no']} with The Artful Products. Please send us your route — a GPX file, a Strava/Garmin link, or the event name — and we'll prepare your preview.",
  'Preview ready' => "Hi $first, here's the preview for your order {$o['order_no']}. Please reply \"Approved\" or tell us what to change.",
  'Shipped' => "Hi $first, your order {$o['order_no']} has shipped!" . ($o['tracking_url'] ? " Track it here: {$o['tracking_url']}" : ($o['tracking_no'] ? " Tracking number: {$o['tracking_no']} ({$o['courier']})" : '')),
];

page_start($o['order_no']);
?>
<p class="back"><a href="index.php">← All orders</a></p>
<div class="ohead">
  <div><h1><?= e($o['order_no']) ?></h1>
    <p class="muted"><?= e(date('d M Y, g:ia', strtotime($o['created_at']))) ?> · <?= $o['source'] === 'manual' ? 'Added by hand' : 'Website' ?><?= $o['rzp_payment_id'] ? ' · ' . e($o['rzp_payment_id']) : '' ?></p></div>
  <div class="ohead-b"><?= (int)$o['archived'] ? '<span class="b">Archived</span>' : '' ?> <?= badge('pay', $o['payment_status']) ?> <?= badge('stage', $o['stage']) ?> <b class="big"><?= inr($o['total']) ?></b></div>
</div>
<?php if ((int)$o['archived']): ?><p class="warn" style="margin-bottom:16px">This order is archived: it's hidden from your lists, totals and the Customers page.</p><?php endif; ?>

<div class="grid2">
  <section class="card">
    <h2>Items</h2>
    <?php foreach ($items as $l): ?>
      <div class="line">
        <div><b><?= e($l['name']) ?></b> <span class="muted">×<?= (int)$l['qty'] ?></span>
          <?php $x = array_filter([$l['colour'] ?? '', $l['opt'] ?? '']); if ($x): ?><br><span class="muted"><?= e(implode(' · ', $x)) ?></span><?php endif; ?>
          <?php if (!empty($l['note'])): ?><div class="note">“<?= e($l['note']) ?>”</div><?php endif; ?>
          <?php if (!empty($l['personal'])): ?><span class="tag">Personalised</span><?php endif; ?>
        </div>
        <b><?= inr($l['total']) ?></b>
      </div>
    <?php endforeach; ?>
    <div class="sums">
      <div><span>Subtotal</span><span><?= inr($o['sub']) ?></span></div>
      <?php if ((int)$o['disc']): ?><div><span>Discount (<?= e($o['code']) ?>)</span><span>−<?= inr($o['disc']) ?></span></div><?php endif; ?>
      <div><span>Shipping</span><span><?= (int)$o['ship'] ? inr($o['ship']) : 'Free' ?></span></div>
      <?php if ((int)$o['wrap']): ?><div><span>Gift wrap</span><span><?= inr($o['wrap']) ?></span></div><?php endif; ?>
      <div class="tot"><span>Total</span><span><?= inr($o['total']) ?></span></div>
    </div>
    <?php if ($o['note']): ?><p class="onote"><b>Customer's note:</b> <?= nl2br(e($o['note'])) ?></p><?php endif; ?>
  </section>

  <section class="card">
    <h2>Customer</h2>
    <p class="cust"><b><?= e($o['name']) ?></b><br><?= nl2br(e($o['address'])) ?><br><?= e($o['city']) ?> <?= e($o['pin']) ?></p>
    <div class="actions">
      <?php if ($phone): ?><a class="btn wa" href="<?= e($wa("Hi $first,")) ?>" target="_blank" rel="noopener">WhatsApp</a><a class="btn ghost" href="tel:<?= e($o['phone']) ?>">Call <?= e($o['phone']) ?></a><?php endif; ?>
      <?php if ($o['email']): ?><a class="btn ghost" href="mailto:<?= e($o['email']) ?>?subject=<?= e(rawurlencode('Your order ' . $o['order_no'])) ?>">Email</a><?php endif; ?>
    </div>
    <?php if ($phone): ?>
      <p class="label">Quick WhatsApp messages</p>
      <div class="actions"><?php foreach ($templates as $label => $text): ?><a class="btn ghost sm" href="<?= e($wa($text)) ?>" target="_blank" rel="noopener"><?= e($label) ?></a><?php endforeach; ?></div>
    <?php endif; ?>
    <details class="edit"><summary>Edit customer details</summary>
      <form method="post" class="form">
        <?= csrf_field() ?><input type="hidden" name="action" value="customer">
        <?php foreach (['name' => 'Name', 'phone' => 'Phone', 'email' => 'Email', 'city' => 'City', 'pin' => 'PIN'] as $k => $label): ?>
          <label><?= $label ?><input name="<?= $k ?>" value="<?= e($o[$k]) ?>"></label>
        <?php endforeach; ?>
        <label class="full">Address<textarea name="address" rows="2"><?= e($o['address']) ?></textarea></label>
        <button class="btn">Save customer</button>
      </form>
    </details>
  </section>
</div>

<div class="grid2">
  <section class="card">
    <h2>Update order</h2>
    <form method="post" class="form">
      <?= csrf_field() ?><input type="hidden" name="action" value="update">
      <label>Stage<select name="stage"><?php foreach (STAGES as $k => $label): ?><option value="<?= $k ?>" <?= $k === $o['stage'] ? 'selected' : '' ?>><?= $label ?></option><?php endforeach; ?></select></label>
      <label>Payment<select name="payment_status"><?php foreach (PAYMENT as $k => $label): ?><option value="<?= $k ?>" <?= $k === $o['payment_status'] ? 'selected' : '' ?>><?= $label ?></option><?php endforeach; ?></select></label>
      <label>Courier<select name="courier"><option value="">—</option><?php foreach (COURIERS as $k => $_): ?><option <?= $k === $o['courier'] ? 'selected' : '' ?>><?= $k ?></option><?php endforeach; ?></select></label>
      <label>Tracking number<input name="tracking_no" value="<?= e($o['tracking_no']) ?>"></label>
      <label class="full">Tracking link <small class="muted">(filled in automatically for Shiprocket and Delhivery)</small><input name="tracking_url" value="<?= e($o['tracking_url']) ?>" placeholder="https://…"></label>
      <label class="full chk"><input type="checkbox" name="email_customer" value="1" <?= (int)$o['shipped_email_sent'] ? '' : 'checked' ?>> Email the customer when I mark it <b>Shipped</b><?= (int)$o['shipped_email_sent'] ? ' (already sent once)' : '' ?></label>
      <label class="full">Private notes<textarea name="admin_notes" rows="3" placeholder="Only you see this"><?= e($o['admin_notes']) ?></textarea></label>
      <button class="btn primary">Save changes</button>
    </form>
    <div class="actions" style="margin-top:14px">
      <form method="post"><?= csrf_field() ?><input type="hidden" name="action" value="resend"><button class="btn ghost sm" <?= $o['email'] ? '' : 'disabled' ?>>Re-send confirmation email</button></form>
      <form method="post"><?= csrf_field() ?><input type="hidden" name="action" value="shipped_email"><button class="btn ghost sm" <?= $o['email'] ? '' : 'disabled' ?>>Send shipping email</button></form>
    </div>
  </section>

  <section class="card">
    <h2>Timeline</h2>
    <ol class="timeline">
      <?php foreach ($events as $ev): ?>
        <li><b><?= e($ev['message']) ?></b><small><?= e(date('d M Y, g:ia', strtotime($ev['at']))) ?></small></li>
      <?php endforeach; ?>
    </ol>
  </section>
</div>

<section class="card danger-zone">
  <h2>Archive or delete</h2>
  <?php if (!(int)$o['archived']): ?>
    <p class="muted">Archiving hides this order from your lists, sales totals and the Customers page (useful for test orders). You can restore it any time from <b>Orders → Archived</b>.</p>
    <form method="post"><?= csrf_field() ?><input type="hidden" name="action" value="archive"><button class="btn">Archive this order</button></form>
  <?php else: ?>
    <div class="actions">
      <form method="post"><?= csrf_field() ?><input type="hidden" name="action" value="restore"><button class="btn">Restore order</button></form>
    </div>
    <form method="post" class="form compact del" onsubmit="return confirm('Delete <?= e($o['order_no']) ?> permanently? This cannot be undone.')">
      <?= csrf_field() ?><input type="hidden" name="action" value="delete">
      <label class="grow">Delete permanently: type <b><?= e($o['order_no']) ?></b> to confirm<input name="confirm" autocomplete="off" placeholder="<?= e($o['order_no']) ?>"></label>
      <button class="btn danger">Delete forever</button>
    </form>
  <?php endif; ?>
</section>
<?php page_end();
