#!/usr/bin/env bash
# Enable local Ollama AI review on EC2 (t3.medium+ with enough free disk).
# Run on the host after deploy: sudo bash scripts/ec2-setup-ollama.sh
set -euo pipefail

REPO_ROOT="${TRUSTEDGE_REPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$REPO_ROOT"

MODEL="${OLLAMA_MODEL:-llama3.2:3b}"
ENV_FILE="${TRUSTEDGE_ENV_FILE:-/etc/trustedge/backend.env}"

echo "Checking free disk (need several GB for Ollama image + model)..."
df -h / /var/lib/docker 2>/dev/null || df -h /

echo "Starting Ollama (compose profile: ai)..."
export COMPOSE_PROFILES=ai
docker compose -f docker-compose.yml pull ollama
docker compose -f docker-compose.yml up -d ollama

echo "Pulling model ${MODEL} (one-time download)..."
docker exec trustedge-ollama ollama pull "$MODEL"

set_env_kv() {
  local key="$1" value="$2"
  if sudo grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
    sudo sed -i.bak "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
    sudo rm -f "${ENV_FILE}.bak"
  else
    echo "${key}=${value}" | sudo tee -a "$ENV_FILE" >/dev/null
  fi
}

echo "Enabling Ollama AI review in ${ENV_FILE}..."
set_env_kv NETWORK_REVIEW_MODE ollama
# Prefer host gateway so API reaches Ollama even if backend was started without compose profile ai
set_env_kv OLLAMA_BASE_URL http://host.docker.internal:11434
set_env_kv OLLAMA_MODEL "$MODEL"
set_env_kv LLM_TIMEOUT_SEC 180

COMPOSE_PROFILES=ai docker compose -f docker-compose.yml up -d --force-recreate backend ollama

echo "Clearing cached network review (Redis)..."
docker exec trustedge-redis redis-cli --scan --pattern 'dashboard:network_overview:*' | \
  xargs -r docker exec -i trustedge-redis redis-cli DEL || true

echo "Verifying API -> Ollama from inside backend container..."
if docker exec trustedge-api curl -sf http://host.docker.internal:11434/api/tags >/dev/null; then
  echo "Ollama reachable from backend."
else
  echo "WARNING: backend cannot reach Ollama at host.docker.internal:11434"
  echo "Try: docker exec trustedge-api curl -v http://ollama:11434/api/tags"
fi

echo "Done. Open the dashboard AI overview and click Regenerate (first summary may take 15–90s)."
