# notify-gateway

Сервис-шлюз для централизованной отправки уведомлений из разных проектов в Telegram через единый HTTP endpoint.

## Текущий статус

Сейчас репозиторий находится на **stage execution** с фокусом на прозрачный трекинг выполнения.

- План этапов: `docs/PLAN.md`
- Исполнительный stage-план: `docs/execution/STAGE_PLAN.md`
- Задачи текущей стадии: `docs/execution/CURRENT_STAGE_TASKS.md`
- Прогресс выполнения: `docs/execution/PROGRESS.md`
- Переменные окружения и доступы для Yandex Cloud: `docs/ENV_AND_ACCESS.md`
- Текущий операционный статус и блокеры Codex/YC: `docs/STATUS.md`
- Security guardrails для CI: `docs/security/CI_GUARDRAILS.md`
- Deploy runbook и rollback: `docs/DEPLOY_RUNBOOK.md`
- SLO-lite и observability checks: `docs/SLO_AND_OBSERVABILITY.md`
- Регламент ротации секретов: `docs/SECRET_ROTATION.md`
- Матрица IAM least privilege: `docs/IAM_LEAST_PRIVILEGE.md`
- On-call/ops playbook: `docs/ONCALL_OPS_PLAYBOOK.md`

## Цель MVP

- `POST /notify`
- Bearer-авторизация по API key
- валидация payload
- пересылка в Telegram Bot API
- деплой в Yandex Cloud Functions + API Gateway
- секреты только в env/secret storage

## Локальный запуск и проверки

### 1. Подготовка окружения

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install pytest ruff
```

### 2. Переменные окружения

- Скопируйте `.env.example` и заполните тестовыми значениями.
- Для infra-конфигов используйте шаблоны:
  - `infra/env/dev.env.example`
  - `infra/env/prod.env.example`
  - `infra/function/env/common.env.example`
  - `infra/function/env/prod.env.example`

> Не коммитьте реальные секреты и `.env` файлы с боевыми значениями.

### 3. Локальные проверки перед PR

```bash
ruff check .
pytest -q
```

Эти же проверки выполняются в `.github/workflows/ci.yml` для pull request.
