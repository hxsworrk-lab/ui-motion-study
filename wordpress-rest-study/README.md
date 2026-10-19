# Hx Works — internal WordPress REST study

A self-initiated, synthetic integration study. This is a recorded capability example, not a paid client deployment or production security certification.

[Read the study page](https://hxsworrk-lab.github.io/ui-motion-study/wordpress-rest-study/) · [Original observed JSON](observed-result.json) · [Handler](hx-form-probe.php) · [Fixture](exercise.php)

## Recorded execution

On 16 October 2026 at 15:18:55 UTC, WordPress 7.1.3 / PHP 8.3.33 executed seven in-process cases with `WP_REST_Server` and `WP_SQLite_DB`. Four capability/nonce failures returned 403; two input-validation failures returned 400. All six preserved the target submission option. A valid request returned 201 and stored the expected sanitized value.

The raw JSON and three source files below are unchanged copies from the recorded study. The original successful run selected the then-current core, which resolved to 7.1.3; the generator subsequently pinned that observed version. Preparing this public package did not rerun the integration test or create a second result.

## Reproduce in an isolated environment

**Do not run the fixture against a production site.** It creates fixed synthetic users and resets its one test option. No real owner account or customer file should be supplied.

The observed setup used Node 24.18.0, npm 11.16.0 and `@wp-playground/cli@3.1.58`. Commands below are PowerShell, run from this folder. They download the official runtime and core; those dependencies are not bundled. Although npm and the output mount are project-local, this CLI version additionally uses a default WordPress cache in the user home directory. Check your storage policy before running it.

```powershell
New-Item -ItemType Directory -Path .runtime,out -Force | Out-Null
npm install --prefix .runtime --cache .npm-cache --ignore-scripts --no-audit --no-fund --save-exact @wp-playground/cli@3.1.58
node make-blueprint.mjs blueprint.json
$studyOutput = (Resolve-Path out).Path
node .runtime/node_modules/@wp-playground/cli/wp-playground.js run-blueprint --blueprint=blueprint.json --mount-dir $studyOutput /hx-output --php=8.3 --verbosity=debug
Get-Content out/result.json
```

The generated blueprint mounts only the explicit output directory. The fixture loads real WordPress functions and uses `wp_set_current_user()` / `rest_do_request()`; it does not mock the WordPress REST server. A new reproduction writes `out/result.json`, leaving the frozen report intact. Do not add the unsupported `--workers` flag to `run-blueprint`.

## Evidence limits

- In-process requests do not validate HTTP parsing, browser interaction, cookie login, real sessions or network CSRF behavior.
- The six unchanged-state observations concern only `hx_probe_submission`, before the one valid write. They do not prove zero writes to every internal table or cache.
- Database persistence after process exit, production MySQL, third-party plugins, SMTP, external APIs, payment gateways and customer acceptance were not tested.
- AI tools were used for authoring. Results in the frozen JSON came from the actual native runtime; they were not inferred from code review.
- Direct cash spend for the original experiment was zero. Network transfer and model/tool/hosting monetary costs were not quantified. This is not a claim of zero total cost or income.

## Frozen file hashes

| File | SHA-256 |
| --- | --- |
| `hx-form-probe.php` | `8b30c62ee98d17807ef490600535a81e16e91d0b8470d1fbab9251ac21124120` |
| `exercise.php` | `6dc3ff5f4b46f328dce944da387d34c0fc6425d6eaedc0b0d97c50ce9954ccea` |
| `make-blueprint.mjs` | `479d0d69256d6699c0dedef9a2e49f2748bfdd533e8392dbf5c9534fb3cb6c8d` |
| `observed-result.json` | `9f58f318b6e1be80ed4947cae38f719595c3504f13d4dcc37bae58c71bc6261a` |

## Sources and licence

[Custom REST endpoints](https://developer.wordpress.org/rest-api/extending-the-rest-api/adding-custom-endpoints/) · [Internal REST dispatch](https://developer.wordpress.org/reference/functions/rest_do_request/) · [Nonce verification](https://developer.wordpress.org/reference/functions/wp_verify_nonce/) · [Playground CLI](https://developer.wordpress.org/playground/developers/local-development/wp-playground-cli/).

The study files in this subdirectory are distributed under GPL-2.0-or-later; a GPL v2 copy is in [LICENSE](LICENSE). This does not add a licence grant for unrelated repository contents. No WordPress core, npm dependency bundle, fonts, customer assets, private execution receipt or credentials are redistributed here.
