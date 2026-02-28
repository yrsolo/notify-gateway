# Текущий статус интеграции с Yandex Cloud (Cloud Codex)

Обновлено: 2026-02-28.

## Что реализовано

- Базовый сервис `POST /notify` с валидацией и тестами (`pytest`, `ruff`).
- CI для pull request: линт + unit tests (`.github/workflows/ci.yml`).
- Автоматизированный deploy workflow (`.github/workflows/deploy.yml`):
  - деплой Cloud Function;
  - bootstrap/обновление API Gateway;
  - smoke-check `POST /notify`;
  - dry-run fallback при неполных runtime-секретах.
- Infra-скрипты для deploy и обслуживания:
  - `infra/scripts/yc_collect_context.sh`
  - `infra/scripts/yc_deploy_function.sh`
  - `infra/scripts/yc_apply_apigw.sh`
  - `infra/scripts/yc_bootstrap_notify_endpoint.sh`
  - `infra/scripts/smoke_notify.sh`
- Эксплуатационная документация закрыта:
  - `docs/DEPLOY_RUNBOOK.md`
  - `docs/SLO_AND_OBSERVABILITY.md`
  - `docs/SECRET_ROTATION.md`
  - `docs/IAM_LEAST_PRIVILEGE.md`
  - `docs/ONCALL_OPS_PLAYBOOK.md`

## Стадийный статус

- Stage 0 — Discovery & readiness baseline: ✅
- Stage 1 — Repo hardening: ✅
- Stage 2 — Deploy automation: ✅
- Stage 3 — Runtime validation & observability: ✅
- Stage 4 — Production readiness: ✅

Текущий режим: **maintenance** (точечные улучшения и синхронизация документации под изменения).

## Текущие блокеры

- Отсутствует настроенный remote `origin` в локальном окружении контейнера, поэтому обязательная синхронизация `git fetch origin && git rebase origin/main` недоступна в этом раннере.

## Следующие шаги

1. Поддерживать актуальность runbook при изменении workflow/infra-скриптов.
2. Проверить боевой deploy из GitHub Environment `production` после обновления DNS (`NOTIFY_PUBLIC_BASE_URL`, если используется кастомный домен).
3. Периодически подтверждать least-privilege и ротацию секретов по регламенту.
