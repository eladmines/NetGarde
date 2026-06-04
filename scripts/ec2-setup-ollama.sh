#!/usr/bin/env bash
# Enable local Ollama AI review on EC2 (t3.medium+ with enough free disk).
# Run on the host after deploy: sudo bash scripts/ec2-setup-ollama.sh
set -euo pipefail

REPO_ROOT="${NETGARDE_REPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$REPO_ROOT"

MODEL="${OLLAMA_MODEL:-llama3.2:3b}"
ENV_FILE="${NETGARDE_ENV_FILE:-/etc/netgarde/backend.env}"

echo "Checking free disk (need several GB for Ollama image + model)..."
df -h / /var/lib/docker 2>/dev/null || df -h /

echo "Starting Ollama (compose profile: ai)..."
export COMPOSE_PROFILES=ai
docker compose -f docker-compose.yml pull ollama
docker compose -f docker-compose.yml up -d ollama

echo "Pulling model ${MODEL} (one-time download)..."
docker exec netgarde-ollama ollama pull "$MODEL"

echo "Enabling NETWORK_REVIEW_MODE=ollama in ${ENV_FILE}..."
if sudo grep -q '^NETWORK_REVIEW_MODE=' "$ENV_FILE" 2>/dev/null; then
  sudo sed -i.bak 's/^NETWORK_REVIEW_MODE=.*/NETWORK_REVIEW_MODE=ollama/' "$ENV_FILE"
  sudo rm -f "${ENV_FILE}.bak"
else
  echo "NETWORK_REVIEW_MODE=ollama" | sudo tee -a "$ENV_FILE" >/dev/null
fi

docker compose -f docker-compose.yml up -d backend

echo "Done. Open the dashboard and use Regenerate on AI review (first call may be slow)."
