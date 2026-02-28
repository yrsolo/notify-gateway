# Переменные окружения, секреты и доступы (Yandex Cloud)

Этот документ фиксирует, что нужно подготовить, чтобы агент мог **самостоятельно** делать деплой/обновления notify-gateway в Yandex Cloud.

## 1) Runtime переменные (в Cloud Function)

Обязательные:

- `NOTIFY_API_KEYS` (secret)  
  CSV ключей для Bearer-авторизации, пример: `key1,key2,key3`.
- `TELEGRAM_BOT_TOKEN` (secret)  
  Токен бота от BotFather.
- `TELEGRAM_CHAT_ID` (sensitive config)  
  Chat ID (личка/группа/канал), куда отправлять уведомления.

Рекомендованные дополнительные (опционально):

- `NOTIFY_MAX_MESSAGE_LEN` (config) — лимит длины `message`.
- `NOTIFY_MAX_EXTRA_LEN` (config) — лимит длины сериализованного `extra`.
- `LOG_LEVEL` (config) — уровень логирования (`INFO`, `DEBUG`, ...).

---

## 2) Deploy/CI переменные для работы с Yandex Cloud

Чтобы агент мог сам выполнять команды `yc ...`:

### Аутентификация (один из вариантов)
- `YC_TOKEN` (secret) — OAuth token для CLI, **или**
- `YC_IAM_TOKEN` (secret) — короткоживущий IAM token.

### Контекст
- `YC_CLOUD_ID` (config) — Cloud ID.
- `YC_FOLDER_ID` (config) — Folder ID, где ресурсы функции/API GW.

### Идентификаторы ресурсов
- `YC_FUNCTION_NAME` (config) — имя функции (например `notify-gateway`).
  - Допустимый alias для окружения Codex/GitHub Variables: `YC_CLOUD_FUNCTION_NAME` (используется как fallback в workflow).
- `YC_FUNCTION_ID` (config) — ID функции (если уже создана).
- `YC_API_GW_NAME` (config) — имя API Gateway.
- `YC_API_GW_ID` (config) — ID API Gateway (если уже создан).
- `YC_SERVICE_ACCOUNT_ID` (config) — SA для вызова функции из API Gateway.

### Сеть/домен (опционально)
- `YC_DOMAIN` (config) — ваш домен для gateway.
- `YC_DNS_ZONE_ID` (config) — DNS zone ID (если автоматизируем DNS).

---

## 3) Минимальные роли в IAM

Для service account, под которым будет деплой/обновление:

- `serverless.functions.editor` — создавать/обновлять функцию.
- `api-gateway.editor` — создавать/обновлять API Gateway.
- `iam.serviceAccounts.user` — использовать service account при интеграциях.
- `logging.writer` — писать логи (если требуется отдельная роль).

Для service account интеграции API Gateway → Function:

- `serverless.functions.invoker` на целевую функцию.

> Точный набор ролей можно сузить после первого успешного деплоя (принцип least privilege).

---

## 4) Что нужно получить от владельца проекта до старта реализации

1. Значения:
   - `YC_CLOUD_ID`, `YC_FOLDER_ID`;
   - `YC_SERVICE_ACCOUNT_ID` (или право создать новый SA);
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`;
   - начальный `NOTIFY_API_KEYS`.
2. Способ аутентификации агента в YC (`YC_TOKEN` или процесс выдачи IAM token).
3. Решение по домену (используем gateway URL или сразу custom domain).

---

## 5) Правила безопасности

- Никогда не коммитить секреты в git.
- Секреты хранить в CI/CD secret storage или YC Secret Manager.
- Минимум прав для SA и регулярная ротация токенов/ключей.
- Отдельные ключи для `dev/stage/prod` окружений.

---

## 6) Быстрый preflight-check перед деплоем

- [ ] `yc` CLI установлен и авторизован.
- [ ] Выбран `YC_CLOUD_ID` / `YC_FOLDER_ID`.
- [ ] Есть доступ на update/create Function и API Gateway.
- [ ] Проверен Telegram бот (`getMe`) и корректность `TELEGRAM_CHAT_ID`.
- [ ] Подготовлен набор runtime env vars.

---


### CLI недоступен? Используйте API-автообнаружение

Если `yc` CLI не установлен в runtime, можно выполнить автообнаружение через HTTP API:

```bash
./scripts/yc_discovery_via_api.sh
```

Скрипт:
- обменивает `YC_TOKEN` на короткоживущий `iamToken`;
- выводит список доступных cloud;
- выводит список folder для `YC_CLOUD_ID` (или для первой доступной cloud).

## 7) Troubleshooting Codex runtime (если переменные/доступ "как будто есть", но не видны)

### Почему `YC_TOKEN` может не появляться в `printenv`

Частые причины в Codex:

1. Секрет добавлен **после** запуска текущего контейнера, а контейнер использует кэш состояния.
2. Секрет добавлен в карточке окружения, но не применён к уже запущенной сессии (нужен restart/recreate environment).
3. Ожидалось, что секрет будет доступен как env, но фактически он подключается только для новых задач после пересоздания.
4. **Новый чат сам по себе может не помочь**: если используется тот же Codex Environment с включённым кэшем контейнера, вы получаете тот же runtime без новых secret/env.

### Почему бывает "нет доступа" к YC API

В этом runtime запросы идут через `HTTP(S)_PROXY` (`proxy:8080`). Если прокси временно недоступен или режет конкретный хост, `curl` может вернуть `CONNECT tunnel failed`.

### Как поправить (чеклист)

1. В UI окружения проверить, что заданы:
   - Secret: `YC_TOKEN`;
   - Env var: `YC_FOLDER_ID=b1g42qj26s1u7gv7bufm`.
2. Нажать `Сбросить кэш` и перезапустить/пересоздать environment.
3. Если не помогло — создать **новый отдельный Environment** (другой slug/имя), заново добавить secret/env и запустить задачу уже в нём.
4. Запустить новую задачу и проверить:
   ```bash
   printenv | rg '^YC_'
   ```
5. Проверить сеть через прокси (не отключая системные `HTTP_PROXY/HTTPS_PROXY`):
   ```bash
   curl -sS -o /dev/null -w 'HTTP:%{http_code} IP:%{remote_ip} ERR:%{errormsg}\n' https://iam.api.cloud.yandex.net/
   curl -sS -o /dev/null -w 'HTTP:%{http_code} IP:%{remote_ip} ERR:%{errormsg}\n' https://api.cloud.yandex.net/
   ```
6. После этого запускать autodiscovery YC ресурсов.

### Минимальный autodiscovery после фикса

```bash
curl -sS -H "Authorization: Bearer $YC_TOKEN" \
  "https://resource-manager.api.cloud.yandex.net/resource-manager/v1/clouds?folderId=${YC_FOLDER_ID}"
```

