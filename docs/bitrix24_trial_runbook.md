# Bitrix24 Trial Validation Runbook

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Purpose

This runbook is the practical path for the first controlled validation against a real Bitrix24 trial portal.

Use it when you want to:
- keep the current MVP in a demo-safe state locally;
- switch only the Bitrix24 boundary from mock to real;
- verify whether the portal accepts CRM and task writes;
- debug configuration, field mapping, or worker-state issues without guessing.

This is an integration-validation guide, not a production rollout guide.

## Validation strategy

Do not switch everything to real at once.

Use the phases in this order:
1. Confirm the local mock baseline still works.
2. Keep `AI_PROVIDER=mock`, switch only `BITRIX_MODE=real`.
3. Validate the Bitrix24 write path with one synthetic happy-path request.
4. Validate one review-needed request.
5. Only after that, consider `AI_PROVIDER=openai`.

This isolates failures cleanly:
- if the happy path fails in phase 2, the problem is in Bitrix24 config, CRM mode, field mapping, or portal permissions;
- if phase 2 passes and phase 5 fails, the problem is in the AI boundary, not the Bitrix boundary.

## What you need from the portal

Prepare these values before editing `.env`:
- incoming webhook URL with CRM and task permissions;
- portal base URL, for example `https://your-portal.bitrix24.com`;
- one test responsible user ID that can own created entities and tasks;
- decision whether the portal should use `legacy` or `universal` CRM mode;
- confirmation that you will test only with synthetic data.

If the portal has custom CRM fields, you may also need to adjust:
- `config/field_mapping.yaml`

## Choosing the CRM mode

Use `BITRIX_CRM_MODE=legacy` when:
- the portal uses classic leads;
- you want the most straightforward first validation path;
- you want the code path that explicitly maps phone and email.

Use `BITRIX_CRM_MODE=universal` when:
- the portal is expected to accept `crm.item.add`;
- `entityTypeId=1` is the intended CRM entity target for your portal setup;
- the trial portal is already aligned with the universal CRM path.

If you are unsure, start with `legacy`.

## Recommended `.env` for the first real Bitrix pass

Start from `.env.example`, then use values like these:

```env
ENVIRONMENT=development
DEBUG=true

AI_PROVIDER=mock
BITRIX_MODE=real
BITRIX_CRM_MODE=legacy

BITRIX24_WEBHOOK_URL=https://your-portal.bitrix24.com/rest/1/your-webhook-token
BITRIX24_BASE_URL=https://your-portal.bitrix24.com

WORKER_AUTOSTART=true
INTAKE_WEBHOOK_SECRET=change_me_to_a_local_secret
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_me_to_a_local_password
```

Notes:
- do not commit `.env`;
- keep synthetic names, emails, phones, and company names;
- keep `AI_PROVIDER=mock` for the first real Bitrix pass;
- keep one local SQLite DB until the validation path is stable.

## Pre-flight checks

Before sending any request:

1. Run:

```bash
pytest -q
ruff check .
```

2. Start the app:

```bash
docker compose up --build
```

Or:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

3. Confirm:
- `GET /health` returns healthy output;
- `GET /docs` opens;
- `GET /` asks for Basic Auth;
- the admin settings page shows `bitrix_mode=real` and the expected `bitrix_crm_mode`;
- `WORKER_AUTOSTART=true` is active.

## First happy-path request

Use one deterministic synthetic request that should route, not review:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/intake ^
  -H "Content-Type: application/json" ^
  -H "X-Webhook-Secret: change_me_to_a_local_secret" ^
  -d "{\"idempotency_key\":\"bitrix-real-0001\",\"source\":\"web_form\",\"name\":\"Ivan Synthetic\",\"email\":\"ivan.synthetic@example.com\",\"phone\":\"+37360000111\",\"company\":\"Demo Integration SRL\",\"message\":\"Нужна интеграция Bitrix24 CRM, настройка лидов и автоматизация обработки заявок.\"}"
```

Expected local behavior:
- HTTP `202 Accepted`;
- a `request_id`;
- masked raw payload in the response.

Expected pipeline behavior:
- `received`
- `processing`
- `classified`
- `routed`
- `bitrix_syncing`
- `completed`

Expected real-portal behavior:
- one CRM entity is created;
- one task is created;
- the local request detail page shows Bitrix IDs and a best-effort portal URL.

## Review-needed validation request

Send one ambiguous request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/intake ^
  -H "Content-Type: application/json" ^
  -H "X-Webhook-Secret: change_me_to_a_local_secret" ^
  -d "{\"idempotency_key\":\"bitrix-real-0002\",\"source\":\"web_form\",\"message\":\"Нужна автоматизация, но пока сами не понимаем, что именно и как лучше сделать.\"}"
```

Expected behavior:
- the request lands in `/admin/review`;
- no Bitrix entity is created automatically;
- detail view shows the review-needed status and the timeline.

This confirms the human-review gate still works even when Bitrix mode is real.

## Where to inspect the result

