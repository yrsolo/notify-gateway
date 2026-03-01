# Current Stage — S4 (P0): Stabilize CI/Deploy

Owner: engineering
Target: reduce CI fragility by removing `yc` CLI usage in GitHub Actions.

## S4-T08A — Python YC API bootstrap tool ✅ (plan completed)
Goal: create a small Python utility used in CI to create/update API Gateway endpoint and (if applicable) sync secrets.

Files to create/change:
- `tools/yc_bootstrap.py` (new)  [NOTE: do not implement now, plan-only]
- `docs/plan/S4-T08A.md` (new)

Acceptance criteria:
- [x] Plan describes required YC API operations (gateway create/update, spec update, deployment).
- [x] Plan lists required inputs (service account JSON / IAM token method / folder_id / cloud_id etc).
- [x] Plan specifies outputs consumed by CI (NOTIFY_ENDPOINT, gateway id/name).
- [x] Plan includes rollback steps.

Test plan:
- [ ] Smoke: run tool in dry-run mode in CI (no changes), validate auth + permissions.
- [ ] Smoke: run tool against a test env to ensure endpoint exists and is callable.

Rollout:
- Introduce tool in parallel (no deletion of old path).
Rollback:
- Keep old yc CLI path until new path is proven in prod.

## S4-T08B — Update GitHub Actions deploy workflow ✅
Goal: switch deploy workflow to call `tools/yc_bootstrap.py` instead of `yc` CLI scripts.

Files to create/change:
- `.github/workflows/deploy.yml`
- `docs/plan/S4-T08B.md` (new)

Acceptance criteria:
- [x] `yc` CLI installation removed from workflow.
- [x] Workflow exports same env outputs (NOTIFY_ENDPOINT etc).
- [x] Smoke-check step still runs.

Test plan:
- [ ] CI run on branch with dry-run.
- [ ] One controlled deploy to staging.

Rollback:
- Revert workflow file.

## S4-T08C — Add smoke tests for bootstrap + endpoint ✅
Goal: ensure CI validates that endpoint exists and notification call works.

Files to create/change:
- `infra/scripts/smoke_notify.sh`
- `docs/plan/S4-T08C.md` (new)

Acceptance criteria:
- [x] Smoke test checks HTTP status + basic JSON shape.
- [x] Smoke test runs after deploy.

## S4-T08D — Document secrets/env + rollback ✅
Goal: make it obvious what secrets are needed and how to recover from failures.

Files to create/change:
- `docs/plan/S4-T08D.md` (new)
- Update README or docs if such section already exists.

Acceptance criteria:
- [x] List of required GH secrets and example values format.
- [x] Clear rollback instructions.
