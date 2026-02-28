# IAM least-privilege matrix

## Current baseline roles (observed in project docs)

Для deploy service account в текущем baseline:
- `serverless.functions.editor`
- `api-gateway.editor`
- `iam.serviceAccounts.user`
- `logging.writer`

Для интеграции API Gateway -> Function:
- `serverless.functions.invoker` на целевую функцию

Источник baseline: `docs/ENV_AND_ACCESS.md`.

## Target least-privilege matrix

### 1) CI Deploy Service Account
- `serverless.functions.editor` (scoped to target folder)
- `api-gateway.editor` (scoped to target folder)
- `iam.serviceAccounts.user` (только на конкретный integration SA)
- `lockbox.payloadViewer` (если runtime секреты читаются из Lockbox в pipeline)

### 2) API Gateway Integration Service Account
- `serverless.functions.invoker` (только на конкретную функцию)

### 3) Observability / Read-only
- `logging.viewer` для on-call инженеров
- `monitoring.viewer` (если используются метрики YC Monitoring)

## Hardening actions
1. Ограничить роли уровнем folder/resource, убрать организационные/глобальные выдачи.
2. Разделить SA для deploy и runtime integration.
3. Запретить постоянные токены, перейти на short-lived IAM token issuance в CI.
4. Проводить quarterly review ролей и удалять неиспользуемые binding-правила.

## Acceptance checks
- [ ] Нет wildcard-ролей уровня organization для deploy SA.
- [ ] Integration SA не имеет editor/admin ролей.
- [ ] Все role bindings документированы и привязаны к владельцу.
- [ ] Проведён dry-run deploy после ужесточения ролей.
