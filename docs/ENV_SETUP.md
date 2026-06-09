# Environment Variables Setup Guide

How to configure TrustEdge for local development and production.

**Canonical references:** [backend/.env.example](../backend/.env.example) and [frontend/.env.example](../frontend/.env.example) list every variable. This guide covers setup steps and the most important groups.

## Overview

| Environment | Backend file | Frontend file |
|-------------|--------------|---------------|
| Development | `backend/.env.development` | `frontend/.env.development` |
| Production (Docker) | `backend/.env.production` | `frontend/.env.production` |
| Production (EC2 host) | `/etc/trustedge/backend.env` | Built into S3 deploy |

`.env` files are gitignored. Copy from `.env.example` templates.

## Backend Environment Variables

### Development (`.env.development`)

Create `backend/.env.development`:

```env
# Development Environment Variables
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=12345
POSTGRES_DB=trustedge
DB_URL=postgresql+psycopg2://postgres:12345@db:5432/trustedge

# Application Configuration
PYTHONUNBUFFERED=1
ENVIRONMENT=development

# Logging
LOG_LEVEL=DEBUG

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# DNS ingest (default: only blocked queries persisted to RDS; live feed always uses WebSocket)
PERSIST_ALL_DNS=false
```

### Production (`.env.production`)

Create `backend/.env.production`:

```env
# Production Environment Variables
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_ME_IN_PRODUCTION
POSTGRES_DB=trustedge
DB_URL=postgresql+psycopg2://postgres:CHANGE_ME_IN_PRODUCTION@db:5432/trustedge

# Application Configuration
PYTHONUNBUFFERED=1
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Security — set strong random values in production
ADMIN_API_TOKEN=REPLACE_WITH_LONG_RANDOM_SECRET
DNS_INGEST_TOKEN=REPLACE_WITH_LONG_RANDOM_SECRET
DEVICE_TOKEN_SECRET=REPLACE_WITH_LONG_RANDOM_SECRET
WG_AGENT_TOKEN=REPLACE_WITH_LONG_RANDOM_SECRET

# WireGuard enroll
VPN_ENDPOINT=your-ec2-ip:51820
VPN_SERVER_PUBLIC_KEY=REPLACE_WITH_wg0_PUBLIC_KEY
WG_AGENT_URL=http://172.17.0.1:9109
```

## Frontend Environment Variables

### Development (`.env.development`)

Create `frontend/.env.development`:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
GENERATE_SOURCEMAP=true

# Optional locally; required when backend ADMIN_API_TOKEN is set
# REACT_APP_ADMIN_API_TOKEN=REPLACE_WITH_LONG_RANDOM_SECRET
```

### Production (`.env.production`)

Create `frontend/.env.production`:

```env
# FastAPI origin — not the CloudFront/S3 dashboard URL
REACT_APP_API_BASE_URL=http://your-ec2-ip:8000
REACT_APP_ADMIN_API_TOKEN=REPLACE_WITH_LONG_RANDOM_SECRET
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
```

## Quick Setup

### Option 1: Manual Creation

1. Copy the example content above into new files:
   - `backend/.env.development`
   - `backend/.env.production`
   - `frontend/.env.development`
   - `frontend/.env.production`

2. Update the values for your environment, especially:
   - Database passwords
   - API URLs
   - Production secrets

### Option 2: Using Command Line

**Windows (PowerShell):**
```powershell
# Backend development
@"
# Development Environment Variables
POSTGRES_USER=postgres
POSTGRES_PASSWORD=12345
POSTGRES_DB=trustedge
DB_URL=postgresql+psycopg2://postgres:12345@db:5432/trustedge
PYTHONUNBUFFERED=1
ENVIRONMENT=development
LOG_LEVEL=DEBUG
API_HOST=0.0.0.0
API_PORT=8000
"@ | Out-File -FilePath backend\.env.development -Encoding utf8

# Backend production
@"
# Production Environment Variables
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_ME_IN_PRODUCTION
POSTGRES_DB=trustedge
DB_URL=postgresql+psycopg2://postgres:CHANGE_ME_IN_PRODUCTION@db:5432/trustedge
PYTHONUNBUFFERED=1
ENVIRONMENT=production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
"@ | Out-File -FilePath backend\.env.production -Encoding utf8

# Frontend development
@"
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
GENERATE_SOURCEMAP=true
"@ | Out-File -FilePath frontend\.env.development -Encoding utf8

# Frontend production
@"
REACT_APP_API_BASE_URL=https://api.yourdomain.com
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
"@ | Out-File -FilePath frontend\.env.production -Encoding utf8
```

**Linux/Mac:**
```bash
# Backend development
cat > backend/.env.development << EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=12345
POSTGRES_DB=trustedge
DB_URL=postgresql+psycopg2://postgres:12345@db:5432/trustedge
PYTHONUNBUFFERED=1
ENVIRONMENT=development
LOG_LEVEL=DEBUG
API_HOST=0.0.0.0
API_PORT=8000
EOF

# Backend production
cat > backend/.env.production << EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_ME_IN_PRODUCTION
POSTGRES_DB=trustedge
DB_URL=postgresql+psycopg2://postgres:CHANGE_ME_IN_PRODUCTION@db:5432/trustedge
PYTHONUNBUFFERED=1
ENVIRONMENT=production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
EOF

# Frontend development
cat > frontend/.env.development << EOF
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
GENERATE_SOURCEMAP=true
EOF

