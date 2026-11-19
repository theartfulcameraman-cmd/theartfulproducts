<?php
/* Custom products: things you make for orders that come from outside the website
   (custom awards, one-off frames, corporate gifts…). They NEVER appear on the website —
   they're only offered in "+ New order" so those orders are tracked here too. */
require __DIR__ . '/_admin.php';
if (admin_ready()) { header('Location: login.php'); exit; }
require_login();

$edit = isset($_GET['edit']) ? custom_product((int)$_GET['edit']) : null;

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
  check_csrf();
  $action = $_POST['action'] ?? 'save';
  if (in_array($action, ['archive', 'restore', 'delete'], true)) {
    $pid = (int)($_POST['id'] ?? 0); $cp = custom_product($pid);
    if ($cp && $action !== 'delete') {
      db()->prepare('UPDATE custom_products SET active = ? WHERE id = ?')->execute([$action === 'restore' ? 1 : 0, $pid]);
      flash('“' . $cp['name'] . '” ' . ($action === 'restore' ? 'restored; it is offered in + New order again.' : 'archived; it is no longer offered in + New order.'));
    } elseif ($cp) {
      // permanent; only for archived products. Past orders keep the product's name and price.
      if ((int)$cp['active']) flash('Archive the product first; only archived products can be deleted.');
      else { db()->prepare('DELETE FROM custom_products WHERE id = ?')->execute([$pid]); flash('“' . $cp['name'] . '” deleted permanently. Past orders still show it.'); }
    }
    header('Location: products.php'); exit;
  }
  $f = [
    'name' => clip($_POST['name'] ?? '', 160),
    'price' => max(0, (int)($_POST['price'] ?? 0)),
    'category' => clip($_POST['category'] ?? '', 80),
    'description' => mb_substr(trim((string)($_POST['description'] ?? '')), 0, 2000),
    'personal' => empty($_POST['personal']) ? 0 : 1,
    'active' => empty($_POST['active']) ? 0 : 1,
  ];
  if ($f['name'] === '') { flash('Please give the product a name.'); header('Location: products.php'); exit; }
  $id = (int)($_POST['id'] ?? 0);
  if ($id) {
    db()->prepare('UPDATE custom_products SET name=?, price=?, category=?, description=?, personal=?, active=? WHERE id=?')
      ->execute([$f['name'], $f['price'], $f['category'], $f['description'], $f['personal'], $f['active'], $id]);
    flash('Saved “' . $f['name'] . '”.');
  } else {
    db()->prepare('INSERT INTO custom_products (created_at, name, price, category, description, personal, active) VALUES (?,?,?,?,?,?,?)')
      ->execute([now(), $f['name'], $f['price'], $f['category'], $f['description'], $f['personal'], 1]);
    flash('Added “' . $f['name'] . '”. It’s now available in + New order.');
  }
  header('Location: products.php'); exit;
}

$rows = custom_products(false);
$used = [];
foreach (db()->query("SELECT items FROM orders WHERE source = 'manual'")->fetchAll() as $o)
  foreach (json_decode($o['items'] ?: '[]', true) ?: [] as $l) if (str_starts_with((string)($l['id'] ?? ''), 'c:')) $used[$l['id']] = ($used[$l['id']] ?? 0) + (int)$l['qty'];

page_start('Custom products', 'products.php');
?>
<h1>Custom products</h1>
<p class="muted">Products for orders you get outside the website. They <b>never show on the website</b>, only in <a href="new-order.php">+ New order</a>.
  Website products are managed in <code>data.js</code>.</p>

<div class="grid2">
  <section class="card">
    <h2><?= $edit ? 'Edit product' : 'Add a custom product' ?></h2>
    <form method="post" class="form">
      <?= csrf_field() ?><input type="hidden" name="id" value="<?= (int)($edit['id'] ?? 0) ?>">
      <label class="full">Name<input name="name" required value="<?= e($edit['name'] ?? '') ?>" placeholder="e.g. Corporate Trek Trophy"></label>
      <label>Usual price (₹)<input name="price" type="number" min="0" value="<?= (int)($edit['price'] ?? 0) ?>"></label>
      <label>Category <small class="muted">(optional)</small><input name="category" value="<?= e($edit['category'] ?? '') ?>" placeholder="Awards, Gifts…" list="cats"></label>
      <datalist id="cats"><?php foreach (array_unique(array_filter(array_column($rows, 'category'))) as $c): ?><option value="<?= e($c) ?>"><?php endforeach; ?></datalist>
      <label class="full">Description / spec <small class="muted">(only you see this)</small><textarea name="description" rows="3"><?= e($edit['description'] ?? '') ?></textarea></label>
      <label class="full chk"><input type="checkbox" name="personal" value="1" <?= !empty($edit['personal']) ? 'checked' : '' ?>> Needs a route file / personal details (order starts as “Awaiting route file”)</label>
      <?php if ($edit): ?><label class="full chk"><input type="checkbox" name="active" value="1" <?= !empty($edit['active']) ? 'checked' : '' ?>> Available in + New order (untick to archive it; past orders keep it)</label><?php else: ?><input type="hidden" name="active" value="1"><?php endif; ?>
      <div class="actions full"><button class="btn primary"><?= $edit ? 'Save product' : 'Add product' ?></button><?php if ($edit): ?><a class="btn ghost" href="products.php">Cancel</a><?php endif; ?></div>
    </form>
  </section>

  <section class="card">
    <h2>Your custom products <span class="muted">(<?= count($rows) ?>)</span></h2>
    <?php if (!$rows): ?><p class="muted">None yet. Add one on the left. For a one-time item you can also just type it in + New order.</p><?php endif; ?>
    <?php foreach ($rows as $r): ?>
      <div class="line">
        <div><b><?= e($r['name']) ?></b> <?= $r['active'] ? '' : '<span class="tag">Archived</span>' ?> <?= $r['personal'] ? '<span class="tag">Personalised</span>' : '' ?>
          <br><span class="muted"><?= e(implode(' · ', array_filter([$r['category'], ($used['c:' . $r['id']] ?? 0) ? ($used['c:' . $r['id']] . ' sold') : '']))) ?></span>
          <?php if ($r['description']): ?><div class="muted" style="font-size:.85rem;margin-top:4px"><?= nl2br(e($r['description'])) ?></div><?php endif; ?></div>
        <div class="prod-acts"><b><?= inr($r['price']) ?></b>
          <div class="actions">
            <a href="?edit=<?= (int)$r['id'] ?>" class="btn ghost sm">Edit</a>
            <?php $hid = csrf_field() . '<input type="hidden" name="id" value="' . (int)$r['id'] . '">'; ?>
            <?php if ($r['active']): ?>
              <form method="post"><?= $hid ?><input type="hidden" name="action" value="archive"><button class="btn sm arch">Archive</button></form>
            <?php else: ?>
              <form method="post"><?= $hid ?><input type="hidden" name="action" value="restore"><button class="btn ghost sm">Restore</button></form>
              <form method="post" onsubmit="return confirm('Delete “<?= e(addslashes($r['name'])) ?>” permanently? Past orders keep its name and price.')"><?= $hid ?><input type="hidden" name="action" value="delete"><button class="btn danger sm">Delete</button></form>
            <?php endif; ?>
          </div></div>
      </div>
    <?php endforeach; ?>
  </section>
</div>
<?php page_end();
