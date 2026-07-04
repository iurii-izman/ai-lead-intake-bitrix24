# Demo Walkthrough

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Purpose

This walkthrough is the repeatable local demo path for the current repository baseline.

Use it when you need to:
- show the project live in an interview or portfolio review;
- re-create the main happy path quickly;
- capture screenshots against a predictable local state;
- explain the system without relying on hidden setup knowledge.

For a real Bitrix24 trial-portal validation path, use:
- [Bitrix24 trial validation runbook](./bitrix24_trial_runbook.md)

## Demo mode assumptions

Use the demo in fully synthetic local mode:
- `AI_PROVIDER=mock`
- `BITRIX_MODE=mock`
- `WORKER_AUTOSTART=true`
- no real secrets
- no real customer data

This document is intentionally for mock-mode demo and presentation flow.
It is not the primary runbook for the first real Bitrix24 integration pass.

The walkthrough assumes the repository root is:

```text
C:\dev_bitrix24\ai_lead_intake_bitrix24
```

## Setup

### Option A: Docker Compose

1. Copy the example environment file:

```bash
copy .env.example .env
```

2. Start the app:

```bash
docker compose up --build
```

3. Wait until the application is reachable on `http://127.0.0.1:8000`.

### Option B: Local Python

1. Copy the environment file:

```bash
copy .env.example .env
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -e .[dev]
```

4. Start the app:

```bash
uvicorn app.main:app --reload
```

## Pre-demo checks

Before presenting, confirm:

1. `GET /health` returns `{"status":"ok"}` or equivalent healthy output.
2. `GET /docs` opens.
3. `GET /` redirects to or opens the admin UI and asks for Basic Auth.
4. `pytest -q` is green if you need to demonstrate engineering quality.
5. No real data or secrets are visible in the local environment.

## Recommended demo path

This path is optimized for a 5-10 minute walkthrough.

### Step 1: Show the repository positioning

Open:
- `README.md`
- `docs/architecture.md`

Say:
- this is a demo/product prototype, not a commercial deployment;
- the architecture is production-capable;
- the current baseline is already implemented end-to-end.

### Step 2: Open the API docs

Open:
- `http://127.0.0.1:8000/docs`

Show:
- `POST /api/v1/intake`
- `GET /api/v1/intake/{request_id}`

Explain:
- intake is protected by `X-Webhook-Secret`;
- requests are stored first and processed asynchronously;
- the API supports idempotent replay and record lookup.

### Step 3: Submit a new intake request

Use this example request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/intake ^
  -H "Content-Type: application/json" ^
  -H "X-Webhook-Secret: change_me" ^
  -d "{\"idempotency_key\":\"demo-live-0001\",\"source\":\"web_form\",\"name\":\"Ivan Demo\",\"email\":\"ivan.demo.synthetic@example.com\",\"phone\":\"+37360000111\",\"company\":\"Demo Company SRL\",\"message\":\"Нужна интеграция Bitrix24 и 1С, а также автоматизация входящих лидов.\"}"
```

Expected result:
- HTTP `202 Accepted`
- a `request_id`
- masked raw payload in the response

What to say:
- the request is accepted quickly;
- PII is masked in the stored payload representation;
- the worker will process it in the background.

### Step 4: Retrieve the stored request directly

Run:

```bash
curl -H "X-Webhook-Secret: change_me" http://127.0.0.1:8000/api/v1/intake/{request_id}
```

Replace `{request_id}` with the value returned by the previous step.

Expected result:
- HTTP `200`
- the same request metadata and status

What to say:
- external systems can re-check the intake record safely;
- idempotency and retrieval are both explicit.

### Step 5: Show the admin dashboard

Open:
- `http://127.0.0.1:8000/`

Login with the demo credentials from `.env`:
- username: `admin`
- password: `change_me`

Show:
- queue metrics cards;
- requests table;
- status progression when the worker processes the request.

Expected states you may observe:
- `received`
- `processing`
- `classified`
- `review_needed`
- `routed`
- `bitrix_syncing`
- `completed`

### Step 6: Open request detail

Open the newly created request from the queue.

Show:
- masked raw request section;
- AI classification block;
- routing decision block;
- Bitrix entities block;
- processing timeline.

What to emphasize:
- input remains masked;
- AI output is structured;
- routing is deterministic;
- Bitrix writes are isolated behind an adapter boundary;
- the timeline makes the system auditable.

### Step 7: Demonstrate a review-needed flow

Use a more ambiguous request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/intake ^
  -H "Content-Type: application/json" ^
  -H "X-Webhook-Secret: change_me" ^
  -d "{\"idempotency_key\":\"demo-live-0002\",\"source\":\"web_form\",\"message\":\"Нужна какая-то автоматизация, пока не уверены что именно.\"}"
```

Open:
- `/admin/review`

Show:
- the request in the review queue;
- detail page with low-confidence or review-driven outcome;
- available manual actions.

Explain:
- AI does not auto-decide everything;
- low-confidence cases are explicitly routed to human review.

### Step 8: Demonstrate admin action

From the detail page, show one of:
- `Approve`
- `Reprocess AI`
- `Retry Bitrix`
- `Drop`

Recommended live action:
- use `Approve` on a review-needed record or `Reprocess AI` on a dropped/review item.

What to show after the action:
- status changes;
- new timeline entries;
- Bitrix mock entities appearing when the flow completes.

### Step 9: Show Bitrix result path

On a completed request detail page, show:
- CRM entity row
- task row
- synthetic Bitrix IDs

Explain:
- in demo mode this is mocked;
- in real mode the same path goes through the isolated real adapter.

## Fallback demo plan

If the worker timing is awkward in a live setting:

1. Seed demo data:

```bash
python scripts/seed_demo_data.py --database-url sqlite+pysqlite:///./demo.sqlite3 --replace
```

2. Use pre-existing queue items from the seeded dataset.
3. Show both a likely completed-looking item and a review/dropped item already present in the UI.

## What to avoid during the demo

- Do not open `.env`.
- Do not show real Bitrix portal URLs or tokens.
- Do not use real personal data.
- Do not claim production rollout or live customer usage.
- Do not show local machine clutter or unrelated browser tabs in screenshots.

## Fast verification checklist

- `/health` works
- `/docs` works
- intake POST returns `202`
- intake GET returns the saved record
- admin auth is active
- request detail shows masked values
- timeline shows pipeline steps
- completed item shows Bitrix mock entities
- review queue shows uncertain items

## Suggested order for a 7-minute presentation

1. README positioning
2. Architecture diagram
3. `/docs`
4. Live intake POST
5. Admin dashboard
6. Request detail
7. Review queue
8. Mock Bitrix result
