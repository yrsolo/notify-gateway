# Current Stage — S6 (P2): Reliability & polish

Owner: engineering  
Target: improve reliability and maintainability after P0/P1 stabilization.

## S6-T12A — Telegram error mapping + optional retry/backoff ✅
Goal: make Telegram failure responses more actionable and add safe retry for temporary failures.

Files changed:
- `src/handler.py`
- `tests/test_handler.py`
- `README.md`

Acceptance criteria:
- [x] Telegram API error mapping returns clearer user-facing errors for common classes (401/403/400 chat not found/429/5xx).
- [x] Optional retry/backoff is configurable via env vars and defaults to no retries.
- [x] Retry applies only to temporary failures (network/429/5xx) and does not retry permanent auth/access errors.
- [x] Unit tests cover retry and mapping behavior.

Test plan:
- [x] `ruff check .`
- [x] `pytest -q`

Rollout:
- Backward-compatible defaults (`TELEGRAM_RETRY_MAX_ATTEMPTS=1`, `TELEGRAM_RETRY_BACKOFF_SECONDS=0`).

Rollback:
- Revert retry/mapping changes in `src/handler.py` and related tests.

## S6-T12B — Structured logs + request_id correlation ⏳
Goal: add lightweight structured logs and request correlation id.

Acceptance criteria:
- [ ] Handler logs key lifecycle events in stable JSON shape.
- [ ] Request id is accepted from header or generated if absent.
- [ ] Error logs include request id and safe context without secrets.
- [ ] Unit tests validate request id propagation.

## S6-T12C — Expand contract tests and edge-case coverage ⏳
Goal: harden API contract with additional negative/edge tests.

Acceptance criteria:
- [ ] Add tests for malformed headers/body corner cases and base64 decoding.
- [ ] Add tests for help-mode precedence and auth boundaries.
- [ ] Add tests for retry-env validation and response shape stability.
