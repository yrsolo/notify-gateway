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


## Формат запроса `POST /notify`

Минимальный payload:

```json
{
  "project": "billing",
  "title": "Queue lag",
  "message": "Queue > 1000"
}
```

Дополнительно поддерживается поле `template`:
- `notification` — формат по умолчанию (уровень, проект/env, title, message, tags/extra).
- `error` — акцентированный формат ошибки с заголовком `🚨 ERROR`.
- `raw` — отправляет только `message` (HTML-escaping сохраняется).

Дополнительно поддерживается routing в конкретный чат:
- `chat_id` — прямой override Telegram chat target (например, `-100123456789` или `@alerts_room`).
- `chat_alias` — алиас чата, резолвится из env `TELEGRAM_CHAT_ALIASES`.
- `chat_id` и `chat_alias` взаимоисключающие поля.

Формат `TELEGRAM_CHAT_ALIASES`:

```text
ops=-100123456789,alerts=@alerts_room
```

Если routing-поля отсутствуют, используется дефолтный `TELEGRAM_CHAT_ID`.

Параметры надежности Telegram-запроса (опционально):
- `TELEGRAM_RETRY_MAX_ATTEMPTS` — число попыток отправки (по умолчанию `1`, диапазон `1..10`).
- `TELEGRAM_RETRY_BACKOFF_SECONDS` — базовая задержка между попытками (по умолчанию `0`).

Повторные попытки выполняются только для временных сбоев (`network error`, `429`, `5xx`).


## Help mode

Поддерживаются два способа получить краткую справку по контракту:
- `GET /notify/help`
- `POST /notify` с payload `{ "help": true }`

Ответ содержит `required_fields`, `optional_fields` и примеры payload.
