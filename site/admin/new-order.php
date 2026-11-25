<?php
/* Add an order by hand — expo stall, WhatsApp, phone, corporate or any custom order —
   so every order lives in one place. Items can be website products, your custom products
   (admin-only, see products.php) or a one-off item typed in on the spot. Prices are editable. */
require __DIR__ . '/_admin.php';
if (admin_ready()) { header('Location: login.php'); exit; }
require_login();

$cat = catalog();
$site = array_values(array_filter($cat['products'], fn($p) => ($p['status'] ?? 'live') === 'live' && !empty($p['price'])));
$byId = []; foreach ($cat['products'] as $p) $byId[$p['id']] = $p;
$custom = custom_products();
$error = '';

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
  check_csrf();
  try {
    $lines = [];
    foreach ((array)($_POST['item'] ?? []) as $row) {
      $id = (string)($row['id'] ?? '');
      if ($id === '') continue;
      $qty = max(1, min(9999, (int)($row['qty'] ?? 1)));
      $colour = clip($row['colour'] ?? '', 40);
      if (str_starts_with($id, 'c:')) {                       // custom product
        $cp = custom_product((int)substr($id, 2));
        if (!$cp) throw new InvalidArgumentException('That custom product no longer exists');
        $name = $cp['name']; $personal = (bool)$cp['personal']; $default = (int)$cp['price']; $sku = custom_sku($cp);
      } elseif ($id === 'oneoff') {                            // typed in for this order only
        $name = clip($row['name'] ?? '', 160);
        if ($name === '') throw new InvalidArgumentException('Please name the one-off item');
        $personal = !empty($row['personal']); $default = 0; $sku = 'TAP-ONEOFF';
      } elseif (isset($byId[$id])) {                           // website product
        $p = $byId[$id]; $name = $p['name']; $personal = !empty($p['personal']); $default = unit_price($p, $qty, 0);
        $names = array_column($p['colours'] ?? [], 'name');
        if ($names && !in_array($colour, $names, true)) $colour = $names[0];
        $sku = product_sku($p, $colour);
      } else throw new InvalidArgumentException('Unknown product');
      $unit = trim((string)($row['price'] ?? '')) === '' ? $default : max(0, (int)$row['price']);
      $lines[] = ['id' => $id === 'oneoff' ? 'oneoff' : $id, 'sku' => $sku, 'name' => $name, 'qty' => $qty, 'optIdx' => 0, 'opt' => '',
        'colour' => $colour, 'note' => mb_substr(trim((string)($row['note'] ?? '')), 0, 300), 'personal' => $personal, 'unit' => $unit, 'total' => $unit * $qty];
    }
    if (!$lines) throw new InvalidArgumentException('Please add at least one item');
    $c = [];
    foreach (['name', 'phone', 'email', 'address', 'city', 'pin'] as $k) $c[$k] = trim((string)($_POST[$k] ?? ''));
    if (!$c['name']) throw new InvalidArgumentException('Please add the customer name');
    if ($c['email'] && !filter_var($c['email'], FILTER_VALIDATE_EMAIL)) throw new InvalidArgumentException('Please check the email address');

    $sub = array_sum(array_column($lines, 'total'));
    $disc = max(0, min($sub, (int)($_POST['disc'] ?? 0)));
    $ship = max(0, (int)($_POST['ship'] ?? 0));
    $t = ['lines' => $lines, 'sub' => $sub, 'disc' => $disc, 'code' => $disc ? 'MANUAL' : '', 'ship' => $ship, 'wrap' => 0, 'total' => $sub - $disc + $ship];

    $pay = isset(PAYMENT[$_POST['payment_status'] ?? '']) ? $_POST['payment_status'] : 'pending';
    $method = clip($_POST['method'] ?? '', 40);
    $adv = 0;
    if ($pay === 'advance') {
      $adv = (int)($_POST['advance_paid'] ?? 0);
      if ($adv <= 0) throw new InvalidArgumentException('Please enter the advance amount received');
      if ($adv >= $t['total']) { $pay = 'paid'; $adv = 0; }   // advance covers everything = fully paid
    }
    $o = order_create($t, $c, (string)($_POST['note'] ?? ''), 'manual', null, $pay, $method, !empty($_POST['marketing']));
    $oid = (int)$o['id'];
    if ($adv) { order_update($oid, ['advance_paid' => $adv]); add_event($oid, 'paid', 'Advance ' . inr($adv) . ' received' . ($method ? " · $method" : '') . ' · ' . inr($t['total'] - $adv) . ' due'); }
    $stage = isset(STAGES[$_POST['stage'] ?? '']) ? $_POST['stage'] : 'new';
    if ($stage === 'new' && in_array($pay, ['paid', 'advance', 'cod'], true) && array_filter($lines, fn($l) => $l['personal'])) $stage = 'awaiting_route';
    if ($stage !== 'new') order_update($oid, ['stage' => $stage]);
    if (!empty($_POST['source_label'])) add_event($oid, 'created', 'Order from: ' . clip($_POST['source_label'], 80));
    if ($pay === 'paid') add_event($oid, 'paid', 'Marked paid by hand' . ($method ? " · $method" : ''));
    if (!empty($_POST['send_email']) && $c['email']) {
      email_order_confirmation(order_get($oid));
      db()->prepare('UPDATE orders SET confirm_emails_sent = 1 WHERE id = ?')->execute([$oid]);
      add_event($oid, 'email', 'Confirmation sent to ' . $c['email']);
    }
    flash('Order ' . $o['order_no'] . ' added.');
    header('Location: order.php?id=' . $oid); exit;
  } catch (InvalidArgumentException $e) { $error = $e->getMessage(); }
}

/* one product <select>, reused for every row */
$options = '<option value="">— choose —</option><optgroup label="Website products">';
foreach ($site as $p) $options .= '<option value="' . e($p['id']) . '" data-price="' . (int)$p['price'] . '" data-colours="' . e(json_encode(array_column($p['colours'] ?? [], 'name'))) . '">' . e(product_sku($p) . ' · ' . $p['name']) . '</option>';
$options .= '</optgroup>';
if ($custom) {
  $options .= '<optgroup label="Custom products (not on website)">';
  foreach ($custom as $cp) $options .= '<option value="c:' . (int)$cp['id'] . '" data-price="' . (int)$cp['price'] . '">' . e(custom_sku($cp) . ' · ' . $cp['name']) . '</option>';
  $options .= '</optgroup>';
}
$options .= '<optgroup label="Other"><option value="oneoff" data-price="">TAP-ONEOFF · One-off item (type a name)…</option></optgroup>';

page_start('New order', 'new-order.php');
?>
<h1>Add an order by hand</h1>
<p class="muted">For expo-stall, WhatsApp, phone, corporate or any custom order. Items can be website products, your
  <a href="products.php">custom products</a> (never shown on the website), or a one-off item. Prices can be changed per order.</p>
<?php if ($error): ?><p class="warn"><?= e($error) ?></p><?php endif; ?>
<form method="post" class="card form" id="nf">
  <?= csrf_field() ?>
  <h2 class="full">Items</h2>
  <div class="full items-head"><span>Product</span><span>Qty</span><span>Price each (₹)</span><span>Colour</span><span>Event / name / details</span></div>
  <div class="full" id="rows">
    <?php for ($i = 0; $i < 3; $i++): ?>
      <div class="itemrow2" data-i="<?= $i ?>">
        <div class="pick"><select name="item[<?= $i ?>][id]" class="prod"><?= $options ?></select>
          <input name="item[<?= $i ?>][name]" class="oneoff" placeholder="Item name, e.g. Custom office trophy" hidden>
          <label class="chk oneoff" hidden><input type="checkbox" name="item[<?= $i ?>][personal]" value="1"> needs route file</label></div>
        <input name="item[<?= $i ?>][qty]" type="number" min="1" value="1" aria-label="Quantity">
        <input name="item[<?= $i ?>][price]" type="number" min="0" class="price" placeholder="price" aria-label="Price each">
        <select name="item[<?= $i ?>][colour]" class="colour" aria-label="Colour"><option value="">—</option></select>
        <input name="item[<?= $i ?>][note]" placeholder="Event, name, time, size…" aria-label="Details">
      </div>
    <?php endfor; ?>
  </div>
  <div class="full actions"><button type="button" class="btn ghost sm" id="addrow">+ Add another item</button><span class="muted" id="subtotal"></span></div>

  <h2 class="full">Customer</h2>
  <label>Name<input name="name" required></label>
  <label>Phone<input name="phone" inputmode="tel"></label>
  <label>Email <small class="muted">(for the confirmation)</small><input name="email" type="email"></label>
  <label>Order came from<input name="source_label" placeholder="Pune Marathon expo, Instagram DM, referral…" list="srcs"></label>
  <datalist id="srcs"><option value="Expo stall"><option value="WhatsApp"><option value="Instagram"><option value="Phone call"><option value="Corporate"><option value="Referral"></datalist>
  <label class="full">Address<textarea name="address" rows="2" placeholder="Leave empty if collected in person"></textarea></label>
  <label>City<input name="city"></label>
  <label>PIN<input name="pin" inputmode="numeric"></label>

  <h2 class="full">Payment &amp; status</h2>
  <label>Payment<select name="payment_status"><option value="paid">Paid in full</option><option value="advance">Advance paid</option><option value="pending">Not paid yet</option><option value="cod">Cash on delivery</option></select></label>
  <label data-advance hidden>Advance received (₹, any amount)<input name="advance_paid" type="number" min="1" placeholder="e.g. 1000"><small class="muted" data-due></small></label>
  <label>Method<select name="method"><option>UPI</option><option>Cash</option><option>Card</option><option>Bank transfer</option><option>Payment link</option><option>Invoice</option></select></label>
  <label>Shipping charge (₹)<input name="ship" type="number" min="0" value="0"></label>
  <label>Discount (₹)<input name="disc" type="number" min="0" value="0"></label>
  <label>Starting stage<select name="stage"><?php foreach (STAGES as $k => $label): ?><option value="<?= $k ?>"><?= $label ?></option><?php endforeach; ?></select></label>
  <label class="full">Note<textarea name="note" rows="2"></textarea></label>
  <label class="full chk"><input type="checkbox" name="send_email" value="1"> Email the customer an order confirmation</label>
  <label class="full chk"><input type="checkbox" name="marketing" value="1"> Customer agreed to receive new products &amp; offers (WhatsApp / email)</label>
  <button class="btn primary">Add order</button>
