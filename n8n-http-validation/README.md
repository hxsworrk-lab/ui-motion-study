# Native n8n HTTP workflow checks

**Hx Works · Self-initiated engineering study · Synthetic records**

This study asks whether one workflow can recover from transient JSON HTTP failures, stop on permanent failures, and validate and deduplicate a batch before writing rows.

The workflow runs in **n8n 2.43.7**, using native HTTP Request, IF, Wait, Split Out, Remove Duplicates and Stop and Error nodes. The source API and row receiver are our own loopback fixtures. They are not Google Sheets or a customer service.

## Recorded checks

| Scenario | Source requests | Row writes | Expected result |
| --- | ---: | ---: | --- |
| Normal response | 1 | 2 | Complete |
| One HTTP 429, then success | 2 | 2 | Recover |
| One HTTP 503, then success | 2 | 2 | Recover |
| Permanent HTTP 400 | 1 | 0 | Stop with an error; do not retry |
| Persistent HTTP 503 | 3 | 0 | Stop after the third attempt |
| Three records with one repeated ID | 1 | 2 | Keep the first record for that ID |
| A batch containing a record without an ID | 1 | 0 | Reject the whole batch before writing |

The harness compares n8n's execution JSON with the receiver's request counts, stored rows and write events. Expected failure branches must report an execution error; a process merely exiting is insufficient. For the duplicate case, checking write events prevents the receiver's upsert from hiding an extra write.

[Recorded results](observed-results.json) · [Selected native execution fields](native-execution-summary.json) · [Workflow generator and runner](run_validation.py) · [Synthetic API and receiver](fixture_server.py)

## What this establishes

- A transient-status gate with a fixed one-second wait and a maximum of three source requests.
- Batch validation before splitting records into writes.
- First-record-wins deduplication by ID within one batch.
- Explicit failure paths that leave the test receiver unchanged.

These are bounded checks of this workflow. They do not establish production reliability, a customer fix, native Google Sheets integration, OAuth handling, provider-level exactly-once delivery, concurrent runs, arbitrary timeout or malformed-body handling, or support for every API's retry rules. The fixed delay does not parse `Retry-After` or implement exponential backoff.

No client material, account credentials, API keys or live cloud services were used. The implementation and written explanation were prepared with AI-assisted tools. It is not prior employment or paid client work.

## Inspect or rerun

Reading the files and results does not require an account or installation. Replaying the checks requires Python 3.11+, Node.js 24.x, and the pinned n8n package and its SQLite binding. The recorded run used Windows and Node.js 24.18.0; other operating systems have not been tested.

The manifest and lock file use the official `n8n-2.43.7.tgz` archive from [the npm registry](https://registry.npmjs.org/n8n/-/n8n-2.43.7.tgz). Its integrity is:

```text
sha512-Ni38zpDiHZaGnQ6dak9XoAL41HDv0okRkqdqptJknRhCsjop18dL2unzBNrBD2i7rqQ8n5mdkRwxMd2PGQEcyA==
```

Place that archive beside the manifest before using `npm ci`. The dependency tree is substantial; it is not included here. Our installation skipped package scripts, then used SQLite's official prebuilt binding. Do not disable TLS verification if a download fails. n8n and its dependencies retain their own licences; no n8n vendor code or binaries are redistributed here.

With the pinned CLI installed locally, run:

```text
python -B run_validation.py --scenario all
```

The harness imports inactive, manual-trigger workflows into a dedicated local SQLite instance. State, generated keys, logs and execution outputs go into ignored `.local/`. It does not use a cloud n8n account, publish webhooks or need Google credentials. Do not point the test at a production instance.

After a full replay, `python -B export_evidence.py` exports the public reports from the existing records without running n8n again. Raw logs, stacks, local paths, instance metadata and generated keys are excluded from the export. Use a fresh output directory for another replay so earlier records remain intact.

`HX_N8N_CLI` can point to an existing pinned CLI, `HX_NODE_EXECUTABLE` can select Node, and `HX_N8N_CHECK_ROOT` can select a separate disposable output directory. The published replay used the existing pinned local installation; it did not repeat a clean dependency installation in this directory.

Before any client work, the actual workflow, material and tool permissions, acceptance checks, revisions, source handover, fee and payment would be agreed.