Use these local surfaces first:
- `/admin/requests`
- `/admin/requests/{request_id}`
- `/admin/review`
- `/admin/settings`

Check these things on the request detail page:
- current status;
- `error_message`, if present;
- AI classification block;
- routing decision block;
- Bitrix entity rows;
- processing timeline entries such as `bitrix_sync_started`, `bitrix_failed`, `completed`.

Then verify the created CRM item and task in the real portal.

## Exact failure interpretation

### Status becomes `review_needed`

Meaning:
- the AI boundary intentionally did not allow auto-routing.

Common reasons:
- low confidence;
- ambiguous request content;
- fallback AI result.

Action:
- this is not a Bitrix24 failure;
- test Bitrix with a clearer happy-path request first.

### Status becomes `failed_retryable`

Meaning:
- Bitrix returned a transient failure;
- the worker will retry automatically on the next polling pass.

Current behavior:
- `retry_count` increments;
- once `retry_count >= WORKER_MAX_RETRY_ATTEMPTS`, the request becomes `failed`.

Common reasons:
- network issue;
- Bitrix24 timeout;
- HTTP `429`;
- Bitrix24 `5xx`.

Action:
- wait for the next worker pass;
- inspect the detail timeline for `pipeline_failed_retryable`;
- if it stabilizes as `failed`, inspect portal availability and webhook health.

### Status becomes `failed`

Meaning:
- the error is treated as final;
- or retry attempts were exhausted.

Most likely causes:
- `BITRIX24_WEBHOOK_URL` is empty or malformed;
- webhook returned `401` or `403`;
- request payload was rejected with HTTP `400`;
- unsupported `BITRIX_CRM_MODE`;
- field mapping does not match the target portal.

Action:
- open the request detail page and inspect `error_message`;
- check the timeline entries `bitrix_failed` and `pipeline_failed`;
- correct `.env` or `config/field_mapping.yaml`;
- send a new idempotency key after fixing config.

## Common trial-portal pitfalls

### Worker is not running

Symptom:
- requests stay in `received`.

Cause:
- `WORKER_AUTOSTART=false`;
- or the app process was restarted without a running worker.

Fix:
- set `WORKER_AUTOSTART=true`;
- restart the app;
- resubmit or use a new request.

### Wrong webhook permissions

Symptom:
- final status `failed`;
- `error_message` or timeline implies auth/config failure.

Fix:
- regenerate or reconfigure the incoming webhook with CRM and task scopes;
- update `BITRIX24_WEBHOOK_URL` in `.env`.

### Wrong CRM mode

Symptom:
- Bitrix rejects the request with HTTP `400`;
- or the portal creates nothing even though the pipeline reaches Bitrix sync.

Fix:
- switch `BITRIX_CRM_MODE` between `legacy` and `universal`;
- retest with a fresh `idempotency_key`.

### Field mapping mismatch

Symptom:
- status `failed`;
- request is rejected by Bitrix even though auth is valid.

Fix:
- inspect `config/field_mapping.yaml`;
- align field names with the actual portal fields;
- remember that custom fields differ between portals.

### Reusing the same idempotency key

Symptom:
- the API returns the existing request rather than creating a new validation case.

Fix:
- always use a new `idempotency_key` for each real-mode attempt.

## Safe operating rules during validation

- Use synthetic data only.
- Do not show the real webhook URL in screenshots or screen shares.
- Do not claim the portal run is production-ready after one happy-path test.
- Do not switch AI and Bitrix to real simultaneously for the first pass.
- Do not edit `.env` live during a demo unless necessary.

## Recommended validation sequence

1. Mock baseline passes locally.
2. Real Bitrix happy path passes with `AI_PROVIDER=mock`.
3. Real Bitrix review-needed path behaves correctly.
4. Only then test `AI_PROVIDER=openai` if desired.
5. Capture sanitized notes about:
   - chosen CRM mode;
   - webhook scope used;
   - any mapping overrides needed;
   - exact failure modes encountered.

## Confirmed local baseline

As of July 4, 2026, the following runtime checks were confirmed locally against a real Bitrix24 trial portal:

- `AI_PROVIDER=mock`
- `BITRIX_MODE=real`
- `BITRIX_CRM_MODE=legacy`
- happy-path intake reaches `completed`
- local Bitrix entity records are created for `crm.lead` and `task`
- a general low-signal request can be routed to `review_needed`
- admin actions were exercised against live runtime records:
  - `Approve`
  - `Reprocess AI`
  - `Retry Bitrix`
  - `Drop`

Important note:
- `Retry Bitrix` can race with the in-process worker when `WORKER_AUTOSTART=true`, because `failed_retryable` records are automatically picked up by the worker queue.
- For a controlled manual retry check, temporarily disable worker autostart or pause the worker loop first.

## If you want the next engineering step

After the first portal validation, the most useful follow-up is:
- document the portal-specific field mapping deltas;
- add a masked real-mode troubleshooting note to the repo;
- optionally add a small non-destructive integration smoke helper for local operators.
