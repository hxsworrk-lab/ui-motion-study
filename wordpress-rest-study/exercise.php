<?php
// Real WordPress core is required; no WP functions or REST server are mocked.
// https://developer.wordpress.org/playground/blueprints/steps/#runPHP
// https://developer.wordpress.org/reference/functions/rest_do_request/
require_once '/wordpress/wp-load.php';

$started = microtime(true);
$initial = array('title' => 'Synthetic baseline', 'email' => 'baseline@example.test');
update_option('hx_probe_submission', $initial, false);

$editor = wp_insert_user(array(
    'user_login' => 'hx_synthetic_editor',
    'user_pass' => 'synthetic-local-only-not-a-real-account',
    'user_email' => 'editor@example.test',
    'role' => 'editor',
));
$subscriber = wp_insert_user(array(
    'user_login' => 'hx_synthetic_subscriber',
    'user_pass' => 'synthetic-local-only-not-a-real-account',
    'user_email' => 'subscriber@example.test',
    'role' => 'subscriber',
));
if (is_wp_error($editor) || is_wp_error($subscriber)) {
    throw new RuntimeException('Could not create isolated synthetic users.');
}

$cases = array(
    array('name' => 'guest_valid_nonce_denied', 'user' => 0, 'nonce' => 'valid', 'body' => array('title' => 'Guest attempt', 'email' => 'guest@example.test'), 'expected_status' => 403, 'expected_code' => 'hx_forbidden'),
    array('name' => 'subscriber_valid_nonce_denied', 'user' => $subscriber, 'nonce' => 'valid', 'body' => array('title' => 'Subscriber attempt', 'email' => 'subscriber@example.test'), 'expected_status' => 403, 'expected_code' => 'hx_forbidden'),
    array('name' => 'editor_bad_nonce_denied', 'user' => $editor, 'nonce' => 'bad', 'body' => array('title' => 'Bad nonce attempt', 'email' => 'editor@example.test'), 'expected_status' => 403, 'expected_code' => 'hx_bad_nonce'),
    array('name' => 'editor_missing_nonce_denied', 'user' => $editor, 'nonce' => 'missing', 'body' => array('title' => 'Missing nonce attempt', 'email' => 'editor@example.test'), 'expected_status' => 403, 'expected_code' => 'hx_bad_nonce'),
    array('name' => 'editor_missing_title_rejected', 'user' => $editor, 'nonce' => 'valid', 'body' => array('email' => 'editor@example.test'), 'expected_status' => 400, 'expected_code' => 'hx_bad_title'),
    array('name' => 'editor_invalid_email_rejected', 'user' => $editor, 'nonce' => 'valid', 'body' => array('title' => 'Invalid email attempt', 'email' => 'not-an-email'), 'expected_status' => 400, 'expected_code' => 'hx_bad_email'),
    array('name' => 'editor_valid_sanitized_payload_saved', 'user' => $editor, 'nonce' => 'valid', 'body' => array('title' => "  <b>Synthetic</b>\nform entry  ", 'email' => 'sample@example.test'), 'expected_status' => 201, 'expected_code' => null),
);
$observations = array();
foreach ($cases as $case) {
    wp_set_current_user($case['user']);
    $before = get_option('hx_probe_submission');
    $request = new WP_REST_Request('POST', '/hx-probe/v1/submission');
    $request->set_body_params($case['body']);
    if ($case['nonce'] !== 'missing') {
        $request->set_header('X-WP-Nonce', $case['nonce'] === 'valid' ? wp_create_nonce('wp_rest') : 'deliberately-invalid-local-value');
    }
    $response = rest_do_request($request);
    $after = get_option('hx_probe_submission');
    $data = $response->get_data();
    $code = isset($data['code']) ? $data['code'] : null;
    $invalid_unchanged = $case['expected_status'] === 201 ? null : ($before === $after);
    $valid_value = $case['expected_status'] === 201 ? ($after === array('title' => 'Synthetic form entry', 'email' => 'sample@example.test')) : null;
    $observations[] = array(
        'case' => $case['name'],
        'actor_roles' => wp_get_current_user()->roles,
        'edit_posts_capability' => current_user_can('edit_posts'),
        'nonce_mode' => $case['nonce'],
        'status' => $response->get_status(),
        'response' => $data,
        'state_before' => $before,
        'state_after' => $after,
        'invalid_request_left_submission_unchanged' => $invalid_unchanged,
        'valid_payload_persisted_as_expected' => $valid_value,
        'passed' => $response->get_status() === $case['expected_status'] && $code === $case['expected_code'] && $invalid_unchanged !== false && $valid_value !== false,
    );
}
$functions = array();
foreach (array('rest_do_request', 'wp_verify_nonce', 'current_user_can', 'get_option', 'sanitize_text_field') as $name) {
    $reflection = new ReflectionFunction($name);
    $functions[$name] = array('file' => $reflection->getFileName(), 'start_line' => $reflection->getStartLine());
}
$result = array(
    'kind' => 'self_initiated_synthetic_wordpress_internal_rest_integration',
    'observed_at_utc' => gmdate('c'),
    'wordpress_version' => $GLOBALS['wp_version'],
    'php_version' => PHP_VERSION,
    'php_sapi' => PHP_SAPI,
    'core_version_file_sha256' => hash_file('sha256', ABSPATH . WPINC . '/version.php'),
    'core_functions' => $functions,
    'rest_server_class' => get_class(rest_get_server()),
    'database_class' => get_class($GLOBALS['wpdb']),
    'case_count' => count($observations),
    'all_passed' => count(array_filter($observations, function ($row) { return !$row['passed']; })) === 0,
    'observations' => $observations,
    'elapsed_seconds' => round(microtime(true) - $started, 6),
    'limitations' => array(
        'Internal rest_do_request calls; not HTTP/browser/cookie authentication or network CSRF validation.',
        'Synthetic WP users use wp_set_current_user; not login/session tests or a real owner account.',
        'No database persistence across Playground process exit or production database compatibility tested.',
        'No client site, third-party form plugin, SMTP delivery, payment or purchased work tested.',
        'No-write observations concern this one submission option, not every WordPress internal table or cache.',
    ),
);
$encoded = wp_json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
// Only this isolated output directory is mounted by the headless runner.
if (file_put_contents('/hx-output/result.json', $encoded) === false) {
    throw new RuntimeException('Could not preserve the actual integration observation.');
}
echo "HX_PROBE_RESULT_BEGIN\n" . $encoded . "HX_PROBE_RESULT_END\n";
if (!$result['all_passed']) {
    throw new RuntimeException('One or more actual WordPress integration observations failed.');
}
