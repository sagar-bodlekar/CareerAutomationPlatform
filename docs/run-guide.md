# Run Guide — AI Career Automation Platform

> **Version:** 1.0  
> **Last Updated:** June 11, 2026  
> **Total Services:** 10 backend microservices + 1 frontend + 6 infrastructure + 5 monitoring

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Quick Start (5 minutes)](#3-quick-start-5-minutes)
4. [Step-by-Step Setup](#4-step-by-step-setup)
   - [4.1 Environment Configuration](#41-environment-configuration)
   - [4.2 Start Infrastructure](#42-start-infrastructure)
   - [4.3 Install Dependencies](#43-install-dependencies)
   - [4.4 Database Migrations](#44-database-migrations)
   - [4.5 Run Backend Services](#45-run-backend-services)
   - [4.6 Run Frontend](#46-run-frontend)
   - [4.7 Seed Sample Data](#47-seed-sample-data)
5. [Full Stack Docker](#5-full-stack-docker)
6. [Monitoring Stack](#6-monitoring-stack)
7. [Testing Everything](#7-testing-everything)
8. [API Endpoints Map](#8-api-endpoints-map)
9. [Common Tasks](#9-common-tasks)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Browser  │  │   curl   │  │ Postman  │  │  Python  │    │
│  │:3000     │  │          │  │          │  │  Client  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
┌───────▼─────────────▼─────────────▼─────────────▼──────────┐
│                    API GATEWAY (Nginx :80)                   │
│  Auth Rate Limit: 20r/m  |  API Rate Limit: 100r/m          │
│  Routes: /api/v1/{service}/  →  backend containers          │
│          /  →  Frontend SPA                                 │
└───────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬────┘
        │     │     │     │     │     │     │     │     │
┌───────▼┐ ┌──▼──┐ ┌▼────┐ ┌▼───┐ ┌▼────┐ ┌▼──┐ ┌▼────┐ ┌▼───┐
│ Profile│ │Auth │ │Resume │ │Job │ │Match│ │Out-│ │Appli-│ │ AI  │
│:8001   │ │:8002│ │:8003  │ │:8004│ │:8005│ │reach│ │cation│ │Orch.│
│        │ │     │ │       │ │     │ │     │ │:8006│ │:8007 │ │:8009│
└────────┘ └─────┘ └───────┘ └─────┘ └─────┘ └─────┘ └──────┘ └─────┘
            ┌───────┐ ┌───────────┐ ┌───────────────┐
            │Tracking│ │Notificati │ │  Monitoring   │
            │:8010   │ │on:8011    │ │ Prometheus     │
            │        │ │WebSocket  │ │ Grafana :3001  │
            └────────┘ └───────────┘ │ Loki           │
                                     └───────────────┘
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │PostgreSQL│  │  Redis   │  │  MinIO   │  │ PgBouncer│    │
│  │:5432     │  │:6379     │  │:9000     │  │:5433     │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Service Responsibilities:**

| Service | Port | Purpose |
|---------|------|---------|
| **Profile** | 8001 | User profile CRUD (SSOT) |
| **Auth** | 8002 | Registration, login, JWT, OAuth |
| **Resume** | 8003 | Resume generation, PDF, ATS optimization |
| **Job** | 8004 | Job scraping, search, filtering |
| **Match** | 8005 | Profile-job matching engine |
| **Outreach** | 8006 | Cover letter & email generation |
| **Application** | 8007 | Application pipeline, state machine, delivery |
| **AI Orchestrator** | 8009 | LLM integration (Gemini/Groq) |
| **Tracking** | 8010 | Analytics, funnel, export |
| **Notification** | 8011 | In-app notifications via WebSocket |

---

## 2. Prerequisites

### Required Software

| Tool | Version | Check |
|------|---------|-------|
| **Docker & Docker Compose** | Latest | `docker --version && docker compose version` |
| **Python** | 3.12+ | `python --version` |
| **Node.js** | 20+ | `node --version` |
| **npm** | 10+ | `npm --version` |

### Recommended (Optional)

| Tool | Purpose |
|------|---------|
| **psql** (PostgreSQL client) | Direct DB inspection |
| **redis-cli** | Redis inspection |
| **curl / httpie** | API testing |
| **Postman / Insomnia** | API exploration |
| **VS Code** | Development |

### API Keys (for AI features, optional)

- **Google Gemini** (free): https://aistudio.google.com/
- **Groq** (free fallback): https://console.groq.com/

Without API keys, AI features return stub responses (the app still works).

---

## 3. Quick Start (5 minutes)

```bash
# 1. Copy environment config
cp .env.example .env

# 2. Start infrastructure (PostgreSQL, Redis, MinIO)
docker compose up -d postgres redis minio

# 3. Install Python dependencies
pip install -e backend/shared/
pip install -r backend/requirements-shared.txt

# 4. Run database migrations
cd backend && alembic upgrade head && cd ..

# 5. Run tests to verify (run services separately to avoid conftest collision)
cd backend && python -m pytest application_service/tests/ -v --tb=short
cd backend && python -m pytest tracking_service/tests/ -v --tb=short

# 6. Seed sample data
python scripts/seed_data.py

# 7. Start a service (e.g., Profile Service)
cd backend/profile_service && uvicorn app.main:app --reload --port 8001
```

**Open another terminal for the frontend:**

```bash
cd frontend
npm install
npm run dev
```

**Open:** http://localhost:5173 (frontend) or http://localhost:8001/docs (API docs)

---

## 4. Step-by-Step Setup

### 4.1 Environment Configuration

```bash
# From the project root
cp .env.example .env
```

Edit `.env` to set:
- `GEMINI_API_KEY` — For AI features (optional)
- `GROQ_API_KEY` — For AI fallback (optional)
- `JWT_SECRET` — Change to a random 256-bit secret for production

The defaults work for local development without any changes.

### 4.2 Start Infrastructure

```bash
# Start all infrastructure services
docker compose up -d postgres redis minio pgbouncer
```

**What starts:**

| Container | Port | Purpose |
|-----------|------|---------|
| `career-postgres` | 5432 | Main database (PostgreSQL 16) |
| `career-redis` | 6379 | Cache & pub-sub (Redis 7) |
| `career-minio` | 9000, 9001 | Object storage (S3-compatible) |
| `career-pgbouncer` | 5433 | Connection pooling |
| `career-minio-setup` | — | Creates MinIO buckets (runs once) |

**Verify:**

```bash
# Check all services are healthy
docker compose ps

# Test PostgreSQL
docker compose exec postgres pg_isready -U postgres

# Test Redis
docker compose exec redis redis-cli ping  # Should return PONG

# Access MinIO Console
open http://localhost:9001  # minioadmin / minioadmin
```

### 4.3 Install Dependencies

```bash
# Backend: Install shared library in dev mode
pip install -e backend/shared/

# Backend: Install shared requirements
pip install -r backend/requirements-shared.txt

# Frontend: Install npm dependencies
cd frontend && npm install && cd ..
```

> **Windows note:** On Windows, use `py -m pip` or `python -m pip` if `pip` is not in PATH.

**What gets installed:**

| Package | Purpose |
|---------|---------|
| `fastapi`, `uvicorn` | Web framework |
| `sqlalchemy`, `asyncpg`, `alembic` | Database ORM & migrations |
| `pydantic`, `pydantic-settings` | Validation & config |
| `redis` | Caching & pub-sub |
| `httpx` | HTTP client (service-to-service calls) |
| `prometheus-client` | Metrics endpoint |
| `structlog` | Structured JSON logging |
| `google-genai`, `openai` | AI provider SDKs |
| `minio` | S3-compatible object storage |
| `celery` | Async task queue |
| `python-jose`, `passlib`, `cryptography` | Auth |

### 4.4 Database Migrations

```bash
cd backend && alembic upgrade head && cd ..
```

This creates all tables across all microservices in a single PostgreSQL database.

**What gets created (schema: `career`):**

| Service | Tables Created |
|---------|---------------|
| Profile | `user_profiles`, `personal_info`, `skills`, `work_experiences`, `education`, `projects`, `certifications`, `social_links` |
| Auth | `auth_users`, `auth_oauth_connections`, `auth_api_keys` |
| Resume | `resumes`, `resume_files`, `resume_templates` |
| Job | `jobs`, `job_sources` |
| Match | `job_matches` |
| AI Orchestrator | `ai_execution_logs` |
| Outreach | `outreach_content` |
| Application | `applications`, `application_events` |
| Tracking | `application_stats`, `application_funnels`, `daily_application_counts` |

**Verify:**

```bash
# Connect and list tables
docker compose exec postgres psql -U postgres -d career_platform -c "\dt career.*"
```

### 4.5 Run Backend Services

You can run services individually (development mode) or all together via Docker.

#### Option A: Run Individually (for development)

Open a **separate terminal** for each service:

```bash
# Terminal 1: Profile Service
cd backend/profile_service && uvicorn app.main:app --reload --port 8001

# Terminal 2: Auth Service
cd backend/auth_service && uvicorn app.main:app --reload --port 8002

# Terminal 3: Resume Service
cd backend/resume_service && uvicorn app.main:app --reload --port 8003

# Terminal 4: Job Service
cd backend/job_service && uvicorn app.main:app --reload --port 8004

# Terminal 5: Match Service
cd backend/match_service && uvicorn app.main:app --reload --port 8005

# Terminal 6: Outreach Service
cd backend/outreach_service && uvicorn app.main:app --reload --port 8006

# Terminal 7: Application Service
cd backend/application_service && uvicorn app.main:app --reload --port 8007

# Terminal 8: AI Orchestrator
cd backend/ai_orchestrator && uvicorn app.main:app --reload --port 8009

# Terminal 9: Tracking Service
cd backend/tracking_service && uvicorn app.main:app --reload --port 8010

# Terminal 10: Notification Service
cd backend/notification_service && uvicorn app.main:app --reload --port 8011
```

#### Option B: Run All via Docker

```bash
# Build and start all services
docker compose up -d --build

# Or start specific services only
docker compose up -d --build profile-api auth-api resume-api
```

### 4.6 Run Frontend

```bash
cd frontend
npm install     # Only needed first time
npm run dev     # Development server on :5173
```

**Frontend features available:**

| Page | Route | Description |
|------|-------|-------------|
| Login | `/login` | Email/password login |
| Register | `/register` | User registration |
| Dashboard | `/` | Stats, quick actions, activity feed |
| Profile | `/profile` | View full career profile |
| Profile Edit | `/profile/edit` | Edit personal info |
| Skills | `/profile/skills` | Skills manager |
| Jobs | `/jobs` | Search & filter jobs |
| Job Detail | `/jobs/:id` | Job details, apply button |
| Resumes | `/resumes` | Resume list with ATS scores |
| Resume Detail | `/resumes/:id` | Resume viewer, optimize |
| Resume Generate | `/resumes/generate` | Generate from template |
| Applications | `/applications` | Application list with status |
| Application Detail | `/applications/:id` | Timeline & package status |
| Tracking | `/tracking` | Stats cards, funnel, daily chart |
| Analytics | `/tracking/analytics` | Source breakdown, response rates |
| Notifications | `/tracking/notifications` | Read/unread notifications |

### 4.7 Seed Sample Data

```bash
python scripts/seed_data.py
```

**What gets created:**

| Data | Quantity | Details |
|------|----------|---------|
| **Profile** | 1 | Alex Johnson — Senior Full-Stack Engineer |
| **Skills** | 12 | Python, TypeScript, React, FastAPI, PostgreSQL, etc. |
| **Experience** | 3 | TechCorp (current), StartupXYZ, WebAgency Co. |
| **Education** | 1 | UC Berkeley, B.S. Computer Science |
| **Projects** | 2 | AI Career Platform, DevOps Dashboard |
| **Jobs** | 6 | Google, Stripe, Anthropic, Datadog, Figma, Netflix |
| **Resume** | 1 | Master Resume with ATS score 85 |
| **Applications** | 2 | 1 sent/delivered + 1 draft with event history |
| **Matches** | 6 | Match scores from 45% to 82.5% |
| **Tracking Stats** | 1 | 28 applications, 24 sent, 6 interviews, 2 offers |
| **Funnel** | 1 | Status distribution snapshot |
| **Daily Counts** | 30 | 30 days of activity data |
| **Outreach** | 1 | Cover letter for Google position |

The script is **idempotent** — running it multiple times won't create duplicates.

---

## 5. Full Stack Docker

Start everything at once:

```bash
# Copy config and start all services
cp .env.example .env
docker compose up -d --build
```

**All services:**

| Service | Container Name | Port | URL |
|---------|---------------|------|-----|
| **PostgreSQL** | career-postgres | 5432 | `postgresql://postgres:postgres@localhost:5432` |
| **PgBouncer** | career-pgbouncer | 5433 | `postgresql://postgres:postgres@localhost:5433` |
| **Redis** | career-redis | 6379 | `redis://localhost:6379` |
| **MinIO API** | career-minio | 9000 | `http://localhost:9000` |
| **MinIO Console** | career-minio | 9001 | `http://localhost:9001` |
| **Profile API** | career-profile-api | 8001 | `http://localhost/api/v1/profiles/` |
| **Auth API** | career-auth-api | 8002 | `http://localhost/api/v1/auth/` |
| **Resume API** | career-resume-api | 8003 | `http://localhost/api/v1/resumes/` |
| **Job API** | career-job-api | 8004 | `http://localhost/api/v1/jobs/` |
| **Match API** | career-match-api | 8005 | `http://localhost/api/v1/matches/` |
| **Outreach API** | career-outreach-api | 8006 | `http://localhost/api/v1/outreach/` |
| **Application API** | career-application-api | 8007 | `http://localhost/api/v1/applications/` |
| **AI Orchestrator** | career-ai-orchestrator | 8009 | `http://localhost/api/v1/ai/` |
| **Tracking API** | career-tracking-api | 8010 | `http://localhost/api/v1/tracking/` |
| **Notification API** | career-notification-api | 8011 | `http://localhost/api/v1/notifications/` |
| **Frontend** | career-frontend | 3000 → 80 | `http://localhost/` |
| **Nginx Gateway** | career-nginx | 80 | `http://localhost/` |
| **Prometheus** | career-prometheus | 9090 | `http://localhost:9090` |
| **Grafana** | career-grafana | 3001 | `http://localhost:3001` |
| **Loki** | career-loki | 3100 | `http://localhost:3100` |
| **OTEL Collector** | career-otel-collector | 4317/4318 | gRPC/HTTP |

**Useful Docker commands:**

```bash
# View logs for a specific service
docker compose logs -f profile-api

# View logs for all services
docker compose logs -f

# Restart a single service
docker compose restart profile-api

# Rebuild and restart a service
docker compose up -d --build profile-api

# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes data)
docker compose down -v

# Check resource usage
docker stats
```

---

## 6. Monitoring Stack

Start the monitoring services:

```bash
docker compose up -d prometheus grafana loki promtail otel-collector
```

### Access Monitoring

| Tool | URL | Credentials |
|------|-----|-------------|
| **Prometheus** | http://localhost:9090 | None |
| **Grafana** | http://localhost:3001 | admin / admin |
| **Loki** | http://localhost:3100/ready | None |

### What to Check

**Prometheus:**
1. Open http://localhost:9090/targets → All services should be UP
2. Try a query: `up` → Should show 1 for all services
3. Try: `rate(http_requests_total[5m])` → Request rate per service

**Grafana:**
1. Open http://localhost:3001 → Login (admin/admin)
2. Navigate to Dashboards → Browse
3. Open the 4 provisioned dashboards:
   - **Service Health** — Uptime, request rate, error rate, latency
   - **Queue Status** — Task queues depth and processing
   - **AI Usage** — Token usage and generation times
   - **Business KPIs** — Applications sent, matches found, interviews

### Alerts

Alert rules are pre-configured in `docker/prometheus/alert.rules.yml`:

| Alert | Condition | Severity |
|-------|-----------|----------|
| `ServiceDown` | Service down for >1min | Critical |
| `HighErrorRate` | 5xx > 5% for 5min | Warning |
| `HighLatency` | P95 > 2s for 5min | Warning |
| `DeliveryFailureRate` | Delivery failures > 10% | Warning |

---

## 7. Testing Everything

### Backend Tests

```bash
# Run all tests (run services separately to avoid conftest collisions)
cd backend

# Application Service (35 tests)
python -m pytest application_service/tests/ -v --tb=short

# Tracking Service (8 tests)
python -m pytest tracking_service/tests/ -v --tb=short

# Outreach Service (25 tests)
python -m pytest outreach_service/tests/ -v --tb=short

# Run with coverage
python -m pytest application_service/tests/ -v --cov=app --cov-report=term
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npx vitest run

# Run tests in watch mode
npx vitest

# TypeScript check
npx tsc --noEmit
```

### Frontend Build

```bash
cd frontend
npm run build    # Output in dist/
npx vite preview # Preview production build
```

### Full CI Pipeline

```bash
# Run everything
cd backend && python -m pytest application_service/tests/ -v --tb=short
cd backend && python -m pytest tracking_service/tests/ -v --tb=short
cd frontend && npx tsc --noEmit
cd frontend && npx vitest run
cd frontend && npm run build
```

---

## 8. API Endpoints Map

### Health & Metrics (all services)

```
GET  /api/v1/health      → {"status": "ok", "service": "..."}
GET  /metrics            → Prometheus metrics
```

### Auth Service (:8002)

```
POST /api/v1/auth/register       → Register user
POST /api/v1/auth/login          → Login, get JWT tokens
POST /api/v1/auth/refresh        → Refresh access token
POST /api/v1/auth/logout         → Invalidate refresh token
POST /api/v1/auth/change-password → Change password
```

### Profile Service (:8001)

```
GET    /api/v1/profiles/{id}              → Get full profile
POST   /api/v1/profiles                   → Create profile
PUT    /api/v1/profiles/{id}              → Update profile
GET    /api/v1/profiles/{id}/export       → Export as JSON
POST   /api/v1/profiles/{id}/import       → Import JSON
DELETE /api/v1/profiles/{id}              → Delete profile
```

### Resume Service (:8003)

```
GET    /api/v1/resumes                → List resumes
POST   /api/v1/resumes                → Create master resume
GET    /api/v1/resumes/{id}           → Get resume details
PUT    /api/v1/resumes/{id}           → Update resume
POST   /api/v1/resumes/{id}/generate  → Generate PDF
GET    /api/v1/resumes/{id}/download   → Download PDF
POST   /api/v1/resumes/{id}/optimize  → ATS optimize
```

### Job Service (:8004)

```
GET  /api/v1/jobs             → Search/filter jobs
GET  /api/v1/jobs/{id}        → Get job details
POST /api/v1/jobs/refresh     → Trigger scraping
```

### Match Service (:8005)

```
POST /api/v1/matches/score                  → Score profile+job
GET  /api/v1/matches/recommendations/{pid}  → Top-N matches
GET  /api/v1/matches/gaps/{pid}/{jid}       → Skill gap analysis
```

### Outreach Service (:8006)

```
POST /api/v1/outreach/cover-letter   → Generate cover letter
POST /api/v1/outreach/email          → Generate email
GET  /api/v1/outreach/templates      → List templates
PUT  /api/v1/outreach/content/{id}   → Edit content
```

### Application Service (:8007)

```
POST   /api/v1/applications                 → Create draft
GET    /api/v1/applications                 → List (with filters)
GET    /api/v1/applications/{id}            → Get with timeline
POST   /api/v1/applications/{id}/submit     → Submit
POST   /api/v1/applications/{id}/retry      → Retry delivery
PATCH  /api/v1/applications/{id}/status     → Update status
```

### AI Orchestrator (:8009)

```
POST /api/v1/ai/execute    → Execute AI task by agent name
GET  /api/v1/ai/agents     → List available agents
GET  /api/v1/ai/usage      → Token usage statistics
```

### Tracking Service (:8010)

```
GET  /api/v1/tracking/stats          → Aggregate stats
GET  /api/v1/tracking/analytics      → Detailed analytics
GET  /api/v1/tracking/funnel         → Status distribution
GET  /api/v1/tracking/trends         → Daily trends
POST /api/v1/tracking/export         → Export CSV/JSON
```

### Notification Service (:8011)

```
GET    /api/v1/notifications              → Get notifications
GET    /api/v1/notifications/unread/count → Unread count
POST   /api/v1/notifications/{id}/read    → Mark as read
POST   /api/v1/notifications/read-all     → Mark all read
WS     /ws/notifications/{user_id}        → Real-time stream
```

### Webhooks

```
POST /api/v1/webhooks/delivery    → Email delivery status
POST /api/v1/webhooks/gmail       → Gmail webhook (placeholder)
POST /api/v1/webhooks/outlook     → Outlook webhook (placeholder)
```

---

## 9. Common Tasks

### Database Operations

```bash
# Run migrations
cd backend && alembic upgrade head

# Create new migration (after model changes)
cd backend && alembic revision --autogenerate -m "description"

# Rollback last migration
cd backend && alembic downgrade -1

# Rollback to specific version
cd backend && alembic downgrade <revision_id>

# Check migration history
cd backend && alembic history

# Connect to database directly
docker compose exec postgres psql -U postgres -d career_platform

# List all tables
\dt career.*

# Describe a table
\d career.applications

# Run a query
SELECT status, COUNT(*) FROM career.applications GROUP BY status;
```

### Service Operations

```bash
# Check service health
curl http://localhost:8001/api/v1/health

# Check Prometheus metrics
curl http://localhost:8001/metrics

# View Swagger API docs (FastAPI auto-generated)
open http://localhost:8001/docs

# View ReDoc API docs
open http://localhost:8001/redoc
```

### Using the API (with Sample Data)

After running `python scripts/seed_data.py`:

```bash
# Get profile (id=1)
curl http://localhost:8001/api/v1/profiles/1 | python -m json.tool

# List jobs
curl "http://localhost:8004/api/v1/jobs?skills=Python,React" | python -m json.tool

# Get tracking stats
curl "http://localhost:8010/api/v1/tracking/stats?profile_id=1" | python -m json.tool

# Get application with timeline
curl "http://localhost:8007/api/v1/applications/1" | python -m json.tool

# Score a match
curl -X POST http://localhost:8005/api/v1/matches/score \
  -H "Content-Type: application/json" \
  -d '{"profile_id": 1, "job_id": 1}' | python -m json.tool
```

### Development Utilities

```bash
# Run all tests (via Makefile)
make test
make lint
make seed

# Start/stop infrastructure
make dev-up
make dev-down

# List all available Make commands
make help
```

---

## 10. Troubleshooting

### Database Connection Refused

```
Error: could not connect to server: Connection refused
```

**Fix:**
```bash
# Ensure PostgreSQL is running
docker compose ps postgres
docker compose logs postgres

# Wait for health check
docker compose up -d postgres --wait
```

### Migration Fails

```
ERROR [alembic.env] Can't locate revision identified by 'xxx'
```

**Fix:**
```bash
# Check current revision
cd backend && alembic current

# Reset migrations (WARNING: drops data)
cd backend && alembic downgrade base && alembic upgrade head
```

### ImportError: cannot import name 'X'

```
ImportError: cannot import name 'setup_metrics' from 'shared.middleware'
```

**Fix:**
```bash
# Reinstall shared package
pip install -e backend/shared/

# Or reinstall from scratch
pip uninstall career-platform-shared -y
pip install -e backend/shared/
```

### Docker Build Fails

```
ERROR: failed to solve: failed to compute cache key: ...
```

**Fix:**
```bash
# Clean build without cache
docker compose build --no-cache profile-api

# Or rebuild everything from scratch
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Port Already in Use

```
Error: address already in use (port 8001)
```

**Fix:**
```bash
# Find what's using the port
netstat -ano | findstr :8001    # Windows
lsof -i :8001                    # macOS/Linux

# Kill the process or use a different port
uvicorn app.main:app --reload --port 8001
```

### Frontend Can't Connect to API

```
Proxy error: Could not proxy request /api/v1/...
```

**Fix:**
```bash
# Ensure the backend service is running
curl http://localhost:8001/api/v1/health

# Check vite.config.ts proxy settings
# The dev server proxies /api to http://localhost:80 (Nginx)
# Make sure Nginx is running or the service is accessible
```

### Tests Fail with ImportPathMismatchError

```
_pytest.pathlib.ImportPathMismatchError
```

**Fix:** Run test suites separately:
```bash
# Instead of:
pytest backend/ -v

# Run individually:
cd backend && python -m pytest application_service/tests/ -v
cd backend && python -m pytest tracking_service/tests/ -v
cd backend && python -m pytest outreach_service/tests/ -v
```

### Seed Script Fails

```
sqlalchemy.exc.ProgrammingError: relation "career.applications" does not exist
```

**Fix:**
```bash
# Run migrations first
cd backend && alembic upgrade head

# Then seed
python scripts/seed_data.py
```

---

## Quick Reference

```bash
# ─── First Time Setup ────────────────────────────────────
cp .env.example .env
docker compose up -d postgres redis minio
pip install -e backend/shared/
pip install -r backend/requirements-shared.txt
cd backend && alembic upgrade head && cd ..
cd frontend && npm install && cd ..

# ─── Run Tests ───────────────────────────────────────────
cd backend && python -m pytest application_service/tests/ -v
cd frontend && npx tsc --noEmit && npx vitest run

# ─── Seed Data ───────────────────────────────────────────
python scripts/seed_data.py

# ─── Start Services (Development) ───────────────────────
cd backend/profile_service && uvicorn app.main:app --reload --port 8001
cd frontend && npm run dev

# ─── Start Services (Docker) ────────────────────────────
docker compose up -d --build

# ─── Monitoring ─────────────────────────────────────────
docker compose up -d prometheus grafana
open http://localhost:9090  # Prometheus
open http://localhost:3001  # Grafana (admin/admin)

# ─── Clean Up ───────────────────────────────────────────
docker compose down
```
