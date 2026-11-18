<?php
require __DIR__ . '/_admin.php';

$problem = admin_ready();
$error = '';
if (!$problem && ($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
  check_csrf();
  if (too_many_attempts()) {
    $error = 'Too many wrong attempts. Please wait 15 minutes and try again.';
  } elseif (check_password((string)($_POST['password'] ?? ''))) {
    session_regenerate_id(true);
    $_SESSION['admin'] = true; $_SESSION['at'] = time();
    header('Location: index.php'); exit;
  } else {
    record_failed_login();
    $error = 'That password is not right.';
  }
}
if (logged_in()) { header('Location: index.php'); exit; }

page_start('Log in');
?>
<div class="login">
  <h1>Admin login</h1>
  <?php if ($problem): ?>
    <p class="warn"><?= e($problem) ?></p>
  <?php else: ?>
    <?php if ($error): ?><p class="warn"><?= e($error) ?></p><?php endif; ?>
    <form method="post">
      <?= csrf_field() ?>
      <label>Password<input type="password" name="password" autocomplete="current-password" required autofocus></label>
      <button class="btn primary">Log in</button>
    </form>
  <?php endif; ?>
</div>
<?php page_end();
