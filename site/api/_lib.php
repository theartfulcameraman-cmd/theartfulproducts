<?php
/* ------------------------------------------------------------------
   Pricing + JSON helpers for the payment endpoints.
   The pricing rules are a line-for-line port of site/assets/js/pricing.js
   (tools/test_backend.py checks the two give identical totals).
   Prices come from catalog.json, written from data.js by tools/build_pages.py.
------------------------------------------------------------------- */
if (basename($_SERVER['SCRIPT_FILENAME'] ?? '') === basename(__FILE__)) { http_response_code(404); exit; }

/* PHP 7.4 compatibility (the host may still run 7.4): PHP 8 string helpers */
if (!function_exists('str_starts_with')) { function str_starts_with(string $h, string $n): bool { return $n === '' || strncmp($h, $n, strlen($n)) === 0; } }
if (!function_exists('str_ends_with')) { function str_ends_with(string $h, string $n): bool { return $n === '' || substr($h, -strlen($n)) === $n; } }
if (!function_exists('str_contains')) { function str_contains(string $h, string $n): bool { return $n === '' || strpos($h, $n) !== false; } }

function send_json(int $status, array $body): void {
  http_response_code($status);
  header('Content-Type: application/json');
  header('Cache-Control: no-store');
  echo json_encode($body, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
  exit;
}

function require_post(): array {
  if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') send_json(405, ['error' => 'Use POST']);
  $body = json_decode(file_get_contents('php://input') ?: '', true);
  if (!is_array($body)) send_json(400, ['error' => 'Bad request']);
  return $body;
}

function catalog(): array {
  static $c = null;
  if ($c === null) {
    $c = json_decode((string)@file_get_contents(__DIR__ . '/catalog.json'), true);
    if (!is_array($c)) send_json(500, ['error' => 'Catalogue missing']);
  }
  return $c;
}

/* ---- pricing: same rules as pricing.js ---- */
function unit_price(array $p, int $qty, int $optIdx): int {
  $base = (int)($p['price'] ?? 0);
  foreach (($p['tiers'] ?? []) as $t) if ($qty >= (int)$t['min']) $base = (int)$t['price'];
  return $base + (int)($p['options']['extra'][$optIdx] ?? 0);
}

function discount_rate($code, array $site): float {
  if (!$code) return 0;
  $code = strtoupper(trim((string)$code));
  $fs = $site['flashSale'] ?? null;
  if ($fs && !empty($fs['active']) && !empty($fs['code']) && $code === strtoupper($fs['code']) && time() < strtotime($fs['ends']))
    return ($fs['percent'] ?? 10) / 100;
  $extra = $site['discountCodes'][$code] ?? 0;
  return $extra ? $extra / 100 : 0;
}

function compute_order(array $items, array $opts, array $site, array $products): array {
  $byId = [];
  foreach ($products as $p) $byId[$p['id']] = $p;
  $lines = [];
  foreach ($items as $it) {
    if (!is_array($it)) throw new InvalidArgumentException('Bad item');
    $id = (string)($it['id'] ?? '');
    if (!isset($byId[$id])) throw new InvalidArgumentException("Unknown product: $id");
    $p = $byId[$id];
    if (($p['status'] ?? 'live') !== 'live' || empty($p['price'])) throw new InvalidArgumentException($p['name'] . " can't be bought online");
    $qty = max(1, min(999, (int)($it['qty'] ?? 1)));
    $nOpt = isset($p['options']) ? count($p['options']['values']) : 1;
    $optIdx = max(0, min($nOpt - 1, (int)($it['optIdx'] ?? 0)));
    $colours = array_map(fn($c) => $c['name'], $p['colours'] ?? []);
    $u = unit_price($p, $qty, $optIdx);
    $lines[] = [
      'id' => $p['id'], 'name' => $p['name'], 'qty' => $qty, 'optIdx' => $optIdx,
      'opt' => isset($p['options']) ? $p['options']['values'][$optIdx] : '',
      'colour' => in_array($it['colour'] ?? null, $colours, true) ? $it['colour'] : ($colours[0] ?? ''),
      'note' => mb_substr((string)($it['note'] ?? ''), 0, 300),
      'personal' => !empty($p['personal']),
      'unit' => $u, 'total' => $u * $qty,
    ];
  }
  if (!$lines) throw new InvalidArgumentException('The cart is empty');
  $sub = array_sum(array_column($lines, 'total'));
  $rate = discount_rate($opts['code'] ?? '', $site);
  $disc = (int)round($sub * $rate);
  $physical = false;
  foreach ($lines as $l) if (($byId[$l['id']]['art'] ?? '') !== 'giftcard') $physical = true;
  $ship = (!$physical || $sub >= $site['freeShippingAbove']) ? 0 : (int)$site['shippingFlat'];
  $wrap = !empty($opts['wrap']) ? (int)$site['giftWrap'] : 0;
  return ['lines' => $lines, 'sub' => $sub, 'rate' => $rate, 'code' => $rate ? strtoupper(trim((string)$opts['code'])) : '',
          'disc' => $disc, 'ship' => $ship, 'wrap' => $wrap, 'total' => $sub - $disc + $ship + $wrap];
}

function clip($s, int $n = 250): string {
  return mb_substr(trim(preg_replace('/\s+/u', ' ', (string)$s)), 0, $n);
}
