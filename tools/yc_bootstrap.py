#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, parse, request

API_BASE = "https://serverless-api.cloud.yandex.net/apigateway/v1"
FUNCTIONS_BASE = "https://serverless-functions.api.cloud.yandex.net/functions/v1"
OP_BASE = "https://operation.api.cloud.yandex.net/operations"
PLACEHOLDER_PATTERN = re.compile(r"<YOUR_[A-Z0-9_]+>")


class BootstrapError(RuntimeError):
    pass


@dataclass
class Gateway:
    gateway_id: str
    name: str
    domain: str | None


class YcClient:
    def __init__(self, iam_token: str, folder_id: str) -> None:
        self.iam_token = iam_token
        self.folder_id = folder_id

    def _request(self, method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None
        headers = {"Authorization": f"Bearer {self.iam_token}"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = request.Request(url=url, method=method, headers=headers, data=body)
        try:
            with request.urlopen(req, timeout=60) as response:
                raw = response.read().decode("utf-8")
                if not raw:
                    return {}
                return json.loads(raw)
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise BootstrapError(f"YC API error {exc.code} on {method} {url}: {details}") from exc
        except error.URLError as exc:
            raise BootstrapError(f"Network error on {method} {url}: {exc.reason}") from exc

    def list_gateways(self) -> list[dict[str, Any]]:
        params = parse.urlencode({"folderId": self.folder_id, "pageSize": 1000})
        data = self._request("GET", f"{API_BASE}/apigateways?{params}")
        return data.get("apiGateways", [])

    def list_functions(self) -> list[dict[str, Any]]:
        params = parse.urlencode({"folderId": self.folder_id, "pageSize": 1000})
        data = self._request("GET", f"{FUNCTIONS_BASE}/functions?{params}")
        return data.get("functions", [])

    def create_gateway(self, name: str, openapi_spec: str) -> str:
        payload = {"folderId": self.folder_id, "name": name, "openapiSpec": openapi_spec}
        data = self._request("POST", f"{API_BASE}/apigateways", payload)
        op_id = data.get("id")
        if not op_id:
            raise BootstrapError("Create gateway response does not contain operation id")
        return op_id

    def update_gateway(self, gateway_id: str, openapi_spec: str) -> str:
        params = parse.urlencode({"updateMask": "openapiSpec"})
        payload = {"openapiSpec": openapi_spec}
        data = self._request("PATCH", f"{API_BASE}/apigateways/{gateway_id}?{params}", payload)
        op_id = data.get("id")
        if not op_id:
            raise BootstrapError("Update gateway response does not contain operation id")
        return op_id

    def wait_operation(self, operation_id: str, timeout_s: int, poll_interval_s: int) -> None:
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            data = self._request("GET", f"{OP_BASE}/{operation_id}")
            if data.get("done"):
                if "error" in data:
                    raise BootstrapError(f"Operation {operation_id} failed: {data['error']}")
                return
            time.sleep(poll_interval_s)
        raise BootstrapError(f"Operation {operation_id} timed out after {timeout_s}s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or update YC API Gateway and resolve notify endpoint")
    parser.add_argument("--folder-id", default=os.getenv("YC_FOLDER_ID"), required=os.getenv("YC_FOLDER_ID") is None)
    parser.add_argument("--gateway-name", default=os.getenv("YC_API_GW_NAME", "notify-gateway-gw"))
    parser.add_argument("--function-id", default=os.getenv("YC_FUNCTION_ID"))
    parser.add_argument("--function-name", default=os.getenv("YC_FUNCTION_NAME"))
    parser.add_argument("--service-account-id", default=os.getenv("YC_SERVICE_ACCOUNT_ID"), required=os.getenv("YC_SERVICE_ACCOUNT_ID") is None)
    parser.add_argument("--spec-template", default=os.getenv("APIGW_SPEC_TEMPLATE", "infra/apigw.yaml"))
    parser.add_argument("--spec-rendered", default=os.getenv("APIGW_SPEC_RENDERED", "build/apigw.rendered.yaml"))
    parser.add_argument("--public-base-url", default=os.getenv("NOTIFY_PUBLIC_BASE_URL", ""))
    parser.add_argument("--iam-token", default=os.getenv("YC_IAM_TOKEN"), required=os.getenv("YC_IAM_TOKEN") is None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-env", action="store_true")
    parser.add_argument("--operation-timeout", type=int, default=180)
    parser.add_argument("--poll-interval", type=int, default=5)
    return parser.parse_args()


def render_spec(template_path: str, rendered_path: str, function_id: str, service_account_id: str) -> str:
    template = Path(template_path).read_text(encoding="utf-8")
    rendered = (
        template.replace("<YOUR_FUNCTION_ID>", function_id)
        .replace("<YOUR_SERVICE_ACCOUNT_ID>", service_account_id)
    )

    unresolved = PLACEHOLDER_PATTERN.findall(rendered)
    if unresolved:
        raise BootstrapError(f"Rendered API Gateway spec still has unresolved placeholders: {sorted(set(unresolved))}")

    rendered_target = Path(rendered_path)
    rendered_target.parent.mkdir(parents=True, exist_ok=True)
    rendered_target.write_text(rendered, encoding="utf-8")
    return rendered


def resolve_gateway(gateways: list[dict[str, Any]], name: str) -> Gateway | None:
    for raw in gateways:
        if raw.get("name") == name:
            return Gateway(
                gateway_id=raw.get("id", ""),
                name=raw.get("name", name),
                domain=raw.get("domain"),
            )
    return None


def resolve_function_id(functions: list[dict[str, Any]], name: str) -> str:
    for raw in functions:
        if raw.get("name") == name:
            value = raw.get("id", "")
            if value:
                return value
    raise BootstrapError(f"Unable to resolve function id for function '{name}'")


def endpoint_from(base_url: str, gateway: Gateway | None) -> str:
    if base_url:
        return f"{base_url.rstrip('/')}/notify"
    if gateway and gateway.domain:
        return f"https://{gateway.domain}/notify"
    raise BootstrapError("Unable to resolve NOTIFY_ENDPOINT: neither NOTIFY_PUBLIC_BASE_URL nor gateway domain is available")


def log(msg: str, output_env: bool) -> None:
    if not output_env:
        print(msg, file=sys.stderr)


def main() -> int:
    args = parse_args()
    try:
        client = YcClient(iam_token=args.iam_token, folder_id=args.folder_id)

        function_id = args.function_id
        if not function_id:
            if not args.function_name:
                raise BootstrapError("Either --function-id/YC_FUNCTION_ID or --function-name/YC_FUNCTION_NAME must be provided")
            function_id = resolve_function_id(client.list_functions(), args.function_name)

        rendered_spec = render_spec(
            template_path=args.spec_template,
            rendered_path=args.spec_rendered,
            function_id=function_id,
            service_account_id=args.service_account_id,
        )
        existing = resolve_gateway(client.list_gateways(), args.gateway_name)

        if args.dry_run:
            log("Dry-run mode: gateway mutation is skipped", output_env=args.output_env)
            gateway = existing
        else:
            if existing is None:
                log(f"Creating API Gateway '{args.gateway_name}'", output_env=args.output_env)
                op_id = client.create_gateway(name=args.gateway_name, openapi_spec=rendered_spec)
            else:
                log(f"Updating API Gateway '{args.gateway_name}' ({existing.gateway_id})", output_env=args.output_env)
                op_id = client.update_gateway(gateway_id=existing.gateway_id, openapi_spec=rendered_spec)

            client.wait_operation(
                operation_id=op_id,
                timeout_s=args.operation_timeout,
                poll_interval_s=args.poll_interval,
            )
            gateway = resolve_gateway(client.list_gateways(), args.gateway_name)

        endpoint = endpoint_from(args.public_base_url, gateway)

        if gateway and gateway.gateway_id:
            print(f"YC_API_GW_ID={gateway.gateway_id}")
        print(f"YC_API_GW_NAME={args.gateway_name}")
        if gateway and gateway.domain:
            print(f"YC_API_GW_DOMAIN={gateway.domain}")
        print(f"NOTIFY_ENDPOINT={endpoint}")
        return 0
    except BootstrapError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