</form>
<script>
/* show the advance-amount box only when "Advance paid" is picked */
document.querySelectorAll('select[name="payment_status"]').forEach(sel => {
  const box = sel.form.querySelector('[data-advance]'); if (!box) return;
  const inp = box.querySelector('input'), due = box.querySelector('[data-due]'), f = sel.form;
  const rs = n => '₹' + Math.round(n).toLocaleString('en-IN');
  const orderTotal = () => {   // order page knows its total; the new-order form adds it up from the rows
    if (box.dataset.total) return +box.dataset.total;
    let s = 0;
    f.querySelectorAll('.itemrow2').forEach(r => { if (r.querySelector('.prod').value) s += (+r.querySelector('.price').value || 0) * (+r.querySelector('[name$="[qty]"]').value || 0); });
    return Math.max(0, s - (+f.disc.value || 0) + (+f.ship.value || 0));
  };
  const sync = () => {
    box.hidden = sel.value !== 'advance'; inp.required = !box.hidden;
    const t = orderTotal(), a = +inp.value || 0;
    due.textContent = !t ? 'Add items to see the balance' : !a ? 'Order total ' + rs(t) + ': type any amount received'
      : a >= t ? 'Covers the full ' + rs(t) + ': will be saved as Paid' : 'Balance due: ' + rs(t - a) + ' of ' + rs(t);
  };
  sel.addEventListener('change', sync); f.addEventListener('input', sync); f.addEventListener('change', sync); sync();
});
(() => {
  const rows = document.getElementById('rows'), inr = n => '₹' + Math.round(n).toLocaleString('en-IN');
  const wire = row => {
    const sel = row.querySelector('.prod'), price = row.querySelector('.price'), colour = row.querySelector('.colour');
    sel.addEventListener('change', () => {
      const o = sel.selectedOptions[0], one = sel.value === 'oneoff';
      row.querySelectorAll('.oneoff').forEach(el => el.hidden = !one);
      price.value = o && o.dataset.price ? o.dataset.price : '';
      const cols = o && o.dataset.colours ? JSON.parse(o.dataset.colours) : [];
      colour.innerHTML = cols.length ? cols.map(c => '<option>' + c.replace(/</g, '&lt;') + '</option>').join('') : '<option value="">—</option>';
      total();
    });
  };
  const total = () => {
    let s = 0;
    rows.querySelectorAll('.itemrow2').forEach(r => { if (r.querySelector('.prod').value) s += (+r.querySelector('.price').value || 0) * (+r.querySelector('[name$="[qty]"]').value || 0); });
    document.getElementById('subtotal').textContent = s ? 'Items total: ' + inr(s) : '';
  };
  rows.querySelectorAll('.itemrow2').forEach(wire);
  rows.addEventListener('input', total);
  document.getElementById('addrow').addEventListener('click', () => {
    const last = rows.lastElementChild, i = +last.dataset.i + 1, row = last.cloneNode(true);
    row.dataset.i = i;
    row.querySelectorAll('[name]').forEach(el => { el.name = el.name.replace(/item\[\d+\]/, 'item[' + i + ']'); if (el.type === 'checkbox') el.checked = false; else if (el.tagName !== 'SELECT') el.value = el.name.endsWith('[qty]') ? 1 : ''; });
    row.querySelector('.prod').value = ''; row.querySelector('.colour').innerHTML = '<option value="">—</option>';
    row.querySelectorAll('.oneoff').forEach(el => el.hidden = true);
    rows.appendChild(row); wire(row);
  });
})();
</script>
<?php page_end();