# Frontend production
cat > frontend/.env.production << EOF
REACT_APP_API_BASE_URL=https://api.yourdomain.com
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
EOF
```

## Docker Compose Configuration

The docker-compose files are already configured to use the appropriate `.env` files:

- **Development**: `docker-compose.dev.yml` uses `.env.development`
- **Production**: `docker-compose.yml` uses `.env.production`

## Important Notes

1. **Never commit `.env` files** - They are already in `.gitignore`
2. **Update production passwords** - Change `CHANGE_ME_IN_PRODUCTION` to secure passwords
3. **Update API URLs** - Set correct production API URLs in frontend `.env.production`
4. **Security** - Use strong, unique passwords for production
5. **Secrets** - Store sensitive values in environment variables or secrets management systems

## Environment Variable Reference

### Core (backend)

| Variable | Description | Dev | Prod |
|----------|-------------|-----|------|
| `DB_URL` | PostgreSQL connection string | `...@db:5432/...` | RDS URL |
| `ENVIRONMENT` | Environment name | `development` | `production` |
| `LOG_LEVEL` | Logging verbosity | `DEBUG` | `INFO` |
| `LOG_JSON` | Structured JSON logs | `0` | `1` (see [CLOUDWATCH_LOGGING.md](CLOUDWATCH_LOGGING.md)) |
| `PERSIST_ALL_DNS` | Store all DNS queries in RDS | `false` | `false` |

### Security tokens (backend)

| Variable | Used by | Notes |
|----------|---------|-------|
| `ADMIN_API_TOKEN` | Dashboard, policy/device admin APIs | Empty = auth disabled (dev only) |
| `DNS_INGEST_TOKEN` | `dns_log_watcher`, `dns-sync` | Required on EC2 for ingest and policy pull |
| `WG_AGENT_TOKEN` | Backend → `trustedge-wg-agent` | Must match host agent token |
| `DEVICE_TOKEN_SECRET` | VPN client device tokens | Signs tokens issued at enroll |
| `ENROLL_BOOTSTRAP_TOKEN` | `POST /v1/enroll` (optional) | TrustEdgeClient `--api-token` |

Frontend: set `REACT_APP_ADMIN_API_TOKEN` to the same value as `ADMIN_API_TOKEN`.

Host agent: set `TRUSTEDGE_WG_AGENT_TOKEN` in the systemd unit — see [host-agent/README.md](../host-agent/README.md).

### VPN & host agent (backend)

| Variable | Description |
|----------|-------------|
| `VPN_ENDPOINT` | Public `host:51820` returned in enroll config |
| `VPN_SERVER_PUBLIC_KEY` | WireGuard server public key |
| `WG_AGENT_URL` | Host agent URL from Docker (`http://172.17.0.1:9109`) |

### Real-time usage (backend)

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis for live throughput | `redis://redis:6379/0` |
| `USAGE_REDIS_ENABLED` | Enable Redis usage window | `true` |
| `USAGE_HISTORY_MINUTES` | Chart history window | `60` |
| `BANDWIDTH_ALERT_MIB_PER_SEC` | Throughput alert threshold | `50` |

### Behavior & policy (backend)

Key tuning variables — full list in [backend/.env.example](../backend/.env.example):

| Variable | Description |
|----------|-------------|
| `BEHAVIOR_ALERT_THRESHOLD` | Score above which alerts fire |
| `BEHAVIOR_AUTO_BLOCK_THRESHOLD` | Score above which auto-blocks trigger |
| `BEHAVIOR_FAST_START` | Lower profile readiness bar (dev/demo) |
| `POLICY_PACK_FETCH_ENABLED` | Fetch upstream block lists on startup |
| `FORBIDDEN_COUNTRY_ENABLED` | Geo DNS blocking rules |
| `NETWORK_REVIEW_MODE` | Dashboard AI review: `template` \| `openai` \| `ollama` |

### Frontend

| Variable | Description | Development | Production |
|----------|-------------|-------------|------------|
| `REACT_APP_API_BASE_URL` | FastAPI origin (not CloudFront UI URL) | `http://localhost:8000` | `http://<ec2-ip>:8000` |
| `REACT_APP_ADMIN_API_TOKEN` | Admin bearer token | optional | **required** when backend token set |
| `REACT_APP_ENVIRONMENT` | Environment label | `development` | `production` |
| `GENERATE_SOURCEMAP` | Source maps | `true` | `false` |

## Troubleshooting

### Environment variables not loading

1. Check file names match exactly: `.env.development` or `.env.production`
2. Verify docker-compose file references the correct `.env` file
3. Restart containers after changing `.env` files:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Frontend variables not working

- React requires variables to start with `REACT_APP_`
- Restart the dev server after changing `.env` files
- Clear browser cache if needed

### Database connection issues

- Verify `DB_URL` format is correct
- Check PostgreSQL credentials match
- Ensure database container is running

### Admin API returns 401

- Set `ADMIN_API_TOKEN` in backend and `REACT_APP_ADMIN_API_TOKEN` in frontend to the same value
- Restart frontend dev server after changing `.env`

### Policy blocks not reaching dnsmasq (EC2)

- Verify `DNS_INGEST_TOKEN` is set and matches dns-sync / log-watcher config
- Verify `WG_AGENT_TOKEN` matches `trustedge-wg-agent` — see [host-agent/README.md](../host-agent/README.md)
