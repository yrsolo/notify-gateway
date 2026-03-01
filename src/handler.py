import base64
import html
import json
import os
import re
import time
import uuid
from typing import Any
from urllib import error, request

_ALLOWED_LEVELS = {"info", "warning", "error"}
_ALLOWED_TEMPLATES = {"notification", "error", "raw"}
_ALIAS_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,31}$")
_CHAT_TARGET_RE = re.compile(r"^-?\d+$|^@[A-Za-z][A-Za-z0-9_]{4,}$")
_LEVEL_EMOJI = {
    "info": "🟩",
    "warning": "🟨",
    "error": "🟥",
}


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    del context

    request_id = _resolve_request_id(event)
    _log_event(
        "info",
        "request_received",
        request_id,
        method=str(event.get("httpMethod", "")).upper() or None,
        path=str(event.get("path", "")) or None,
    )

    if _is_help_request(event):
        _log_event("info", "help_response_returned", request_id)
        return _response(200, _help_response_body())

    try:
        api_keys = _load_api_keys()
        token = _required_env("TELEGRAM_BOT_TOKEN")
        chat_id = _required_env("TELEGRAM_CHAT_ID")
        chat_aliases = _load_chat_aliases()
        retry_max_attempts, retry_backoff_seconds = _load_retry_config()
    except ValueError as exc:
        _log_event("error", "config_validation_failed", request_id, error=str(exc))
        return _response(500, {"ok": False, "error": str(exc)})

    auth_header = _get_header(event, "Authorization")
    if not _is_authorized(auth_header, api_keys):
        _log_event("warning", "authorization_failed", request_id)
        return _response(401, {"ok": False, "error": "invalid API key"})

    try:
        payload = _parse_body(event)
        normalized = _validate_payload(payload)
    except ValueError as exc:
        _log_event("warning", "request_validation_failed", request_id, error=str(exc))
        return _response(400, {"ok": False, "error": str(exc)})

    message_text = _format_message(normalized)

    try:
        resolved_chat_id = _resolve_chat_id(chat_id, chat_aliases, normalized)
    except ValueError as exc:
        _log_event("warning", "chat_routing_failed", request_id, error=str(exc))
        return _response(400, {"ok": False, "error": str(exc)})

    try:
        telegram_message_id = _send_telegram_message(
            token=token,
            chat_id=resolved_chat_id,
            text=message_text,
            retry_max_attempts=retry_max_attempts,
            retry_backoff_seconds=retry_backoff_seconds,
        )
    except RuntimeError as exc:
        _log_event("error", "telegram_send_failed", request_id, error=str(exc))
        return _response(502, {"ok": False, "error": str(exc)})

    _log_event("info", "request_succeeded", request_id, telegram_message_id=telegram_message_id)
    return _response(200, {"ok": True, "telegram_message_id": telegram_message_id})


def _is_help_request(event: dict[str, Any]) -> bool:
    method = str(event.get("httpMethod", "")).upper()
    path = str(event.get("path", ""))

    if method == "GET" and path.rstrip("/") == "/notify/help":
        return True

    try:
        payload = _parse_body(event)
    except ValueError:
        return False

    help_value = payload.get("help")
    return help_value is True


def _help_response_body() -> dict[str, Any]:
    return {
        "ok": True,
        "usage": "POST /notify",
        "required_fields": ["project", "title", "message"],
        "optional_fields": [
            "env",
            "level",
            "template",
            "tags",
            "extra",
            "chat_id",
            "chat_alias",
        ],
        "examples": {
            "minimal": {
                "project": "billing",
                "title": "Queue lag",
                "message": "Queue > 1000",
            },
            "routed": {
                "project": "billing",
                "title": "Error spike",
                "message": "5xx > 2%",
                "template": "error",
                "chat_alias": "ops",
            },
        },
    }


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"missing required env var: {name}")
    return value


def _load_api_keys() -> set[str]:
    raw_value = _required_env("NOTIFY_API_KEYS")
    keys = {k.strip() for k in raw_value.split(",") if k.strip()}
    if not keys:
        raise ValueError("NOTIFY_API_KEYS must contain at least one key")
    return keys


def _load_chat_aliases() -> dict[str, str]:
    raw_value = os.getenv("TELEGRAM_CHAT_ALIASES", "").strip()
    if not raw_value:
        return {}

    aliases: dict[str, str] = {}
    for pair in raw_value.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            raise ValueError(
                "invalid TELEGRAM_CHAT_ALIASES format: expected alias=chat_id pairs"
            )

        alias, target = pair.split("=", 1)
        alias = alias.strip()
        target = target.strip()

        if not _ALIAS_RE.fullmatch(alias):
            raise ValueError(f"invalid chat alias '{alias}' in TELEGRAM_CHAT_ALIASES")
        if not _is_valid_chat_target(target):
            raise ValueError(f"invalid chat target for alias '{alias}'")
        if alias in aliases:
            raise ValueError(f"duplicate chat alias '{alias}' in TELEGRAM_CHAT_ALIASES")

        aliases[alias] = target

    return aliases


