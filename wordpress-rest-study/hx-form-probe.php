<?php
/**
 * Plugin Name: Hx Works Synthetic Form Capability Probe
 * Description: Internal, self-initiated WordPress integration experiment. No client data.
 * License: GPL-2.0-or-later
 *
 * Sources:
 * https://developer.wordpress.org/rest-api/extending-the-rest-api/adding-custom-endpoints/
 * https://developer.wordpress.org/reference/functions/wp_verify_nonce/
 */
defined('ABSPATH') || exit;

add_action('rest_api_init', function () {
    register_rest_route('hx-probe/v1', '/submission', array(
        'methods' => 'POST',
        'permission_callback' => function (WP_REST_Request $request) {
            // A valid nonce is not authorization: capability is checked separately.
            if (!current_user_can('edit_posts')) {
                return new WP_Error('hx_forbidden', 'edit_posts capability required.', array('status' => 403));
            }
            if (!wp_verify_nonce($request->get_header('X-WP-Nonce'), 'wp_rest')) {
                return new WP_Error('hx_bad_nonce', 'Valid action nonce required.', array('status' => 403));
            }
            return true;
        },
        'callback' => function (WP_REST_Request $request) {
            $raw_title = $request->get_param('title');
            $raw_email = $request->get_param('email');
            if (!is_string($raw_title) || trim(sanitize_text_field($raw_title)) === '') {
                return new WP_Error('hx_bad_title', 'Non-empty title required.', array('status' => 400));
            }
            if (!is_string($raw_email) || !is_email($raw_email)) {
                return new WP_Error('hx_bad_email', 'Valid email required.', array('status' => 400));
            }
            $payload = array(
                'title' => sanitize_text_field($raw_title),
                'email' => sanitize_email($raw_email),
            );
            update_option('hx_probe_submission', $payload, false);
            return new WP_REST_Response(array('saved' => true, 'record' => get_option('hx_probe_submission')), 201);
        },
    ));
});
