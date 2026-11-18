<?php
/* POST /api/enquiry.php — saves organiser (bulk) and contact-form enquiries to the admin dashboard
   and emails you a copy. The form still opens WhatsApp / email for the customer as before. */
require __DIR__ . '/_app.php';

$body = require_post();
if (!empty($body['website'])) send_json(200, ['ok' => true]);           // hidden "honeypot" field: filled only by spam bots
$kind = in_array($body['kind'] ?? '', ['organiser', 'contact'], true) ? $body['kind'] : 'contact';
$data = [];
foreach ((array)($body['data'] ?? []) as $k => $v) $data[clip($k, 40)] = is_array($v) ? implode(', ', array_map('strval', $v)) : clip($v, 2000);
if (empty($data['name']) || (empty($data['phone']) && empty($data['email']))) send_json(400, ['error' => 'Please add your name and a phone or email']);
if (!db_configured()) send_json(200, ['ok' => true, 'saved' => false]);

try {
  $id = enquiry_create($kind, $data);
  $rows = '';
  foreach ($data as $k => $v) $rows .= '<tr><td style="padding:6px 10px 6px 0;color:#777;vertical-align:top">' . e(ucfirst($k)) . '</td><td style="padding:6px 0">' . nl2br(e($v)) . '</td></tr>';
  $admin = rtrim(cfg('site_url', ''), '/') . '/admin/enquiries.php';
  send_mail((string)cfg('owner_email'), ($kind === 'organiser' ? 'New bulk enquiry' : 'New message') . ' · ' . ($data['event'] ?? $data['topic'] ?? $data['name']),
    email_wrap($kind === 'organiser' ? 'New organiser enquiry' : 'New contact message', '<table style="font-size:14px">' . $rows . '</table><p><a href="' . e($admin) . '">Open enquiries in admin</a></p>'),
    (string)($data['email'] ?? ''));
  send_json(200, ['ok' => true, 'saved' => true, 'id' => $id]);
} catch (Throwable $e) {
  error_log('Enquiry save failed: ' . $e->getMessage());
  send_json(200, ['ok' => true, 'saved' => false]);
}
