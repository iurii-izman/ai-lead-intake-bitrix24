# Screenshots Capture Checklist

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Goal

Capture a coherent, public-safe visual set from the actual implemented UI and demo flow.

Use this checklist together with:
- `docs/screenshots_plan.md`
- `docs/demo_walkthrough.md`

## Before capture

- Start the app in mock mode.
- Use only synthetic requests.
- Make sure `WORKER_AUTOSTART=true` if you need live pipeline movement.
- Prepare at least one request in each useful state you want to show:
  - completed
  - review_needed
  - dropped
  - failed or failed_retryable if relevant
- Close unrelated apps and browser tabs.

## Required safety checks

- No `.env` contents visible anywhere.
- No real email, phone, name, or company data visible.
- No real Bitrix portal URLs or tokens visible.
- No local filesystem paths shown unless they are intentionally part of the developer-facing presentation.
- No browser bookmarks, chat messages, or desktop notifications visible.

## Recommended capture set

### 1. Cover image

Capture or design a simple flow visual for:

```text
Request -> AI -> Routing -> Bitrix24 -> Task -> Human review
```

Use:
- large readable typography
- no clutter
- no terminal noise

### 2. Architecture

Capture:
- the Mermaid architecture doc rendered cleanly
- or a polished screenshot of the architecture section from docs

Check:
- component names are readable
- no accidental editor chrome dominates the frame

### 3. Dashboard queue

Capture:
- summary cards
- request table
- a mix of statuses

Check:
- masked payloads only
- queue labels readable
- no empty-state screenshot unless you need it deliberately

### 4. Request detail

Capture:
- raw request block
- AI classification
- routing decision
- Bitrix entities
- processing timeline

Check:
- masked values are actually visible as masked
- the timeline shows meaningful transitions
- no duplicate noisy panels dominate the frame

### 5. Review queue / review-needed item

Capture:
- at least one low-confidence or manual-review request
- visible action buttons such as `Approve`, `Reprocess AI`, or `Drop`

Check:
- screenshot communicates human-in-the-loop clearly

### 6. Completed Bitrix result

Capture:
- completed request detail
- CRM entity row
- task row

Check:
- only synthetic Bitrix IDs
- no real URLs or tenant-specific information

## Composition guidance

- Prefer consistent browser zoom and window size.
- Keep the same visual style across the whole set.
- Use light, readable frames.
- Crop aggressively; remove dead space and irrelevant controls.
- If the browser address bar reveals local host details you do not want to show, crop it out.

## Suggested capture order

1. Architecture
2. Dashboard queue
3. Review-needed detail
4. Completed detail
5. Bitrix result block
6. Optional API docs or intake response example

## Final review before publication

- Every visible personal field is synthetic or masked.
- The screenshot order tells a coherent story.
- The set supports the README and Notion case, not a different story.
- The visuals match the current implemented UI rather than an outdated mockup.
