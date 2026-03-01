# Current Stage — S5 (P1): Product features

Owner: engineering  
Target: add small product improvements without turning handler into a monolith.

## S5-T09 — Message templates (notification / error / raw) ✅
Goal: support selectable message format via payload field `template`.

Files changed:
- `src/handler.py`
- `tests/test_handler.py`
- `README.md`

Acceptance criteria:
- [x] Payload supports `template` with values `notification` (default), `error`, `raw`.
- [x] `notification` keeps existing formatting behavior.
- [x] `error` uses explicit error header and context formatting.
- [x] `raw` sends only message text (escaped), without project/title wrappers.
- [x] Invalid template returns `400` with validation error.

Test plan:
- [x] `pytest -q`
- [x] `ruff check .`

Rollout:
- Backward-compatible: default template remains `notification`.

Rollback:
- Revert template-specific changes in `src/handler.py`.

## S5-T10 — Chat routing (chat_id override + aliases) ⏳
Goal: add optional routing of notifications to specific Telegram chats by alias/override.

Files to create/change:
- `src/handler.py`
- `tests/test_handler.py`
- docs (if contract changes)

Acceptance criteria:
- [ ] Optional payload override for target chat is supported with strict validation.
- [ ] Alias mapping can be configured via env var.
- [ ] Default chat remains unchanged when override is not provided.
- [ ] Unit tests cover routing success/fallback/rejection.

## S5-T11 — Help mode/endpoint (documented usage + examples) ⏳
Goal: add lightweight help behavior for API consumers.

Files to create/change:
- `src/handler.py`
- docs (README / runbook)
- tests

Acceptance criteria:
- [ ] Help mode available via request flag/path.
- [ ] Returns JSON with required fields and examples.
- [ ] Covered by unit tests.
