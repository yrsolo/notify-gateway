# Deploy runbook

Документ описывает безопасный деплой `notify-gateway` в Yandex Cloud Function, обновление API Gateway, smoke-check и rollback.

## 1) Требуемые переменные и секреты

### GitHub Actions Variables (non-secret)
- `YC_FOLDER_ID`
- `YC_FUNCTION_NAME` (или alias `YC_CLOUD_FUNCTION_NAME`)
- `YC_API_GW_NAME` (опционально, default `notify-gateway-gw`)
- `YC_SERVICE_ACCOUNT_ID`
- `YC_FUNCTION_ENTRYPOINT` (опционально, default `handler.handler`)
- `NOTIFY_PUBLIC_BASE_URL` (опционально, например `https://api.example.com`)
- `TELEGRAM_CHAT_ID` (можно хранить как variable или secret)

### GitHub Actions Secrets
- `YC_SA_JSON_CREDENTIALS` — JSON ключ service account (raw JSON или base64 от JSON).
- `NOTIFY_API_KEYS` — runtime ключ(и) функции. Пример: `prod-key-1,prod-key-2`.
- `TELEGRAM_BOT_TOKEN` — токен Telegram-бота формата `123456789:AA...`.
- `NOTIFY_API_KEY` — один рабочий ключ для smoke-check запроса к `/notify`.
- `TELEGRAM_CHAT_ID` (если не задан как variable) — числовой id чата, например `-1001234567890`.

> Значения секретов не должны выводиться в лог.

## 2) Что делает deploy workflow

Файл: `.github/workflows/deploy.yml` (GitHub Environment `production`).

Триггеры:
- `push` в `main`;
- `workflow_dispatch` с выбором `dry_run=true/false`.

Основные шаги:
1. Определяет режим dry-run:
   - для `workflow_dispatch` — по input;
   - для `push` — автоматически включает dry-run, если не хватает runtime-секретов.
2. Валидирует обязательные переменные.
3. Деплоит Function через `yc-actions/yc-sls-function@v4` (только если `DRY_RUN=false`).
4. Получает `YC_IAM_TOKEN` из `YC_SA_JSON_CREDENTIALS` без использования `yc` CLI.
5. Запускает Python bootstrap `tools/yc_bootstrap.py` и получает `NOTIFY_ENDPOINT` (+ gateway metadata).
6. Запускает `infra/scripts/smoke_notify.sh` (в dry-run или реальном режиме).

## 3) Bootstrap YC_API_GW_NAME и NOTIFY_ENDPOINT

Если gateway еще не создан или значения переменных утеряны, их можно восстановить:

```bash
python tools/yc_bootstrap.py \
  --folder-id <folder-id> \
  --gateway-name <gw-name> \
  --function-name <function-name> \
  --service-account-id <sa-id> \
  --spec-template infra/apigw.yaml \
  --spec-rendered build/apigw.rendered.yaml \
  --iam-token <iam-token> \
  --output-env
```

Bootstrap tool:
- создаёт/обновляет API Gateway `notify-gateway-gw` (или имя из `YC_API_GW_NAME`);
- рендерит `infra/apigw.yaml` в файл `build/apigw.rendered.yaml`;
- печатает env-пары (`YC_API_GW_NAME`, `YC_API_GW_ID`, `NOTIFY_ENDPOINT`) для экспорта в CI.

Если задан `NOTIFY_PUBLIC_BASE_URL`, то endpoint формируется как `<NOTIFY_PUBLIC_BASE_URL>/notify`.

## 4) Локальные проверки перед релизом

```bash
ruff check .
pytest -q

YC_FOLDER_ID=<folder-id> YC_FUNCTION_NAME=notify-gateway \
infra/scripts/yc_deploy_function.sh --dry-run

python tools/yc_bootstrap.py \
  --folder-id <folder-id> \
  --gateway-name notify-gateway-gw \
  --function-name notify-gateway \
  --service-account-id <sa-id> \
  --spec-template infra/apigw.yaml \
  --spec-rendered build/apigw.rendered.yaml \
  --iam-token <iam-token> \
  --dry-run

NOTIFY_ENDPOINT=https://example/notify NOTIFY_API_KEY=dummy \
infra/scripts/smoke_notify.sh --dry-run
```

## 5) Rollback runbook

### 5.1 Trigger rollback
Запускать rollback, если выполняется хотя бы один критерий:
- smoke-check падает 2 запуска подряд;
- доля 5xx по gateway > 5% в течение 5 минут;
- критический сбой отправки в Telegram.

### 5.2 Function rollback
1. Получить список версий функции:
   ```bash
   yc serverless function version list --function-name "$YC_FUNCTION_NAME" --folder-id "$YC_FOLDER_ID"
   ```
2. Выбрать предыдущую стабильную версию.
3. Обновить API Gateway spec на стабильную интеграцию через `tools/yc_bootstrap.py` (с ref на стабильный `infra/apigw.yaml`).
4. Выполнить smoke-check.

### 5.3 API Gateway rollback
1. Вернуть предыдущую стабильную спецификацию:
   ```bash
   git checkout <stable-tag> -- infra/apigw.yaml
   ```
2. Применить её:
   ```bash
   python tools/yc_bootstrap.py \
     --folder-id <folder-id> \
     --gateway-name <gw-name> \
     --function-name <function-name> \
     --service-account-id <sa-id> \
     --spec-template infra/apigw.yaml \
     --spec-rendered build/apigw.rendered.yaml \
     --iam-token <iam-token>
   ```
3. Выполнить smoke-check и проверить логи.

### 5.4 Пост-rollback проверка
- `POST /notify` smoke-check возвращает `200` и `ok=true`.
- В логах функции нет всплеска 5xx в течение 10 минут.
- Обновлён статус в `docs/execution/PROGRESS.md`.

## 6) Безопасность
- Никогда не печатать секреты (`YC_SA_JSON_CREDENTIALS`, `NOTIFY_API_KEY`, `TELEGRAM_BOT_TOKEN`).
- Для shell-скриптов использовать `set -euo pipefail`.
- Для секретных участков CI использовать `set +x` и mask.
