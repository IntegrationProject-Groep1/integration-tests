# End-to-End Test Overview (All Services)

_Last updated: 2026-05-07_

## Why this document exists

Your current `integration-tests` suite is excellent for **contract compatibility** (XML ↔ XSD), but that is only one layer.
To prove “everything works”, we also need to validate **runtime behavior across real services**: queues, retries, databases, side effects, and recovery.

## Current reality (what is already covered)

## 1) Contract coverage (strong)
- `integration-tests/test_contracts.py` validates many cross-team message contracts.
- `integration-tests/test_identity_service_contracts.py` validates Identity payload contract shape from source-level behavior.
- `integration-tests/readiness-report.md` currently reports **60/65 (92%)**.

## 2) DoD static checks (partial)
- `integration-tests/test_dod_checks.py` checks project expectations (file presence, references, etc.).
- This confirms readiness signals, not full runtime behavior.

## 3) True cross-service E2E coverage (limited)
- Some local/integration-style tests exist in service repos (e.g. Planning, Facturatie), but there is no single unified, reproducible full-stack E2E suite in `integration-tests/` that proves complete business journeys.

## Test pyramid for this project

1. **Unit tests** → function/class logic in one service.
2. **Contract tests** → XML payload shape compatibility (your current strength).
3. **Service integration tests** → service + RabbitMQ/DB/external dependency.
4. **System E2E tests** → multi-service business flows with real side effects.
5. **Resilience E2E tests** → outage/retry/DLQ/idempotency under failure.

You are currently strong at levels 1–2, partial at 3, and missing most of 4–5.

## Service-by-service E2E overview

| Service | What is covered now | Missing for “everything works” |
|---|---|---|
| Frontend | Unit + contract fixtures | End-user registration/cancel/payment path against live downstream services |
| CRM | Unit + contract fixtures | Real queue consumption/forwarding + DB persistence + retry behavior |
| Kassa | Unit/integration-style internals | Badge/payment runtime flow to CRM/Facturatie with idempotency checks |
| Facturatie | Unit + some integration tests | Real invoice lifecycle (create/update/cancel/consolidate) from inbound events |
| Planning | Unit + local E2E script(s) | Reproducible CI-safe flow from frontend request to published updates and persistence |
| Identity Service | Source-level contract tests | End-to-end UUID propagation across downstream services |
| Monitoring | Contract-level message checks | Heartbeat loss detection + alerting behavior + recovery visibility |
| Mailing | Contract tests only | Real trigger verification from CRM/Facturatie/Monitoring events |
| Heartbeat | Schema + service presence | Runtime 1s heartbeat continuity and timeout detection path |

## P0 business journeys to automate first

These are the minimum journeys to claim system-level end-to-end confidence:

1. **Registration happy path**
   - Frontend publishes registration
   - CRM persists and forwards
   - Identity UUID assigned/attached
   - Facturatie updates billing state when relevant
   - Mailing confirmation trigger observed

2. **Payment + consumption path**
   - Kassa emits payment/consumption
   - CRM processes and forwards
   - Facturatie invoice state changes are persisted
   - Frontend receives balance/invoice availability updates (if applicable)

3. **Session lifecycle path**
   - Frontend create/update/delete request
   - Planning persists and broadcasts result
   - Frontend/CRM-facing updates are observable

4. **Monitoring path**
   - Heartbeats from services at 1s cadence
   - One service outage is detected
   - Alert/log event emitted
   - Recovery is reflected in status

5. **Critical sad path**
   - Invalid message rejected -> DLQ/rejection flow observed
   - Replay/fix path tested
   - Duplicate message does not create duplicate business state (idempotency)

## What each true E2E test must assert

For every journey, assert all four:

1. **Message-level**: expected routing key/event appears.
2. **State-level**: expected DB/business state exists.
3. **Side-effect-level**: external/system action happened (mail trigger, invoice update, etc.).
4. **Observability-level**: structured log + correlation/master UUID trace exists.

If one of these is missing, it is not a full E2E proof.

## Suggested implementation in `integration-tests/`

Add these new suites:

- `test_e2e_flows.py` (happy-path multi-service journeys)
- `test_e2e_resilience.py` (outage/retry/idempotency)
- `test_e2e_observability.py` (heartbeat/log/alert expectations)

And helper module:

- `helpers/e2e_assertions.py` (polling, queue inspection, correlation-id tracing, timeout helpers)

## Demo-ready acceptance gate

Define “everything works” as:

- All P0 journeys pass in the same run.
- No unexpected DLQ growth.
- Correlation/master UUID traceable through full journey.
- One controlled service outage and recovery demonstrated successfully.
- Contract tests remain green (no schema regressions).

## Recommended rollout plan (before demo)

- **Day 1:** implement registration and payment/consumption E2E in `integration-tests/`.
- **Day 2:** implement session lifecycle + observability E2E.
- **Day 3:** implement sad-path resilience (DLQ/idempotency/outage).
- **Day 4:** stabilize flakiness, timeouts, and test data reset strategy.
- **Day 5:** run full suite + regenerate readiness report with E2E section.

## Important note

Current readiness percentage (92%) is valuable, but it measures mainly **contract fitness**.
For final evaluation criteria (flows + error handling + testing + monitoring), add system E2E evidence as described above.