def _load_retry_config() -> tuple[int, float]:
    max_attempts_raw = os.getenv("TELEGRAM_RETRY_MAX_ATTEMPTS", "1").strip()
    backoff_raw = os.getenv("TELEGRAM_RETRY_BACKOFF_SECONDS", "0").strip()

    try:
        max_attempts = int(max_attempts_raw)
    except ValueError as exc:
        raise ValueError("TELEGRAM_RETRY_MAX_ATTEMPTS must be an integer") from exc

    if max_attempts < 1 or max_attempts > 10:
        raise ValueError("TELEGRAM_RETRY_MAX_ATTEMPTS must be between 1 and 10")

    try:
        backoff_seconds = float(backoff_raw)
    except ValueError as exc:
        raise ValueError("TELEGRAM_RETRY_BACKOFF_SECONDS must be a number") from exc

    if backoff_seconds < 0:
        raise ValueError("TELEGRAM_RETRY_BACKOFF_SECONDS must be >= 0")

    return max_attempts, backoff_seconds


def _get_header(event: dict[str, Any], key: str) -> str:
    headers = event.get("headers") or {}
    if not isinstance(headers, dict):
        return ""
    for header_name, header_value in headers.items():
        if header_name.lower() == key.lower():
            return str(header_value)
    return ""



def _resolve_request_id(event: dict[str, Any]) -> str:
    request_id = _get_header(event, "X-Request-Id").strip()
    if request_id:
        return request_id[:128]
    return uuid.uuid4().hex


def _log_event(level: str, event: str, request_id: str, **context: Any) -> None:
    safe_level = level if level in _ALLOWED_LEVELS else "info"
    payload = {
        "level": safe_level,
        "event": event,
        "request_id": request_id,
    }

    safe_context = {k: v for k, v in context.items() if v is not None}
    if safe_context:
        payload["context"] = safe_context

    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))

def _is_authorized(auth_header: str, keys: set[str]) -> bool:
    if not auth_header.startswith("Bearer "):
        return False
    presented_key = auth_header[len("Bearer ") :].strip()
    return presented_key in keys


def _parse_body(event: dict[str, Any]) -> dict[str, Any]:
    body = event.get("body")
    if body is None:
        raise ValueError("request body is required")

    if isinstance(body, dict):
        return body

    if not isinstance(body, str):
        raise ValueError("request body must be a JSON object")

    if event.get("isBase64Encoded"):
        try:
            body = base64.b64decode(body).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            raise ValueError("request body contains invalid base64")

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        raise ValueError("request body is not valid JSON")

    if not isinstance(parsed, dict):
        raise ValueError("request body must be a JSON object")

    return parsed


def _validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    project = payload.get("project")
    title = payload.get("title")
    message = payload.get("message")

    if not isinstance(project, str) or not project.strip():
        raise ValueError("field 'project' is required and must be a non-empty string")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("field 'title' is required and must be a non-empty string")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("field 'message' is required and must be a non-empty string")

    env = payload.get("env", "prod")
    if not isinstance(env, str) or not env.strip():
        raise ValueError("field 'env' must be a non-empty string")

    level = payload.get("level", "info")
    if not isinstance(level, str) or level not in _ALLOWED_LEVELS:
        raise ValueError("field 'level' must be one of: info, warning, error")

    template = payload.get("template", "notification")
    if not isinstance(template, str) or template not in _ALLOWED_TEMPLATES:
        raise ValueError("field 'template' must be one of: notification, error, raw")

    tags = payload.get("tags")
    if tags is not None:
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
            raise ValueError("field 'tags' must be a list of strings")

    extra = payload.get("extra")
    if extra is not None and not isinstance(extra, dict):
        raise ValueError("field 'extra' must be an object")

    chat_id_override = payload.get("chat_id")
    if chat_id_override is not None:
        if not isinstance(chat_id_override, str) or not _is_valid_chat_target(
            chat_id_override.strip()
        ):
            raise ValueError("field 'chat_id' must be a valid Telegram chat target")
        chat_id_override = chat_id_override.strip()

    chat_alias = payload.get("chat_alias")
    if chat_alias is not None:
        if not isinstance(chat_alias, str) or not _ALIAS_RE.fullmatch(chat_alias.strip()):
            raise ValueError("field 'chat_alias' must be a valid alias string")
        chat_alias = chat_alias.strip()

    if chat_id_override is not None and chat_alias is not None:
        raise ValueError("fields 'chat_id' and 'chat_alias' are mutually exclusive")

    return {
        "project": project.strip(),
        "env": env.strip(),
        "level": level,
        "title": title.strip(),
        "message": message.strip(),
        "template": template,
        "tags": tags,
        "extra": extra,
        "chat_id": chat_id_override,
        "chat_alias": chat_alias,
    }


