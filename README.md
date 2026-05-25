# 🛡️ NetGarde

**Network-level DNS firewall and monitoring dashboard for home and small office networks.**

NetGarde intercepts all DNS traffic through a WireGuard VPN tunnel, blocks unwanted domains via dnsmasq, and provides a real-time dashboard to monitor and manage network activity.

---

## 📸 Features

- **DNS-Level Website Blocking** — Block domains via dnsmasq with automatic config sync
- **Real-Time DNS Monitoring** — Live WebSocket feed of all DNS queries as they happen
- **Dashboard & Analytics** — Statistics cards, data grid, and grouped site views
- **Blocked Sites Management** — Full CRUD with categories and search
- **Noise Filtering** — Automatically hides system telemetry, CDN, and OS update noise
- **VPN Integration** — All client traffic routed through WireGuard for transparent DNS control
- **Automatic Log Ingestion** — Systemd service continuously parses dnsmasq logs and pushes to the API

---

## 🏗️ Architecture

```
┌──────────────┐     WireGuard VPN      ┌──────────────────────────────────────┐
│              │◄──────────────────────► │           EC2 Instance               │
│  Home Router │     (UDP 51820)         │                                      │
│  + Clients   │                         │  ┌──────────┐    ┌───────────────┐   │
│              │  DNS queries ──────────►│  │ dnsmasq  │───►│ dnsmasq.log   │   │
└──────────────┘                         │  └──────────┘    └───────┬───────┘   │
                                         │       │                  │           │
                                         │       │ blocked-         │ tail      │
                                         │       │ domains.conf     │           │
                                         │       │                  ▼           │
                                         │  ┌────┴─────┐   ┌───────────────┐   │
                                         │  │ dns-sync │   │ log_watcher   │   │
                                         │  │container │   │ (systemd)     │   │
                                         │  └────┬─────┘   └───────┬───────┘   │
                                         │       │                  │           │
                                         │       ▼                  ▼           │
                                         │  ┌──────────────────────────────┐   │
                                         │  │    FastAPI Backend (Docker)   │   │
                                         │  │    :8000                      │   │
                                         │  └──────────────┬───────────────┘   │
                                         │                 │                    │
                                         └─────────────────┼────────────────────┘
                                                           │
                                                           ▼
┌──────────────────────┐                          ┌────────────────┐
│   React Dashboard    │◄── CloudFront (HTTPS) ──►│   AWS RDS      │
│   (S3 + CloudFront)  │                          │   PostgreSQL   │
│                      │◄── WebSocket (/ws) ──────┤                │
└──────────────────────┘                          └────────────────┘
```

### Data Flow

1. **Client devices** connect to the home router, which tunnels DNS traffic via **WireGuard** to the EC2 instance
2. **dnsmasq** on the EC2 resolves DNS queries, blocking domains listed in `blocked-domains.conf`
3. **dns_log_watcher** (systemd service) tails `dnsmasq.log` in real-time, parses new queries, and sends batches to the backend API every 2–3 seconds
4. **FastAPI backend** broadcasts all queries via **WebSocket** to the live dashboard; by default only **blocked** queries are stored in PostgreSQL (RDS). Set `PERSIST_ALL_DNS=true` for legacy full logging.
5. **dns-sync container** periodically pulls the blocked sites list from the API and regenerates `blocked-domains.conf` for dnsmasq
6. **React dashboard** displays live feed, statistics, and management interfaces via CloudFront

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19, TypeScript, Material UI 7, MUI X Data Grid & Charts |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2, Alembic, Pydantic 2 |
| **Database** | PostgreSQL 16 (AWS RDS) |
| **DNS Server** | dnsmasq |
| **VPN** | WireGuard |
| **Infrastructure** | AWS EC2, CloudFront, S3, ECR |
| **CI/CD** | GitHub Actions |
| **Containers** | Docker, Docker Compose |

---

## 📁 Project Structure

```
NetGarde/
├── frontend/                   # React SPA (dashboard UI)
│   └── src/
│       ├── features/
│       │   ├── dashboard/      # Stats, live feed, data grid, sites view
│       │   ├── blocked-sites/  # Blocked sites CRUD
│       │   └── categories/     # Categories management
│       ├── pages/              # Route pages
│       └── shared/             # Shared utils, hooks, components
│
├── backend/                    # FastAPI REST API + WebSocket
│   └── app/
│       ├── features/
│       │   ├── blocked_sites/  # Models, schemas, repos, services, controllers, routes
│       │   ├── categories/     # Models, schemas, repos, services, controllers, routes
│       │   └── dns_queries/    # Models, schemas, repos, services, controllers, routes
│       ├── shared/             # DB config, middleware, utils, WebSocket manager
│       └── main.py             # FastAPI app entry point
│
├── dns-sync/                   # DNS log watcher + blocked sites sync
│   ├── dns_log_watcher.py      # Real-time log tail → API (systemd service)
│   ├── sync.py                 # Pull blocked sites → dnsmasq config
│   ├── noise_filter.py         # Filters telemetry/CDN noise domains
│   └── netgarde-log-watcher.service  # systemd unit file
│
├── aws/                        # AWS setup scripts (S3, CloudFront, ECR)
├── .github/workflows/          # CI/CD pipelines
│   ├── deploy-backend.yml      # Build & deploy backend to EC2
│   ├── deploy-frontend.yml     # Build & deploy frontend to S3/CloudFront
│   └── deploy-develop.yml      # Develop branch pipeline
│
├── docker-compose.yml          # Production compose (backend + dns-sync)
├── docker-compose.dev.yml      # Development compose (backend + frontend + db + dns-sync)
└── docs/                       # Documentation
    ├── ENV_SETUP.md             # Environment variables guide
    ├── SYSTEM_ARCHITECTURE.md   # Architecture diagram
    └── DEVELOP.md               # Developer guide
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- [Node.js 18+](https://nodejs.org/) (for frontend development)
- [Python 3.11+](https://www.python.org/) (for local backend development)

### Local Development

**1. Clone the repository:**

```bash
git clone https://github.com/your-username/NetGarde.git
cd NetGarde
```

**2. Set up environment files:**

```bash
# Backend
cp backend/.env.example backend/.env.development

# Frontend
cp frontend/.env.example frontend/.env.development
```

See [docs/ENV_SETUP.md](docs/ENV_SETUP.md) for detailed environment variable configuration.

**3. Start all services with Docker Compose:**

```bash
docker compose -f docker-compose.dev.yml up --build
```

This starts:
- **Backend API** at `http://localhost:8000`
- **Frontend** at `http://localhost:3000`
- **PostgreSQL** at `localhost:5432`
- **dns-sync** container (run on demand)

**4. Or run frontend separately (hot reload):**

```bash
cd frontend
npm install
npm start
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| **Blocked Sites** | | |
| `GET` | `/blocked-sites` | List blocked sites (paginated) |
| `POST` | `/blocked-sites` | Add a blocked site |
| `PUT` | `/blocked-sites/{id}` | Update a blocked site |
| `DELETE` | `/blocked-sites/{id}` | Delete a blocked site |
| `GET` | `/blocked-sites/counts-by-category` | Counts grouped by category |
| **Categories** | | |
| `GET` | `/categories` | List categories |
| `POST` | `/categories` | Create a category |
| `PUT` | `/categories/{id}` | Update a category |
| `DELETE` | `/categories/{id}` | Delete a category |
| **DNS Queries** | | |
| `GET` | `/dns-queries` | List DNS queries (paginated, filterable) |
| `POST` | `/dns-queries` | Log a single DNS query |
| `POST` | `/dns-queries/bulk` | Log multiple DNS queries |
| `GET` | `/dns-queries/stats` | Query statistics (total, blocked, top domains) |
| `GET` | `/dns-queries/sites` | Queries grouped by root domain |
| `GET` | `/dns-queries/clients` | List unique client IPs |
| `DELETE` | `/dns-queries/cleanup` | Delete records older than N days |
| `WS` | `/dns-queries/ws` | Real-time WebSocket live feed |

---

## 🏠 Production Deployment

### AWS Infrastructure

| Service | Purpose |
|---------|---------|
| **EC2** | Hosts backend (Docker), dnsmasq, WireGuard, log watcher |
| **RDS** | PostgreSQL database |
| **S3** | Frontend static files |
| **CloudFront** | CDN for frontend + HTTPS proxy for backend API |
| **ECR** | Docker image registry |

### CI/CD

Pushes to `main` or `develop` trigger GitHub Actions workflows:

- **`deploy-backend.yml`** — Builds Docker image, pushes to ECR, SSHs into EC2 to pull and restart
- **`deploy-frontend.yml`** — Builds React app, syncs to S3, invalidates CloudFront cache

### Host Services

On the EC2 instance, two systemd services run alongside Docker:

```bash
# Real-time DNS log watcher (parses dnsmasq logs → API)
sudo systemctl status netgarde-log-watcher

# DNS server
sudo systemctl status dnsmasq

# WireGuard VPN
sudo systemctl status wg-quick@wg0
```

---

## 🧱 Backend Architecture

The backend follows a **layered OOP architecture**:

```
Route (FastAPI endpoint)
  └── Depends() → IDnsQueryService (Protocol interface)
  └── Depends() → Session (database)
  └── Controller (wires HTTP to service)
       └── Service (business logic)
            └── Repository (database operations)
                 └── SQLAlchemy Model
```

Each feature (`blocked_sites`, `categories`, `dns_queries`) follows the same structure:
- **Model** — SQLAlchemy ORM class
- **Schema** — Pydantic validation models (Create, Response)
- **Repository** — Database CRUD operations
- **Service** — Business logic (implements a Protocol interface)
- **Controller** — Thin layer mapping HTTP requests to service calls
- **Route** — FastAPI router with dependency injection
- **Errors** — Custom domain exception classes

---

## 🔧 Key Configuration

### dnsmasq

```bash
# Blocked domains config (auto-generated by dns-sync)
/etc/dnsmasq.d/blocked-domains.conf

# Main dnsmasq config
/etc/dnsmasq.conf
```

### WireGuard

```bash
# VPN config
/etc/wireguard/wg0.conf
```

### Log Watcher

```bash
# Systemd service config
/etc/systemd/system/netgarde-log-watcher.service

# State file (tracks log read position)
/var/lib/netgarde/log_parser_state
```

---

## 📄 License

This project is for educational and personal use.
