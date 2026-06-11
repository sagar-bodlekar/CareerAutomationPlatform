# AI Career Automation Platform

An intelligent, AI-powered career automation system that streamlines the entire job application lifecycle — from profile creation and resume generation to job discovery, matching, application delivery, and tracking.

> **License:** All components are free and open-source. No paid API dependencies.  
> **Status:** Early development (Phase 1: Foundation)

---

## Architecture Overview

```
Client Layer      → React Dashboard (Web App)
                         ↓
API Gateway       → Nginx / Traefik (Auth · Rate Limiting · Routing)
                         ↓
Service Layer     → Profile · Resume · Job · Match · Outreach · Application · Tracking · AI Orchestrator
                         ↓
AI Agent Layer    → Resume Optimizer · Job Match Engine · Outreach Agent · Career Intelligence
                         ↓
Data Layer        → PostgreSQL · Redis · MinIO · Celery (Queue)
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Node.js 20+ (for frontend, Phase 8+)
- Google Gemini API key (free from [Google AI Studio](https://aistudio.google.com/), Phase 6+)
- Groq API key (free from [Groq Console](https://console.groq.com/), optional fallback for AI)

### Setup

```bash
# 1. Clone and enter the repository
git clone <repo-url> && cd career-platform

# 2. Copy environment variables
cp .env.example .env

# 3. Start infrastructure services
docker compose up -d postgres redis minio

# 4. Install Python dependencies
pip install -e backend/shared/
pip install -r backend/requirements-shared.txt

# 5. Run database migrations
cd backend && alembic upgrade head && cd ..

# 6. Verify setup
make test
```

### Development

```bash
# Start all services
make dev-up

# Stop all services
make dev-down

# Run tests
make test

# Run linter
make lint
```

---

## Project Structure

```
career-platform/
├── backend/
│   ├── profile_service/       # User profile CRUD (SSOT)
│   ├── auth_service/          # Authentication & authorization
│   ├── resume_service/        # Resume generation & ATS optimization
│   ├── job_service/           # Job scraping & search
│   ├── match_service/         # Profile-job matching engine
│   ├── outreach_service/      # Cover letter & email generation
│   ├── application_service/   # Application pipeline & delivery
│   ├── tracking_service/      # Analytics & tracking dashboard
│   ├── ai_orchestrator/       # AI agent orchestration
│   ├── notification_service/  # User notifications
│   ├── shared/                # Shared libraries
│   └── service_template/      # Template for new services
├── frontend/                  # React dashboard (Phase 8)
├── docs/                      # Documentation
├── docker/                    # Docker configs
└── scripts/                   # Utility scripts
```

---

## Documentation

- [Architecture](docs/architecture.md)
- [Implementation Plan](docs/implementation-plan.md)
- [Problem Statement](docs/problemStatement.md)
- [Edge Cases](docs/edge-case.md)
- [Evaluation Criteria](docs/eval.md)

---

## License

All components are free and open-source:
- Backend: MIT / Apache 2.0 / PSF
- Frontend: MIT
- Infrastructure: Apache 2.0 / AGPLv3 / BSD
