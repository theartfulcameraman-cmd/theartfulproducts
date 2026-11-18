<?php
require __DIR__ . '/_admin.php';
if (admin_ready()) { header('Location: login.php'); exit; }
require_login();

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
  check_csrf();
  $status = isset(ENQUIRY_STATUS[$_POST['status'] ?? '']) ? $_POST['status'] : 'new';
  db()->prepare('UPDATE enquiries SET status = ?, notes = ? WHERE id = ?')->execute([$status, mb_substr((string)($_POST['notes'] ?? ''), 0, 5000), (int)($_POST['id'] ?? 0)]);
  flash('Enquiry updated.');
  header('Location: enquiries.php' . (isset($_GET['s']) ? '?s=' . urlencode($_GET['s']) : '')); exit;
}

$filter = isset(ENQUIRY_STATUS[$_GET['s'] ?? '']) ? $_GET['s'] : '';
$s = db()->prepare('SELECT * FROM enquiries' . ($filter ? ' WHERE status = ?' : '') . ' ORDER BY id DESC LIMIT 200');
$s->execute($filter ? [$filter] : []);
$rows = $s->fetchAll();

page_start('Enquiries', 'enquiries.php');
?>
<h1>Enquiries</h1>
<div class="tabs" style="margin-bottom:16px">
  <a href="enquiries.php" class="<?= $filter ? '' : 'on' ?>">All</a>
  <?php foreach (ENQUIRY_STATUS as $k => $label): ?><a href="?s=<?= $k ?>" class="<?= $filter === $k ? 'on' : '' ?>"><?= $label ?></a><?php endforeach; ?>
</div>
<?php if (!$rows): ?><div class="empty">No enquiries yet. Bulk-order and contact forms from the website appear here.</div><?php endif; ?>
<?php foreach ($rows as $r):
  $d = json_decode($r['data'] ?: '{}', true) ?: [];
  $phone = preg_replace('/\D/', '', $r['phone']); if (strlen($phone) === 10) $phone = '91' . $phone;
?>
  <section class="card enq">
    <div class="enq-h">
      <div><b><?= e($r['name']) ?></b> <span class="tag"><?= $r['kind'] === 'organiser' ? 'Bulk / organiser' : 'Contact' ?></span>
        <br><small class="muted"><?= e(date('d M Y, g:ia', strtotime($r['created_at']))) ?></small></div>
      <?= badge('enq', $r['status']) ?>
    </div>
    <dl>
      <?php foreach ($d as $k => $v): if ($v === '' || $k === 'name') continue; ?>
        <dt><?= e(ucfirst($k)) ?></dt><dd><?= nl2br(e($v)) ?></dd>
      <?php endforeach; ?>
    </dl>
    <div class="actions">
      <?php if ($phone): ?><a class="btn wa sm" href="https://wa.me/<?= e($phone) ?>?text=<?= e(rawurlencode('Hi ' . strtok($r['name'], ' ') . ', thank you for your enquiry with The Artful Products.')) ?>" target="_blank" rel="noopener">WhatsApp</a><?php endif; ?>
      <?php if ($r['email']): ?><a class="btn ghost sm" href="mailto:<?= e($r['email']) ?>">Email</a><?php endif; ?>
    </div>
    <form method="post" class="form compact">
      <?= csrf_field() ?><input type="hidden" name="id" value="<?= (int)$r['id'] ?>">
      <label>Status<select name="status"><?php foreach (ENQUIRY_STATUS as $k => $label): ?><option value="<?= $k ?>" <?= $k === $r['status'] ? 'selected' : '' ?>><?= $label ?></option><?php endforeach; ?></select></label>
      <label class="grow">Notes<input name="notes" value="<?= e($r['notes']) ?>" placeholder="Quote sent, follow up on…"></label>
      <button class="btn">Save</button>
    </form>
  </section>
<?php endforeach; ?>
<?php page_end();