def _resolve_chat_id(
    default_chat_id: str, aliases: dict[str, str], payload: dict[str, Any]
) -> str:
    chat_id_override = payload.get("chat_id")
    if chat_id_override:
        return str(chat_id_override)

    chat_alias = payload.get("chat_alias")
    if not chat_alias:
        return default_chat_id

    resolved = aliases.get(str(chat_alias))
    if resolved is None:
        raise ValueError(f"unknown chat alias: {chat_alias}")

    return resolved


def _is_valid_chat_target(value: str) -> bool:
    return bool(_CHAT_TARGET_RE.fullmatch(value))


def _format_message(payload: dict[str, Any]) -> str:
    template = payload["template"]
    if template == "raw":
        return html.escape(payload["message"])

    if template == "error":
        return _format_error_message(payload)

    return _format_notification_message(payload)


def _format_notification_message(payload: dict[str, Any]) -> str:
    emoji = _LEVEL_EMOJI[payload["level"]]
    header = (
        f"{emoji} {html.escape(payload['project'])} "
        f"({html.escape(payload['env'])})"
    )
    title = f"<b>{html.escape(payload['title'])}</b>"
    message = html.escape(payload["message"])

    lines = [header, title, message]

    tags = payload.get("tags")
    if tags:
        escaped_tags = ", ".join(html.escape(tag) for tag in tags)
        lines.append(f"<i>tags:</i> {escaped_tags}")

    extra = payload.get("extra")
    if extra:
        extra_pairs = []
        for key, value in extra.items():
            key_s = html.escape(str(key))
            value_s = html.escape(str(value))
            extra_pairs.append(f"{key_s}={value_s}")
        lines.append(f"<i>extra:</i> {'; '.join(extra_pairs)}")

    return "\n".join(lines)


def _format_error_message(payload: dict[str, Any]) -> str:
    header = f"🚨 <b>ERROR</b> {html.escape(payload['project'])} ({html.escape(payload['env'])})"
    title = f"<b>{html.escape(payload['title'])}</b>"
    message = html.escape(payload["message"])

    lines = [header, title, message]

    tags = payload.get("tags")
    if tags:
        escaped_tags = ", ".join(html.escape(tag) for tag in tags)
        lines.append(f"<i>tags:</i> {escaped_tags}")

    extra = payload.get("extra")
    if extra:
        extra_pairs = []
        for key, value in extra.items():
            key_s = html.escape(str(key))
            value_s = html.escape(str(value))
            extra_pairs.append(f"{key_s}={value_s}")
        lines.append(f"<i>context:</i> {'; '.join(extra_pairs)}")

    return "\n".join(lines)


def _send_telegram_message(
    token: str,
    chat_id: str,
    text: str,
    retry_max_attempts: int,
    retry_backoff_seconds: float,
) -> int:
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
    ).encode("utf-8")

    req = request.Request(
        api_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    for attempt in range(1, retry_max_attempts + 1):
        should_retry = False
        retry_delay = retry_backoff_seconds * attempt

        try:
            with request.urlopen(req, timeout=10) as response:
                raw_body = response.read().decode("utf-8")
        except error.URLError as exc:
            err_message = f"telegram request failed: {exc.reason}"
            should_retry = True
        else:
            try:
                parsed = json.loads(raw_body)
            except json.JSONDecodeError as exc:
                raise RuntimeError("telegram response is not valid JSON") from exc

            if not parsed.get("ok"):
                err_message, should_retry, retry_after = _map_telegram_error(parsed)
                if retry_after is not None:
                    retry_delay = float(retry_after)
            else:
                message_id = ((parsed.get("result") or {}).get("message_id"))
                if not isinstance(message_id, int):
                    raise RuntimeError("telegram response does not contain message_id")
                return message_id

        if should_retry and attempt < retry_max_attempts:
            time.sleep(retry_delay)
            continue

        raise RuntimeError(err_message)

    raise RuntimeError("telegram request failed after retries")


def _map_telegram_error(parsed: dict[str, Any]) -> tuple[str, bool, int | None]:
    description = str(parsed.get("description", "unknown telegram error"))
    error_code = parsed.get("error_code")

    if error_code == 400 and "chat not found" in description.lower():
        return (
            "telegram API error: chat not found (check TELEGRAM_CHAT_ID/chat routing)",
            False,
            None,
        )

    if error_code == 401:
        return ("telegram API error: unauthorized (check TELEGRAM_BOT_TOKEN)", False, None)

    if error_code == 403:
        return (
            "telegram API error: forbidden (bot has no access to target chat)",
            False,
            None,
        )

    if error_code == 429:
        retry_after = (parsed.get("parameters") or {}).get("retry_after")
        safe_retry_after = retry_after if isinstance(retry_after, int) and retry_after > 0 else None
        return ("telegram API error: rate limited", True, safe_retry_after)

    if isinstance(error_code, int) and error_code >= 500:
        return (f"telegram API error: temporary upstream failure ({error_code})", True, None)

    return (f"telegram API error: {description}", False, None)


def _response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }
