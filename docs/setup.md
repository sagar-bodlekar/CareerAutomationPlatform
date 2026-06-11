# Setup Guide — AI Career Automation Platform

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Docker & Docker Compose | Latest | Infrastructure services |
| Python | 3.12+ | Backend microservices |
| Node.js | 20+ | Frontend dashboard (Phase 8+) |
| Google Gemini API Key | Free | AI features (resume, matching, outreach) |
| Groq API Key | Free | AI fallback provider |

## Quick Start

### 1. Clone and Configure

```bash
git clone <repo-url> && cd career-platform
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 2. Start Infrastructure

```bash
docker compose up -d postgres redis minio pgbouncer
```

This starts:
- **PostgreSQL 16** on port 5432
- **Redis 7** on port 6379
- **MinIO** on ports 9000 (API) and 9001 (Console)
- **PgBouncer** on port 5433 (connection pooling)

### 3. Install Backend Dependencies

```bash
pip install -e backend/shared/
pip install -r backend/requirements-shared.txt
```

### 4. Run Database Migrations

```bash
cd backend && alembic upgrade head && cd ..
```

### 5. Verify Setup

```bash
make test        # Run all backend tests
make seed        # Seed database with sample data
```

## Development Workflow

### Running Services Locally

```bash
# Start/stop infrastructure
make dev-up      # docker compose up -d postgres redis minio
make dev-down    # docker compose down

# Run a specific service
cd backend/profile_service && uvicorn app.main:app --reload --port 8001

# Run the frontend
cd frontend && npm run dev
```

### Running Tests

```bash
make test                          # All tests
pytest backend/profile_service/tests/  # Single service
pytest backend/ -v --cov=app       # With coverage
```

### Database

```bash
make migrate        # Run pending migrations
make migrate-new message="description"  # Create new migration
make migrate-rollback  # Rollback last migration

# Connect directly
psql -h localhost -U postgres -d career_platform
```

## Full Stack Run

To run the entire platform locally:

```bash
# Terminal 1: Infrastructure
docker compose up -d

# Terminal 2: All services (or use individual terminals)
cd backend/profile-api && uvicorn app.main:app --reload --port 8001
cd backend/auth-api && uvicorn app.main:app --reload --port 8002
# ... (repeat for each service)

# Terminal 3: Frontend
cd frontend && npm run dev
```

Access:
- **Frontend:** http://localhost:3000
- **API Gateway:** http://localhost/api/v1/
- **API Docs:** http://localhost/api/v1/docs (when available)
- **MinIO Console:** http://localhost:9001
- **Grafana:** http://localhost:3001 (admin/admin)
- **Prometheus:** http://localhost:9090

## Monitoring Stack (Phase 10)

Start the full monitoring stack:

```bash
docker compose up -d prometheus grafana loki promtail otel-collector
```

| Service | Port | Credentials |
|---------|------|-------------|
| Prometheus | 9090 | - |
| Grafana | 3001 | admin / admin |
| Loki | 3100 | - |
| OTEL Collector | 4317 (gRPC), 4318 (HTTP) | - |

## AI API Keys

### Google Gemini (Primary)

1. Visit https://aistudio.google.com/
2. Get free API key
3. Set `GEMINI_API_KEY` in `.env`

### Groq (Fallback)

1. Visit https://console.groq.com/
2. Get free API key
3. Set `GROQ_API_KEY` in `.env`

## Troubleshooting

### Database connection refused
```bash
# Ensure PostgreSQL is running
docker compose ps postgres
# Check logs
docker compose logs postgres
```

### MinIO connection issues
```bash
# Ensure MinIO is running and buckets exist
docker compose ps minio
docker compose logs minio-setup
```

### Alembic migration fails
```bash
# Check database connection
psql -h localhost -U postgres -d career_platform
# Reset migrations (caution: drops all data!)
cd backend && alembic downgrade base && alembic upgrade head
```

### Redis connection issues
```bash
docker compose ps redis
redis-cli -h localhost ping  # Should return PONG
```

### Prometheus targets not showing
Ensure all services are running and have the `/metrics` endpoint exposed.
Check Prometheus targets at http://localhost:9090/targets.

### Grafana dashboards empty
Ensure datasources are provisioned correctly:
```bash
docker compose exec grafana ls /etc/grafana/provisioning/datasources/
```
