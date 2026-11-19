<?php
require __DIR__ . '/_admin.php';
if (admin_ready()) { header('Location: login.php'); exit; }
require_login();

$back = 'enquiries.php' . (isset($_GET['s']) ? '?s=' . urlencode($_GET['s']) : '');
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
  check_csrf();
  $id = (int)($_POST['id'] ?? 0);
  $action = $_POST['action'] ?? 'save';
  if ($action === 'archive' || $action === 'restore') {
    db()->prepare('UPDATE enquiries SET archived = ? WHERE id = ?')->execute([$action === 'archive' ? 1 : 0, $id]);
    flash($action === 'archive' ? 'Enquiry archived. Find it under Archived.' : 'Enquiry restored.');
  } elseif ($action === 'delete') {
    // permanent: only for archived enquiries (the button only shows there, and the browser asks to confirm)
    $n = db()->prepare('DELETE FROM enquiries WHERE id = ? AND COALESCE(archived,0) = 1'); $n->execute([$id]);
    flash($n->rowCount() ? 'Enquiry deleted permanently.' : 'Archive the enquiry first; only archived enquiries can be deleted.');
  } else {
    $status = isset(ENQUIRY_STATUS[$_POST['status'] ?? '']) ? $_POST['status'] : 'new';
    db()->prepare('UPDATE enquiries SET status = ?, notes = ? WHERE id = ?')->execute([$status, mb_substr((string)($_POST['notes'] ?? ''), 0, 5000), $id]);
    flash('Enquiry updated.');
  }
  header('Location: ' . $back); exit;
}

$archivedView = ($_GET['s'] ?? '') === 'archived';
$filter = isset(ENQUIRY_STATUS[$_GET['s'] ?? '']) ? $_GET['s'] : '';
$where = $archivedView ? 'COALESCE(archived,0) = 1' : 'COALESCE(archived,0) = 0' . ($filter ? ' AND status = ?' : '');
$s = db()->prepare("SELECT * FROM enquiries WHERE $where ORDER BY id DESC LIMIT 200");
$s->execute(!$archivedView && $filter ? [$filter] : []);
$rows = $s->fetchAll();
$nArch = (int)db()->query('SELECT COUNT(*) FROM enquiries WHERE COALESCE(archived,0) = 1')->fetchColumn();

page_start('Enquiries', 'enquiries.php');
?>
<h1>Enquiries</h1>
<div class="tabs" style="margin-bottom:16px">
  <a href="enquiries.php" class="<?= $filter || $archivedView ? '' : 'on' ?>">All</a>
  <?php foreach (ENQUIRY_STATUS as $k => $label): ?><a href="?s=<?= $k ?>" class="<?= $filter === $k ? 'on' : '' ?>"><?= $label ?></a><?php endforeach; ?>
  <a href="?s=archived" class="<?= $archivedView ? 'on' : '' ?>">Archived <em><?= $nArch ?></em></a>
</div>
<?php if (!$rows): ?><div class="empty"><?= $archivedView ? 'Nothing archived.' : 'No enquiries yet. Bulk-order and contact forms from the website appear here.' ?></div><?php endif; ?>
<?php foreach ($rows as $r):
  $d = json_decode($r['data'] ?: '{}', true) ?: [];
  $phone = preg_replace('/\D/', '', $r['phone']); if (strlen($phone) === 10) $phone = '91' . $phone;
  $hid = '<input type="hidden" name="id" value="' . (int)$r['id'] . '">';
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
      <?php if ($archivedView): ?>
        <form method="post"><?= csrf_field() . $hid ?><input type="hidden" name="action" value="restore"><button class="btn ghost sm">Restore</button></form>
        <form method="post" onsubmit="return confirm('Delete this enquiry permanently? This cannot be undone.')"><?= csrf_field() . $hid ?><input type="hidden" name="action" value="delete"><button class="btn danger sm">Delete forever</button></form>
      <?php else: ?>
        <form method="post"><?= csrf_field() . $hid ?><input type="hidden" name="action" value="archive"><button class="btn sm arch">Archive</button></form>
      <?php endif; ?>
    </div>
    <?php if (!$archivedView): ?>
    <form method="post" class="form compact">
      <?= csrf_field() . $hid ?>
      <label>Status<select name="status"><?php foreach (ENQUIRY_STATUS as $k => $label): ?><option value="<?= $k ?>" <?= $k === $r['status'] ? 'selected' : '' ?>><?= $label ?></option><?php endforeach; ?></select></label>
      <label class="grow">Notes<input name="notes" value="<?= e($r['notes']) ?>" placeholder="Quote sent, follow up on…"></label>
      <button class="btn">Save</button>
    </form>
    <?php endif; ?>
  </section>
<?php endforeach; ?>
<?php page_end();
