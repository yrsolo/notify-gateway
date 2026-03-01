import base64
import html
import json
import os
from typing import Any
from urllib import error, request

_ALLOWED_LEVELS = {"info", "warning", "error"}
_ALLOWED_TEMPLATES = {"notification", "error", "raw"}
_LEVEL_EMOJI = {
    "info": "🟩",
    "warning": "🟨",
    "error": "🟥",
}


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    del context

    try:
        api_keys = _load_api_keys()
        token = _required_env("TELEGRAM_BOT_TOKEN")
        chat_id = _required_env("TELEGRAM_CHAT_ID")
    except ValueError as exc:
        return _response(500, {"ok": False, "error": str(exc)})

    auth_header = _get_header(event, "Authorization")
    if not _is_authorized(auth_header, api_keys):
        return _response(401, {"ok": False, "error": "invalid API key"})

    try:
        payload = _parse_body(event)
        normalized = _validate_payload(payload)
    except ValueError as exc:
        return _response(400, {"ok": False, "error": str(exc)})

    message_text = _format_message(normalized)

    try:
        telegram_message_id = _send_telegram_message(
            token=token,
            chat_id=chat_id,
            text=message_text,
        )
    except RuntimeError as exc:
        return _response(502, {"ok": False, "error": str(exc)})

    return _response(200, {"ok": True, "telegram_message_id": telegram_message_id})


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


def _get_header(event: dict[str, Any], key: str) -> str:
    headers = event.get("headers") or {}
    for header_name, header_value in headers.items():
        if header_name.lower() == key.lower():
            return str(header_value)
    return ""


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

    return {
        "project": project.strip(),
        "env": env.strip(),
        "level": level,
        "title": title.strip(),
        "message": message.strip(),
        "template": template,
        "tags": tags,
        "extra": extra,
    }


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


def _send_telegram_message(token: str, chat_id: str, text: str) -> int:
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

    try:
        with request.urlopen(req, timeout=10) as response:
            raw_body = response.read().decode("utf-8")
    except error.URLError as exc:
        raise RuntimeError(f"telegram request failed: {exc.reason}")

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError:
        raise RuntimeError("telegram response is not valid JSON")

    if not parsed.get("ok"):
        description = parsed.get("description", "unknown telegram error")
        raise RuntimeError(f"telegram API error: {description}")

    message_id = ((parsed.get("result") or {}).get("message_id"))
    if not isinstance(message_id, int):
        raise RuntimeError("telegram response does not contain message_id")

    return message_id


def _response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }
