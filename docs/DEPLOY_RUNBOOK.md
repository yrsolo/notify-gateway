# Deploy runbook (Stage 2)

Документ описывает безопасный деплой `notify-gateway` в Yandex Cloud Function и обновление API Gateway.

## 1) Требуемые переменные и секреты

### GitHub Actions Variables (non-secret)
- `YC_FOLDER_ID`
- `YC_FUNCTION_NAME`
- `YC_API_GW_NAME`
- `YC_SERVICE_ACCOUNT_ID`
- `YC_FUNCTION_ID` (для рендера `infra/apigw.yaml`)

### GitHub Actions Secrets
- `YC_IAM_TOKEN` (предпочтительно) **или**
- `YC_TOKEN` (fallback для обмена в IAM token)

> Значения секретов не должны выводиться в лог.

## 2) Workflow деплоя

Файл: `.github/workflows/deploy.yml`.

Триггеры:
- `push` в `main` (боевой деплой);
- `workflow_dispatch` (ручной запуск, поддержан `dry_run=true/false`).

Основные шаги:
1. Валидация обязательных переменных.
2. Безопасная подготовка IAM token (`::add-mask::`, без `set -x`).
3. Discovery контекста через `infra/scripts/yc_collect_context.sh`.
4. Деплой функции через `infra/scripts/yc_deploy_function.sh`.
5. Валидация/применение API Gateway через `infra/scripts/yc_apply_apigw.sh`.

## 3) Локальный dry-run (без изменения ресурсов)

```bash
YC_FOLDER_ID=<folder-id> \
YC_FUNCTION_NAME=notify-gateway \
infra/scripts/yc_deploy_function.sh --dry-run

YC_FOLDER_ID=<folder-id> \
YC_API_GW_NAME=notify-gateway-gw \
YC_FUNCTION_ID=<function-id> \
YC_SERVICE_ACCOUNT_ID=<sa-id> \
infra/scripts/yc_apply_apigw.sh --dry-run
```

## 4) Rollback runbook

### 4.1 Function rollback
1. Найти предыдущую стабильную версию функции:
   ```bash
   yc serverless function version list --function-name "$YC_FUNCTION_NAME" --folder-id "$YC_FOLDER_ID"
   ```
2. Переключить integration/tag API Gateway на стабильную версию (или вернуть предыдущую спецификацию).
3. Выполнить smoke-check `POST /notify`.

### 4.2 API Gateway rollback
1. Хранить последнюю стабильную спецификацию (`infra/apigw.yaml` в main + release tag).
2. Применить предыдущую стабильную спецификацию:
   ```bash
   yc serverless api-gateway update --id "$YC_API_GW_ID" --spec <previous-spec-path>
   ```
3. Проверить ответ gateway endpoint и логи функции.

## 5) Безопасность и аудит
- Не печатать секреты (`YC_TOKEN`, `YC_IAM_TOKEN`, bot token).
- Для shell-скриптов использовать `set -euo pipefail`.
- Для секретных участков принудительно держать `set +x`.
- Все ошибки деплоя фиксировать в `docs/execution/PROGRESS.md`.
