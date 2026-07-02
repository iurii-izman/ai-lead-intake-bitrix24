# Screenshot Plan

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Goal
Create public-safe visuals for GitHub, Notion, HH, or a portfolio PDF.

## Safety rules
- Use synthetic data only.
- Mask names, emails, phones, company names, IDs, and webhook values.
- Do not show `.env` contents.
- Do not expose Bitrix24 portal URLs or tokens.
- Do not show raw customer text if it contains personal data.

## Recommended screenshots
1. Cover image
2. Architecture diagram
3. Dashboard queue
4. Request detail with timeline
5. AI classification view
6. Bitrix24 sync result

## Shot descriptions
- Cover image: one-line flow from request to AI to routing to Bitrix24 to task.
- Architecture diagram: components and integration boundaries.
- Dashboard queue: mixed statuses with clear masked payloads.
- Request detail: timeline, confidence gate, routing decision, and draft reply.
- AI classification view: raw input versus structured output.
- Bitrix24 sync result: created entity and task with synthetic identifiers.

## Export checklist
- Check that all visible fields are masked.
- Blur browser address bars if portal or local host details are visible.
- Crop away unrelated desktop chrome.
- Prefer light, readable UI frames.
- Keep the same style across all screenshots.

## Suggested order for publication
1. Cover image
2. Architecture
3. Dashboard
4. Detail view
5. AI output
6. Bitrix24 result
