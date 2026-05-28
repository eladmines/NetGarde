#!/usr/bin/env bash
# Merge deploy-time keys into /etc/netgarde/backend.env without wiping manual settings.
# Used by .github/workflows/deploy-backend.yml on EC2.
set -euo pipefail

ENV_FILE="${NETGARDE_ENV_FILE:-/etc/netgarde/backend.env}"
REPO_ROOT="${NETGARDE_REPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"

# docker compose (ubuntu user, docker group) must read env_file; root-only 600 breaks compose.
fix_env_permissions() {
  if getent group docker >/dev/null 2>&1; then
    sudo chown root:docker "$ENV_FILE"
    sudo chmod 640 "$ENV_FILE"
  else
    local owner="${SUDO_USER:-${USER:-ubuntu}}"
    sudo chown "${owner}:${owner}" "$ENV_FILE"
    sudo chmod 600 "$ENV_FILE"
  fi
}

sudo mkdir -p /etc/netgarde

# Bootstrap when the host env file does not exist yet.
if ! sudo test -f "$ENV_FILE"; then
  if [ -f "$REPO_ROOT/backend/.env.production" ]; then
    echo "Migrating existing $REPO_ROOT/backend/.env.production -> $ENV_FILE"
    sudo cp "$REPO_ROOT/backend/.env.production" "$ENV_FILE"
  else
    echo "Creating $ENV_FILE from backend/.env.production.example"
    sudo cp "$REPO_ROOT/backend/.env.production.example" "$ENV_FILE"
  fi
  fix_env_permissions
fi

token_file_for_key() {
  local key="$1"
  echo "/etc/netgarde/$(echo "$key" | tr '[:upper:]_' '[:lower:]-').token"
}

# Generate stable secrets for placeholder values (first deploy only).
ensure_secret() {
  local key="$1"
  local token_file
  token_file="$(token_file_for_key "$key")"

  local current=""
  current="$(sudo grep -E "^${key}=" "$ENV_FILE" 2>/dev/null | tail -1 | cut -d= -f2- || true)"

  if [ -n "$current" ] && [[ "$current" != *"REPLACE_WITH"* ]] && [ "$current" != "CHANGE_ME" ]; then
    return 0
  fi

  if sudo test -f "$token_file"; then
    # Do not use `<file` with sudo — the shell opens the file as the current user.
    current="$(sudo cat "$token_file" | tr -d '\r\n')"
  else
    current="$(openssl rand -hex 32)"
    echo "$current" | sudo tee "$token_file" >/dev/null
    sudo chmod 600 "$token_file"
    echo "Generated $key (stored in $token_file)"
  fi

  UPDATES+=("${key}=${current}")
}

UPDATES=()
for arg in "$@"; do
  if [[ "$arg" == *=* ]]; then
    UPDATES+=("$arg")
  fi
done

ensure_secret DEVICE_TOKEN_SECRET
ensure_secret DNS_INGEST_TOKEN
ensure_secret ADMIN_API_TOKEN

if [ "${#UPDATES[@]}" -eq 0 ]; then
  echo "No env updates to apply"
  exit 0
fi

UPDATES_JSON="$(printf '%s\n' "${UPDATES[@]}" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().splitlines()))")"

sudo ENV_FILE="$ENV_FILE" UPDATES_JSON="$UPDATES_JSON" python3 <<'PY'
import json
import os

env_file = os.environ["ENV_FILE"]
updates_list = json.loads(os.environ["UPDATES_JSON"])
updates: dict[str, str] = {}
for item in updates_list:
    if not item or "=" not in item:
        continue
    k, v = item.split("=", 1)
    updates[k.strip()] = v

lines: list[str] = []
seen: set[str] = set()

if os.path.isfile(env_file):
    with open(env_file, encoding="utf-8") as f:
        for raw in f:
            if not raw.strip() or raw.lstrip().startswith("#"):
                lines.append(raw if raw.endswith("\n") else raw + "\n")
                continue
            if "=" not in raw:
                lines.append(raw if raw.endswith("\n") else raw + "\n")
                continue
            key = raw.split("=", 1)[0].strip()
            if key in updates:
                lines.append(f"{key}={updates[key]}\n")
                seen.add(key)
            else:
                lines.append(raw if raw.endswith("\n") else raw + "\n")

for key, val in updates.items():
    if key not in seen:
        lines.append(f"{key}={val}\n")

with open(env_file, "w", encoding="utf-8") as f:
    f.writelines(lines)
PY

fix_env_permissions
echo "Updated $ENV_FILE (${#UPDATES[@]} key(s))"
