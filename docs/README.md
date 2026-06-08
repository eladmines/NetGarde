# NetGarde — Technical documentation

Engineering documentation for the [NetGarde platform](https://github.com/NetGarde/NetGarde) ([organization](https://github.com/NetGarde)). The [root README](../README.md) is the portfolio overview; this folder is for implementation detail.

---

## Documentation map

| Document | Audience | Contents |
|----------|----------|----------|
| [DESIGN.md](DESIGN.md) | Engineers | Domain model, system topology, frontend/backend patterns, extension guide |
| [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) | Engineers, reviewers | Architecture diagram, data flows, trust boundaries |
| [DEVELOP.md](DEVELOP.md) | Contributors | Local setup, pytest, Alembic, branch workflow |
| [DEPLOY.md](DEPLOY.md) | Operators | AWS layout, CI/CD, EC2 host services |
| [ENV_SETUP.md](ENV_SETUP.md) | Operators, devs | Environment variables, tokens, troubleshooting |
| [API.md](API.md) | Integrators | REST and WebSocket endpoint reference |
| [CLOUDWATCH_LOGGING.md](CLOUDWATCH_LOGGING.md) | Operators | Production logging, Insights queries |

---

## Repository layout

| Path | Role |
|------|------|
| `frontend/` | React 19 dashboard (feature-based modules) |
| `backend/` | FastAPI API, WebSocket, policy and ingest pipeline |
| `dns-sync/` | Policy → dnsmasq sync, DNS log watcher |
| `host-agent/` | EC2 host service — WireGuard peers, quarantine, sync trigger |
| `scripts/` | EC2 setup (CloudWatch, tokens, TLS) |
| `.github/workflows/` | CI test, ECR build, S3/EC2 deploy |

---

## Reading paths

**Interview / architecture review**

1. [../README.md](../README.md) — product scope and engineering highlights  
2. [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) — components and flows  
3. [DESIGN.md](DESIGN.md) — design principles and code structure  

**Local development**

1. [DEVELOP.md](DEVELOP.md)  
2. [ENV_SETUP.md](ENV_SETUP.md)  

**Production operations**

1. [DEPLOY.md](DEPLOY.md)  
2. [../host-agent/README.md](../host-agent/README.md)  
3. [CLOUDWATCH_LOGGING.md](CLOUDWATCH_LOGGING.md)  

---

## External references

| Resource | Location |
|----------|----------|
| Backend env catalog | [backend/.env.example](../backend/.env.example) |
| Frontend env catalog | [frontend/.env.example](../frontend/.env.example) |
| Screenshot assets | [images/README.md](images/README.md) |
| VPN enroll client | [NetGardeClient](https://github.com/NetGarde/NetGardeClient) |
| GitHub organization | [NetGarde](https://github.com/NetGarde) |
