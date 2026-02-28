#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${YC_TOKEN:-}" ]]; then
  echo "ERROR: YC_TOKEN is not set" >&2
  exit 1
fi

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: required command '$1' is not installed" >&2
    exit 1
  fi
}

require_cmd curl
require_cmd jq

iam_json=$(curl -sS -X POST "https://iam.api.cloud.yandex.net/iam/v1/tokens" \
  -H "Content-Type: application/json" \
  -d "{\"yandexPassportOauthToken\":\"${YC_TOKEN}\"}")

iam_token=$(jq -r '.iamToken // empty' <<<"$iam_json")
expires_at=$(jq -r '.expiresAt // empty' <<<"$iam_json")

if [[ -z "$iam_token" ]]; then
  echo "ERROR: failed to exchange YC_TOKEN to IAM token" >&2
  jq . <<<"$iam_json" >&2 || true
  exit 1
fi

echo "IAM token acquired (masked): ${iam_token:0:8}..."
echo "IAM token expires at: ${expires_at}"

auth_header="Authorization: Bearer ${iam_token}"

clouds_json=$(curl -sS -H "$auth_header" "https://resource-manager.api.cloud.yandex.net/resource-manager/v1/clouds")

echo

echo "Clouds:"
jq -r '.clouds[]? | "- \(.id)\t\(.name)\torg=\(.organizationId // "-")"' <<<"$clouds_json"

if [[ -n "${YC_CLOUD_ID:-}" ]]; then
  cloud_id="$YC_CLOUD_ID"
else
  cloud_id=$(jq -r '.clouds[0].id // empty' <<<"$clouds_json")
fi

if [[ -z "$cloud_id" ]]; then
  echo
  echo "No cloud ID found (set YC_CLOUD_ID to force folder lookup)."
  exit 0
fi

folders_json=$(curl -sS -H "$auth_header" \
  "https://resource-manager.api.cloud.yandex.net/resource-manager/v1/folders?cloudId=${cloud_id}")

echo

echo "Folders in cloud ${cloud_id}:"
jq -r '.folders[]? | "- \(.id)\t\(.name)\tstatus=\(.status)"' <<<"$folders_json"
