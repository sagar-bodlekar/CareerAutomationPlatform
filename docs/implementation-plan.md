# Implementation Plan — AI Career Automation Platform

> **Version:** 1.0  
> **Status:** Active  
> **Last Updated:** June 11, 2026  
> **Total Phases:** 10  
> **Estimated Timeline:** 12–16 weeks (full-time solo dev)

---

## Table of Contents

1. [How to Use This Plan](#1-how-to-use-this-plan)
2. [Development Principles](#2-development-principles)
3. [Phase Overview](#3-phase-overview)
4. [Phase 1: Foundation & Infrastructure](#4-phase-1-foundation--infrastructure)
5. [Phase 2: Profile Service](#5-phase-2-profile-service)
6. [Phase 3: Auth Service](#6-phase-3-auth-service)
7. [Phase 4: Resume Service](#7-phase-4-resume-service)
8. [Phase 5: Job Service](#8-phase-5-job-service)
9. [Phase 6: AI Orchestrator & Matching](#9-phase-6-ai-orchestrator--matching)
10. [Phase 7: Outreach & Application Pipeline](#10-phase-7-outreach--application-pipeline)
11. [Phase 8: Frontend Dashboard](#11-phase-8-frontend-dashboard)
12. [Phase 9: Email Delivery & Tracking](#12-phase-9-email-delivery--tracking)
13. [Phase 10: Polish & Scale](#13-phase-10-polish--scale)
14. [Future Phases](#14-future-phases)
15. [Appendix: Quick-Reference Command Cheatsheet](#15-appendix-quick-reference-command-cheatsheet)

---

## 1. How to Use This Plan

Each phase contains:

| Section | Description |
|---------|-------------|
| **Goal** | What the phase achieves when complete |
| **Services Involved** | Which microservices are created/modified |
| **Dependencies** | What must be done before this phase |
| **Sprints** | 1–3 sprints per phase, each with concrete file creation tasks |
| **File Manifest** | Every file that needs to be created |
| **Verification** | How to confirm the phase works correctly |
| **Estimated Time** | Solo dev hours |

**Workflow:** Complete sprints in order within each phase. Each sprint ends with a working, testable increment. Run verification steps before moving to the next sprint.

---

## 2. Development Principles

1. **Infrastructure first, features second.** Get Docker Compose, databases, and CI running before writing business logic.
2. **Start with the profile.** The user profile (SSOT) is foundational — everything depends on it.
3. **Build services in dependency order.** Profile → Auth → Resume → Job → Match → Outreach → Application → Tracking.
4. **Test at every sprint.** Each sprint includes automated tests + manual verification.
5. **AI last.** The AI Orchestrator depends on Resume and Match services — build the data pipelines first, add AI intelligence on top.
6. **Frontend after backend.** Build all backend APIs first, then connect the React dashboard in Phase 8.

---

## 3. Phase Overview

| Phase | Name | Weeks | Services Built | Dependencies |
|-------|------|-------|---------------|--------------|
| **P1** | Foundation & Infrastructure | 1 | None (Docker, CI, monorepo) | None |
| **P2** | Profile Service | 1.5 | Profile Service | P1 |
| **P3** | Auth Service | 1 | Auth Service | P1 |
| **P4** | Resume Service | 2 | Resume Service | P2, P3 |
| **P5** | Job Service | 2 | Job Service | P1 |
| **P6** | AI Orchestrator & Matching | 2.5 | AI Orchestrator, Match Service | P2, P4, P5 |
| **P7** | Outreach & Application Pipeline | 2 | Outreach Service, Application Service | P2, P4, P6 |
| **P8** | Frontend Dashboard | 2.5 | React Dashboard (all pages) | P2–P7 |
| **P9** | Email Delivery & Tracking | 1.5 | Delivery, Tracking, Notification | P7, P8 |
| **P10** | Polish & Scale | 1 | Monitoring, perf, docs | All |

**Total: ~15 weeks full-time.**

---

## 4. Phase 1: Foundation & Infrastructure

**Goal:** Monorepo scaffold, Docker Compose with all infrastructure services, CI pipeline, shared libraries.

**Services Involved:** None (infrastructure only)

**Dependencies:** None

---

### Sprint 1.1: Monorepo Scaffold

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Create root directory structure per `docs/architecture.md` Section 10
- [ ] Create root `.gitignore` (Python `__pycache__`, `.env`, `node_modules`, `*.pyc`, `.DS_Store`, MinIO data dirs)
- [ ] Create `README.md` with project overview, quick-start, and links to docs
- [ ] Create `.env.example` with all required environment variables (database URLs, Redis URL, JWT secret, MinIO credentials)
- [ ] Create `Makefile` at root with targets: `help`, `install`, `dev-up`, `dev-down`, `test`, `lint`, `migrate`, `seed`
- [ ] Create `.github/workflows/ci.yml` for Python CI (lint, type-check, test)
- [ ] Create `.github/workflows/deploy.yml` as placeholder

**Files to create:**
```
.gitignore
README.md
.env.example
Makefile
.github/workflows/ci.yml
.github/workflows/deploy.yml
.github/CODEOWNERS
```

---

### Sprint 1.2: Docker Compose — Infrastructure

**Estimated Time:** 8 hours

**Tasks:**

- [ ] Create `docker-compose.yml` with infrastructure services:
  - `postgres` (PostgreSQL 16, port 5432, volume for data persistence)
  - `redis` (Redis 7, port 6379)
  - `minio` (MinIO, ports 9000 (API) + 9001 (Console), volumes for data)
  - *(No AI services in Docker — AI uses Gemini API (primary) + Groq API (fallback))*
  - `pgbouncer` (PgBouncer, port 5432, linked to postgres)
  - `nginx` (Nginx, port 80, reverse proxy config)
- [ ] Create `docker/nginx/nginx.conf` with API gateway routing rules
- [ ] Create `docker/postgres/init.sql` with initial database creation
- [ ] *(No local AI setup needed — Gemini API used in Phase 6)*
- [ ] Verify: `docker compose up postgres redis minio -d` launches without errors
- [ ] Verify: Can connect to PostgreSQL via `psql`
- [ ] Verify: Can access MinIO console at `http://localhost:9001`
- [ ] Verify: Can connect to Redis via `redis-cli ping`

**Files to create:**
```
docker-compose.yml
docker/nginx/nginx.conf
docker/postgres/init.sql
```

---

### Sprint 1.3: Shared Libraries & Service Template

**Estimated Time:** 6 hours

**Tasks:**

- [ ] Create `backend/shared/` as a proper installable Python package:
  - `backend/shared/pyproject.toml` — package metadata and build config
  - `backend/shared/__init__.py`
  - `backend/shared/config/` — Pydantic `BaseSettings` classes
  - `backend/shared/database.py` — SQLAlchemy async engine + session factory
  - `backend/shared/logging.py` — JSON structured logging setup (structlog)
  - `backend/shared/schemas/` — Common Pydantic response schemas (`APIResponse`, `PaginatedResponse`, `ErrorResponse`)
  - `backend/shared/utils/` — `datetime_utils.py`, `encryption.py` (AES-256 helpers)
- [ ] Install shared package in development mode: `pip install -e backend/shared/`
- [ ] Each service's `requirements.txt` includes: `-e ../shared` for editable install
- [ ] Create `backend/scripts/create_service.sh` — script to scaffold a new microservice from template
- [ ] Create service template directory: `backend/service_template/` with full internal structure (see Section 10.1 of Architecture)
- [ ] Create `backend/pyproject.toml` at root for unified monorepo config (tool configs: Black, Ruff, mypy, pytest)
- [ ] Create `backend/requirements-shared.txt` with shared dependencies:
  ```
  fastapi>=0.115.0
  pydantic>=2.0
  pydantic-settings>=2.0
  sqlalchemy[asyncio]>=2.0
  alembic>=1.13
  asyncpg>=0.29
  redis[hiredis]>=5.0
  structlog>=24.0
  httpx>=0.27
  python-jose[cryptography]>=3.3
  passlib[bcrypt]>=1.7
  cryptography>=41.0
  ```

**Files to create:**
```
backend/shared/__init__.py
backend/shared/config.py
backend/shared/database.py
backend/shared/logging.py
backend/shared/schemas/__init__.py
backend/shared/schemas/common.py
backend/shared/schemas/pagination.py
backend/shared/utils/__init__.py
backend/shared/utils/datetime_utils.py
backend/shared/utils/encryption.py
backend/requirements-shared.txt
backend/service_template/app/__init__.py
backend/service_template/app/main.py
backend/service_template/app/api/__init__.py
backend/service_template/app/api/router.py
backend/service_template/app/api/v1/__init__.py
backend/service_template/app/api/v1/endpoints.py
backend/service_template/app/api/v1/dependencies.py
backend/service_template/app/core/__init__.py
backend/service_template/app/core/config.py
backend/service_template/app/core/database.py
backend/service_template/app/models/__init__.py
backend/service_template/app/models/models.py
backend/service_template/app/schemas/__init__.py
backend/service_template/app/schemas/request.py
backend/service_template/app/schemas/response.py
backend/service_template/app/services/__init__.py
backend/service_template/app/services/service.py
backend/service_template/tests/__init__.py
backend/service_template/tests/conftest.py
backend/service_template/tests/test_api.py
backend/service_template/tests/test_services.py
backend/service_template/Dockerfile
backend/service_template/requirements.txt
backend/scripts/create_service.sh
```

---

### Sprint 1.4: Database Migrations Setup

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Create root `backend/alembic.ini` with migration configuration
- [ ] Create `backend/alembic/` directory with:
  - `env.py` — async Alembic environment
  - `script.py.mako` — migration template
- [ ] Create initial migration via `alembic revision --autogenerate -m "init"`
- [ ] Create `scripts/migrate.sh` — migration runner script
- [ ] Create `scripts/seed_data.py` — seed script for development data
- [ ] Verify: `alembic upgrade head` runs without errors against local PostgreSQL

**Files to create:**
```
backend/alembic.ini
backend/alembic/env.py
backend/alembic/script.py.mako
backend/alembic/versions/.gitkeep
scripts/migrate.sh
scripts/seed_data.py
```

---

### Phase 1 Verification Checklist

- [ ] `docker compose up -d postgres redis minio` starts all services
- [ ] `psql -h localhost -U postgres -d career_platform` connects successfully
- [ ] `redis-cli -h localhost ping` responds with `PONG`
- [ ] MinIO console accessible at `http://localhost:9001`
- [ ] `pip install -r backend/requirements-shared.txt` installs all dependencies
- [ ] `alembic upgrade head` runs cleanly
- [ ] `make test` runs the test suite (initially empty, passes)
- [ ] CI pipeline passes on GitHub (or local `act`)

---

## 5. Phase 2: Profile Service

**Goal:** Fully functional Profile Service with CRUD APIs for the user's career profile (SSOT).

**Services Involved:** Profile Service

**Dependencies:** Phase 1

---

### Sprint 2.1: Database Models & Migrations

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Create `backend/profile_service/` from service template
- [ ] Implement SQLAlchemy models for all profile tables:
  - `UserProfile` → `user_profiles` table
  - `PersonalInfo` → `personal_info` table
  - `Skill` → `skills` table
  - `WorkExperience` → `work_experiences` table
  - `Education` → `education` table
  - `Project` → `projects` table
  - `Certification` → `certifications` table
  - `SocialLink` → `social_links` table
- [ ] Create Alembic migrations for profile schema
- [ ] Create `seed_data.py` entry for sample profile

**Files to create/modify:**
```
backend/profile_service/app/models/__init__.py
backend/profile_service/app/models/models.py   (all profile tables)
backend/profile_service/app/models/enums.py    (SkillProficiency, LocationType, etc.)
backend/profile_service/alembic/versions/001_create_profile_tables.py
```

---

### Sprint 2.2: Pydantic Schemas

**Estimated Time:** 3 hours

**Tasks:**

- [ ] Create request schemas:
  - `ProfileCreate`, `ProfileUpdate`
  - `PersonalInfoCreate`, `PersonalInfoUpdate`
  - `SkillCreate`, `SkillUpdate`
  - `WorkExperienceCreate`, `WorkExperienceUpdate`
  - `EducationCreate`, `EducationUpdate`
  - `ProjectCreate`, `ProjectUpdate`
  - `CertificationCreate`, `CertificationUpdate`
  - `SocialLinkCreate`, `SocialLinkUpdate`
- [ ] Create response schemas:
  - `ProfileResponse` (full profile with nested personal_info, skills, etc.)
  - `ProfileSummary` (lightweight version for list views)
- [ ] Create query parameter schemas for filtering/search

**Files to create:**
```
backend/profile_service/app/schemas/__init__.py
backend/profile_service/app/schemas/profile.py
backend/profile_service/app/schemas/personal_info.py
backend/profile_service/app/schemas/skill.py
backend/profile_service/app/schemas/experience.py
backend/profile_service/app/schemas/education.py
backend/profile_service/app/schemas/project.py
backend/profile_service/app/schemas/certification.py
backend/profile_service/app/schemas/social_link.py
```

---

### Sprint 2.3: Business Logic & API Endpoints

**Estimated Time:** 6 hours

**Tasks:**

- [ ] Implement service layer:
  - `ProfileService` — CRUD, profile versioning
  - `SkillService` — bulk add/update, category management
  - `ExperienceService` — timeline ordering
  - `ImportService` — JSON import/export
- [ ] Implement API endpoints per Section 4.1 of Architecture
- [ ] Add profile export endpoint (`/api/v1/profiles/{id}/export`) — returns full profile as JSON
- [ ] Add profile import endpoint (`/api/v1/profiles/{id}/import`) — accepts JSON, merges/overwrites
- [ ] Add profile analytics endpoint (`/api/v1/profiles/{id}/analytics`) — returns skill coverage, experience summary
- [ ] Wire up dependencies (DB session, auth dependency placeholder)

**Files to create:**
```
backend/profile_service/app/services/__init__.py
backend/profile_service/app/services/profile_service.py
backend/profile_service/app/services/skill_service.py
backend/profile_service/app/services/experience_service.py
backend/profile_service/app/services/import_service.py
backend/profile_service/app/api/v1/endpoints.py      (all profile CRUD endpoints)
backend/profile_service/app/api/v1/dependencies.py    (get_profile_service, etc.)
backend/profile_service/app/api/router.py             (route aggregation)
backend/profile_service/app/main.py                   (FastAPI app factory)
backend/profile_service/app/core/__init__.py
backend/profile_service/app/core/config.py
backend/profile_service/app/core/database.py
```

---

### Sprint 2.4: Tests & Integration

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Write unit tests for profile service business logic
- [ ] Write API integration tests using TestClient
- [ ] Create Dockerfile for profile service
- [ ] Add profile service to root docker-compose.yml
- [ ] Add Celery task stubs for `profile.created` event

**Files to create:**
```
backend/profile_service/tests/__init__.py
backend/profile_service/tests/conftest.py
backend/profile_service/tests/test_models.py
backend/profile_service/tests/test_services.py
backend/profile_service/tests/test_api.py
backend/profile_service/tests/test_integration.py
backend/profile_service/Dockerfile
backend/profile_service/requirements.txt
```

---

### Phase 2 Verification Checklist

- [ ] `POST /api/v1/profiles` creates a profile and returns 201
- [ ] `GET /api/v1/profiles/{id}` returns full profile with nested data
- [ ] `PUT /api/v1/profiles/{id}` updates profile fields
- [ ] `POST /api/v1/profiles/{id}/skills` adds skills in bulk
- [ ] `GET /api/v1/profiles/{id}/export` returns JSON export
- [ ] `POST /api/v1/profiles/{id}/import` imports JSON successfully
- [ ] All endpoints return proper error responses for invalid data
- [ ] `pytest tests/ -v` passes with >80% coverage
- [ ] `docker compose up -d profile-api` starts and responds on `/health`

---

## 6. Phase 3: Auth Service

**Goal:** Complete authentication system with registration, login, JWT management, and OAuth2 flows.

**Services Involved:** Auth Service

**Dependencies:** Phase 1

---

### Sprint 3.1: Auth Models & Core Logic

**Estimated Time:** 5 hours

**Tasks:**

- [ ] Create `backend/auth_service/` from service template
- [ ] Implement models:
  - `AuthUser` → `auth_users`
  - `OAuthConnection` → `auth_oauth_connections`
  - `ApiKey` → `auth_api_keys`
- [ ] Implement auth core logic:
  - Password hashing (bcrypt via passlib)
  - JWT creation & validation (access + refresh tokens)
  - Token blacklisting via Redis
- [ ] Implement middleware for JWT validation (for use by API Gateway)

**Files to create:**
```
backend/auth_service/app/models/__init__.py
backend/auth_service/app/models/models.py
backend/auth_service/app/core/__init__.py
backend/auth_service/app/core/config.py
backend/auth_service/app/core/database.py
backend/auth_service/app/core/security.py           (password hashing, JWT)
backend/auth_service/app/core/tokens.py             (access + refresh token logic)
backend/auth_service/app/middleware/__init__.py
backend/auth_service/app/middleware/jwt_middleware.py
backend/auth_service/alembic/versions/001_create_auth_tables.py
```

---

### Sprint 3.2: Auth API Endpoints

**Estimated Time:** 5 hours

**Tasks:**

- [ ] Implement endpoints:
  - `POST /api/v1/auth/register` — user registration with email verification
  - `POST /api/v1/auth/login` — login, returns JWT pair
  - `POST /api/v1/auth/refresh` — refresh token rotation
  - `POST /api/v1/auth/logout` — invalidate refresh token
  - `POST /api/v1/auth/change-password` — password change
  - `POST /api/v1/auth/forgot-password` — password reset flow
  - `POST /api/v1/auth/oauth/{provider}` — initiate OAuth2 flow
  - `GET /api/v1/auth/oauth/{provider}/callback` — OAuth2 callback
- [ ] Implement email verification (send verification link)
- [ ] Implement API key management for service-to-service auth

**Files to create:**
```
backend/auth_service/app/schemas/__init__.py
backend/auth_service/app/schemas/auth.py            (login, register, token schemas)
backend/auth_service/app/services/__init__.py
backend/auth_service/app/services/auth_service.py
backend/auth_service/app/services/oauth_service.py
backend/auth_service/app/services/api_key_service.py
backend/auth_service/app/api/v1/endpoints.py
backend/auth_service/app/api/v1/dependencies.py
backend/auth_service/app/api/router.py
backend/auth_service/app/main.py
```

---

### Sprint 3.3: Tests & Integration

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Write tests for registration, login, token refresh
- [ ] Write tests for password hashing and JWT validation
- [ ] Write integration test for full auth flow
- [ ] Create Dockerfile for auth service
- [ ] Add auth service to docker-compose.yml
- [ ] Update API Gateway config with auth routes

**Files to create:**
```
backend/auth_service/tests/__init__.py
backend/auth_service/tests/conftest.py
backend/auth_service/tests/test_auth.py
backend/auth_service/tests/test_tokens.py
backend/auth_service/tests/test_api.py
backend/auth_service/Dockerfile
backend/auth_service/requirements.txt
```

---

### Phase 3 Verification Checklist

- [ ] `POST /api/v1/auth/register` creates user and returns tokens
- [ ] `POST /api/v1/auth/login` authenticates and returns JWT pair
- [ ] `POST /api/v1/auth/refresh` returns new access token
- [ ] Expired/invalid tokens return 401
- [ ] Duplicate email registration returns 409
- [ ] OAuth2 flow initiates and completes
- [ ] `pytest tests/ -v` passes
- [ ] Auth middleware correctly validates tokens on protected routes

---

## 7. Phase 4: Resume Service

**Goal:** Resume generation, PDF export, template management, ATS optimization foundation.

**Services Involved:** Resume Service

**Dependencies:** Phase 2 (Profile Service), Phase 3 (Auth Service)

---

### Sprint 4.1: Resume Models & Schemas

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Create `backend/resume_service/` from service template
- [ ] Implement models:
  - `Resume` → `resumes` table
  - `ResumeFile` → `resume_files` table (PDF metadata)
  - `ResumeTemplate` → `resume_templates` table
- [ ] Implement Pydantic schemas:
  - `ResumeCreate`, `ResumeUpdate` — with structured JSONB content
  - `ResumeResponse` — full resume with sections
  - `ResumeTemplateCreate`, `ResumeTemplateResponse`
  - `ResumeGenerationRequest` — target role, job ID, optimization flags
- [ ] Create Alembic migrations

**Files to create:**
```
backend/resume_service/app/models/__init__.py
backend/resume_service/app/models/models.py
backend/resume_service/app/schemas/__init__.py
backend/resume_service/app/schemas/resume.py
backend/resume_service/app/schemas/template.py
backend/resume_service/app/schemas/generation.py
backend/resume_service/alembic/versions/001_create_resume_tables.py
```

---

### Sprint 4.2: PDF Generation Engine

**Estimated Time:** 6 hours

**Tasks:**

- [ ] Research and choose PDF generation library (WeasyPrint or ReportLab — both open-source)
- [ ] Install WeasyPrint (CSS-based PDF generation from HTML templates)
- [ ] Create HTML/CSS resume templates in `app/templates/resumes/`:
  - `master.html` — full master resume template
  - `modern.html` — modern clean layout
  - `classic.html` — traditional layout
  - `minimal.html` — minimal ATS-friendly layout
- [ ] Implement `PDFGenerator` service:
  - Renders Jinja2 HTML template with resume data
  - Converts to PDF via WeasyPrint
  - Uploads PDF to MinIO
  - Creates `ResumeFile` record
- [ ] Implement resume content assembler (converts profile data → structured resume JSON)
- [ ] Create template management endpoints

**Files to create:**
```
backend/resume_service/app/templates/__init__.py
backend/resume_service/app/templates/resumes/base.html
backend/resume_service/app/templates/resumes/master.html
backend/resume_service/app/templates/resumes/modern.html
backend/resume_service/app/templates/resumes/classic.html
backend/resume_service/app/templates/resumes/minimal.html
backend/resume_service/app/services/__init__.py
backend/resume_service/app/services/resume_service.py
backend/resume_service/app/services/pdf_generator.py
backend/resume_service/app/services/template_service.py
backend/resume_service/app/services/content_assembler.py
```

---

### Sprint 4.3: Resume API Endpoints

**Estimated Time:** 5 hours

**Tasks:**

- [ ] Implement endpoints:
  - `POST /api/v1/resumes` — create master resume from profile
  - `POST /api/v1/resumes/{id}/generate` — generate role-specific resume PDF
  - `GET /api/v1/resumes/{id}` — get resume metadata
  - `GET /api/v1/resumes/{id}/download` — download PDF (redirects to MinIO presigned URL)
  - `PUT /api/v1/resumes/{id}` — update resume content
  - `DELETE /api/v1/resumes/{id}` — soft delete resume
  - `POST /api/v1/resumes/{id}/optimize` — trigger ATS optimization (stub, will connect in P6)
  - `GET /api/v1/resumes` — list resumes with filters
- [ ] Connect to Profile Service for profile data
- [ ] Wire MinIO storage for PDF files
- [ ] Add Celery task `generate_resume` for async PDF generation

**Files to create:**
```
backend/resume_service/app/api/v1/endpoints.py
backend/resume_service/app/api/v1/dependencies.py
backend/resume_service/app/api/router.py
backend/resume_service/app/main.py
backend/resume_service/app/core/__init__.py
backend/resume_service/app/core/config.py
backend/resume_service/app/core/database.py
backend/resume_service/app/core/storage.py          (MinIO client wrapper)
backend/resume_service/app/tasks.py                 (Celery tasks)
```

---

### Sprint 4.4: ATS Optimization Service

**Estimated Time:** 5 hours

**Tasks:**

- [ ] Implement ATS analysis engine in Resume Service:
  - `ATSAnalyzer` — parses job description, extracts key requirements
  - `KeywordExtractor` — identifies important keywords/skills from job description
  - `ATSScorer` — scores resume compatibility with job (keyword density, section alignment, formatting)
  - `ATSRecommendationEngine` — generates suggestions to improve ATS score
- [ ] Implement ATS optimization logic:
  - Reorder experience sections to highlight relevant roles
  - Add missing keywords naturally into bullet points
  - Optimize section headers for ATS parsing
  - Remove irrelevant content that dilutes match score
- [ ] Wire `POST /api/v1/resumes/{id}/optimize` to ATS engine
- [ ] Add `ats_score` computation and return with score breakdown
- [ ] Connect ATS optimizer to AI Orchestrator for AI-enhanced keyword analysis
- [ ] Add Celery task: `optimize_resume_ats`

**Files to create:**
```
backend/resume_service/app/services/ats/__init__.py
backend/resume_service/app/services/ats/analyzer.py
backend/resume_service/app/services/ats/keyword_extractor.py
backend/resume_service/app/services/ats/scorer.py
backend/resume_service/app/services/ats/recommendation_engine.py
backend/resume_service/app/services/ats/optimizer.py
backend/resume_service/app/services/ats/ai_integrator.py
backend/resume_service/app/schemas/ats.py
backend/resume_service/app/tasks_ats.py
```

---

### Sprint 4.5: Tests & Integration

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Write tests for resume creation from profile
- [ ] Write tests for PDF generation (verify PDF output is valid)
- [ ] Write tests for ATS analysis and optimization
- [ ] Write tests for resume CRUD
- [ ] Write integration test: create profile → create master resume → generate PDF → ATS optimize
- [ ] Create Dockerfile
- [ ] Add to docker-compose.yml

**Files to create:**
```
backend/resume_service/tests/__init__.py
backend/resume_service/tests/conftest.py
backend/resume_service/tests/test_resume_service.py
backend/resume_service/tests/test_pdf_generation.py
backend/resume_service/tests/test_ats_optimizer.py
backend/resume_service/tests/test_api.py
backend/resume_service/Dockerfile
backend/resume_service/requirements.txt
```

---

### Phase 4 Verification Checklist

- [ ] `POST /api/v1/resumes` creates master resume from profile data
- [ ] `POST /api/v1/resumes/{id}/generate` generates PDF, stores in MinIO
- [ ] `POST /api/v1/resumes/{id}/optimize` returns ATS score with recommendations
- [ ] `GET /api/v1/resumes/{id}/download` returns PDF file
- [ ] PDF renders correctly (open in browser/PDF viewer)
- [ ] Multiple resume templates render correctly
- [ ] ATS score improves after optimization (before vs after comparison)
- [ ] `pytest tests/ -v` passes
- [ ] MinIO bucket `resumes` has uploaded PDFs

- [ ] `POST /api/v1/resumes` creates master resume from profile data
- [ ] `POST /api/v1/resumes/{id}/generate` generates PDF, stores in MinIO
- [ ] `GET /api/v1/resumes/{id}/download` returns PDF file
- [ ] PDF renders correctly (open in browser/PDF viewer)
- [ ] Multiple resume templates render correctly
- [ ] `pytest tests/ -v` passes
- [ ] MinIO bucket `resumes` has uploaded PDFs

---

## 8. Phase 5: Job Service

**Goal:** Job scraping engine that discovers, normalizes, and stores jobs from multiple sources.

**Services Involved:** Job Service

**Dependencies:** Phase 1

---

### Sprint 5.1: Job Models & Storage

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Create `backend/job_service/` from service template
- [ ] Implement models:
  - `Job` → `jobs` table (see Architecture Section 5.3)
  - `JobSource` → `job_sources` table
- [ ] Create GIN index on `required_skills` for efficient skill matching
- [ ] Create Pydantic schemas:
  - `JobResponse`, `JobListResponse`
  - `JobCreate`, `JobUpdate`
  - `JobSourceCreate`, `JobSourceResponse`
  - `JobFilterParams` — role, skills, location, experience, salary range
- [ ] Create Alembic migrations

**Files to create:**
```
backend/job_service/app/models/__init__.py
backend/job_service/app/models/models.py
backend/job_service/app/schemas/__init__.py
backend/job_service/app/schemas/job.py
backend/job_service/app/schemas/source.py
backend/job_service/app/schemas/filters.py
backend/job_service/alembic/versions/001_create_job_tables.py
```

---

### Sprint 5.2: Scraper Framework

**Estimated Time:** 8 hours

**Tasks:**

- [ ] Implement abstract `JobScraper` base class:
  - `fetch()` — retrieve raw data from source
  - `parse()` — convert raw data to normalized Job schema
  - `deduplicate()` — check against existing jobs
  - `upsert()` — insert or update in database
- [ ] Implement scrapers:
  - `NaukriScraper` — scrapes naukri.com
  - `WellfoundScraper` — scrapes wellfound.com (AngelList)
  - `RemoteOKScraper` — scrapes remoteok.com
  - `LinkedInScraper` — LinkedIn job search (via public API or scraping)
  - `GenericCareerPageScraper` — configurable company career page scraper
- [ ] Implement `JobNormalizer` — maps varied source schemas to unified `Job` schema
- [ ] Implement `DeduplicationService` — Redis-backed dedup using job URL hash
- [ ] Implement scraper error handling + retry logic

**Files to create:**
```
backend/job_service/app/scrapers/__init__.py
backend/job_service/app/scrapers/base.py
backend/job_service/app/scrapers/naukri.py
backend/job_service/app/scrapers/wellfound.py
backend/job_service/app/scrapers/remoteok.py
backend/job_service/app/scrapers/linkedin.py
backend/job_service/app/scrapers/generic.py
backend/job_service/app/services/__init__.py
backend/job_service/app/services/job_service.py
backend/job_service/app/services/scraper_service.py
backend/job_service/app/services/normalizer.py
backend/job_service/app/services/dedup_service.py
```

---

### Sprint 5.3: Job API + Scheduled Scraping

**Estimated Time:** 5 hours

**Tasks:**

- [ ] Implement endpoints:
  - `GET /api/v1/jobs` — list/search/filter jobs
  - `GET /api/v1/jobs/{id}` — get job details
  - `POST /api/v1/jobs/refresh` — trigger immediate scrape
  - `GET /api/v1/jobs/sources` — list configured sources & status
  - `PUT /api/v1/jobs/sources/{id}` — update source configuration
  - `POST /api/v1/jobs/sources/{id}/test` — test scraper connection
- [ ] Implement Celery tasks for scheduled scraping:
  - `scrape_jobs(source_name)` — scrape single source
  - `refresh_all_sources()` — iterate all active sources
- [ ] Configure Celery Beat schedule per Section 7.3 of Architecture
- [ ] Add scraping endpoints for immediate manual trigger

**Files to create:**
```
backend/job_service/app/api/v1/endpoints.py
backend/job_service/app/api/v1/dependencies.py
backend/job_service/app/api/router.py
backend/job_service/app/main.py
backend/job_service/app/core/__init__.py
backend/job_service/app/core/config.py
backend/job_service/app/core/database.py
backend/job_service/app/tasks.py
backend/job_service/app/tasks_scrape.py
```

---

### Sprint 5.4: Tests & Integration

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Write unit tests for scrapers with mock HTTP responses
- [ ] Write tests for job deduplication
- [ ] Write tests for job API (CRUD, search, filtering)
- [ ] Write integration test: scrape single source → verify jobs in DB
- [ ] Create Dockerfile
- [ ] Add to docker-compose.yml (with Celery worker and beat)

**Files to create:**
```
backend/job_service/tests/__init__.py
backend/job_service/tests/conftest.py
backend/job_service/tests/test_scrapers.py
backend/job_service/tests/test_dedup.py
backend/job_service/tests/test_api.py
backend/job_service/tests/test_integration.py
backend/job_service/Dockerfile
backend/job_service/requirements.txt
```

---

### Phase 5 Verification Checklist

- [ ] `GET /api/v1/jobs` returns paginated jobs
- [ ] `GET /api/v1/jobs?skills=Python,React` filters correctly
- [ ] `POST /api/v1/jobs/refresh` triggers scraping, jobs appear in DB
- [ ] Duplicate jobs from same source are correctly detected
- [ ] Celery Beat triggers scheduled scraping
- [ ] `pytest tests/ -v` passes
- [ ] At least one real source (RemoteOK) scrapes successfully

---

## 9. Phase 6: AI Orchestrator & Matching

**Goal:** AI orchestration layer, job matching engine, resume optimization agent.

**Services Involved:** AI Orchestrator Service, Match Service

**Dependencies:** Phase 2 (Profile), Phase 4 (Resume), Phase 5 (Job), Gemini + Groq API keys

---

### Sprint 6.1: AI Orchestrator Core

**Estimated Time:** 6 hours

**Tasks:**

- [ ] Create `backend/ai_orchestrator/` from service template
- [ ] Implement LLM provider:
  - `LLMProvider` (abstract base)
  - `GeminiProvider` — connects to Google Gemini API via `google-genai` SDK
  - `GroqProvider` — connects to Groq API via OpenAI-compatible `openai` SDK (fallback)
- [ ] Implement prompt template engine:
  - Load Jinja2 templates from `app/prompts/`
  - Inject variables (profile data, job description, company info)
  - Context window management (trim when over token limit)
- [ ] Implement structured output parser:
  - Call LLM with system prompt asking for JSON response
  - Validate response against Pydantic schema
  - Retry on parse failure (up to 2 retries)
- [ ] Implement execution logging (`ai_execution_logs` table)
- [ ] Implement retry logic and provider fallback chain (Gemini → Groq → error gracefully)

**Files to create:**
```
backend/ai_orchestrator/app/providers/__init__.py
backend/ai_orchestrator/app/providers/base.py
backend/ai_orchestrator/app/providers/gemini.py
backend/ai_orchestrator/app/providers/groq.py
backend/ai_orchestrator/app/services/__init__.py
backend/ai_orchestrator/app/services/orchestrator.py
backend/ai_orchestrator/app/services/prompt_engine.py
backend/ai_orchestrator/app/services/response_parser.py
backend/ai_orchestrator/app/schemas/__init__.py
backend/ai_orchestrator/app/schemas/agents.py
backend/ai_orchestrator/app/schemas/responses.py
backend/ai_orchestrator/app/models/__init__.py
backend/ai_orchestrator/app/models/models.py   (ai_execution_logs)
```

---

### Sprint 6.2: Prompt Templates

**Estimated Time:** 6 hours

**Tasks:**

- [ ] Create prompt templates for Resume Optimizer:
  - `resume_optimizer/ats_optimization.j2` — Extract keywords, optimize sections for ATS
  - `resume_optimizer/keyword_extraction.j2` — Extract key skills/terms from job description
  - `resume_optimizer/resume_scoring.j2` — Score resume compatibility with job
  - `resume_optimizer/resume_tailoring.j2` — Tailor resume content for specific role
- [ ] Create prompt templates for Job Match Engine:
  - `job_matcher/match_scoring.j2` — Compute match score (0-100)
  - `job_matcher/skill_gap_analysis.j2` — Identify missing vs matched skills
  - `job_matcher/recommendation.j2` — Generate recommendation text
- [ ] Create prompt templates for Outreach Agent:
  - `outreach/cover_letter.j2` — Generate personalized cover letter
  - `outreach/email_generation.j2` — Generate outreach email
  - `outreach/personalization.j2` — Extract personalization hooks from company data
- [ ] Create prompt templates for Career Intelligence:
  - `career_intelligence/skill_recommendation.j2` — Suggest skills to learn
  - `career_intelligence/interview_questions.j2` — Generate interview prep questions
- [ ] Test each prompt with Gemini API to verify quality output

**Files to create:**
```
backend/ai_orchestrator/app/prompts/resume_optimizer/ats_optimization.j2
backend/ai_orchestrator/app/prompts/resume_optimizer/keyword_extraction.j2
backend/ai_orchestrator/app/prompts/resume_optimizer/resume_scoring.j2
backend/ai_orchestrator/app/prompts/resume_optimizer/resume_tailoring.j2
backend/ai_orchestrator/app/prompts/job_matcher/match_scoring.j2
backend/ai_orchestrator/app/prompts/job_matcher/skill_gap_analysis.j2
backend/ai_orchestrator/app/prompts/job_matcher/recommendation.j2
backend/ai_orchestrator/app/prompts/outreach/cover_letter.j2
backend/ai_orchestrator/app/prompts/outreach/email_generation.j2
backend/ai_orchestrator/app/prompts/outreach/personalization.j2
backend/ai_orchestrator/app/prompts/career_intelligence/skill_recommendation.j2
backend/ai_orchestrator/app/prompts/career_intelligence/interview_questions.j2
```

---

### Sprint 6.3: Match Service

**Estimated Time:** 6 hours

**Tasks:**

- [ ] Create `backend/match_service/` from service template
- [ ] Implement models:
  - `JobMatch` → `job_matches` table
- [ ] Implement match scoring logic:
  - `SkillsMatcher` — computes skill overlap (intersection over union)
  - `ExperienceMatcher` — compares years and relevance
  - `EducationMatcher` — degree and field alignment
  - `LocationMatcher` — geographic proximity scoring
  - `TitleMatcher` — title similarity using embeddings
- [ ] Integrate with AI Orchestrator for ML-enhanced matching
- [ ] Implement batch matching (new job → match all active profiles)
- [ ] Implement endpoints:
  - `POST /api/v1/matches/score` — score single profile+job
  - `GET /api/v1/matches/recommendations/{profileId}` — top-N matches
  - `GET /api/v1/matches/gaps/{profileId}/{jobId}` — skill gaps
  - `POST /api/v1/matches/batch` — trigger batch matching
- [ ] Add Celery task: `compute_matches` for batch processing
- [ ] Connect event: `job.scraped` → triggers match computation

**Files to create:**
```
backend/match_service/app/models/__init__.py
backend/match_service/app/models/models.py
backend/match_service/app/schemas/__init__.py
backend/match_service/app/schemas/match.py
backend/match_service/app/schemas/recommendation.py
backend/match_service/app/services/__init__.py
backend/match_service/app/services/match_service.py
backend/match_service/app/services/skills_matcher.py
backend/match_service/app/services/experience_matcher.py
backend/match_service/app/services/education_matcher.py
backend/match_service/app/services/location_matcher.py
backend/match_service/app/services/title_matcher.py
backend/match_service/app/services/batch_matcher.py
backend/match_service/app/services/ai_match_integrator.py
backend/match_service/app/api/v1/endpoints.py
backend/match_service/app/api/v1/dependencies.py
backend/match_service/app/api/router.py
backend/match_service/app/main.py
backend/match_service/app/core/config.py
backend/match_service/app/core/database.py
backend/match_service/app/tasks.py
backend/match_service/alembic/versions/001_create_match_tables.py
```

---

### Sprint 6.4: AI Orchestrator API & Integration

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Implement AI Orchestrator endpoints:
  - `POST /api/v1/ai/execute` — execute any AI task by agent name
  - `GET /api/v1/ai/agents` — list configured agents and their capabilities
  - `GET /api/v1/ai/usage` — get token usage and cost statistics
- [ ] Wire Resume Optimizer to Resume Service (optimize endpoint calls AI)
- [ ] Wire Job Match Engine to Match Service (AI-enhanced scoring)
- [ ] Add Celery task: `ai_execute` for async AI processing
- [ ] Write tests with mocked LLM responses

**Files to create:**
```
backend/ai_orchestrator/app/api/v1/endpoints.py
backend/ai_orchestrator/app/api/v1/dependencies.py
backend/ai_orchestrator/app/api/router.py
backend/ai_orchestrator/app/main.py
backend/ai_orchestrator/app/core/config.py
backend/ai_orchestrator/app/core/database.py
backend/ai_orchestrator/app/agents/__init__.py
backend/ai_orchestrator/app/agents/base_agent.py
backend/ai_orchestrator/app/agents/resume_optimizer.py
backend/ai_orchestrator/app/agents/job_match_engine.py
backend/ai_orchestrator/app/agents/outreach_agent.py
backend/ai_orchestrator/app/agents/career_intelligence.py
backend/ai_orchestrator/app/tasks.py
```

---

### Sprint 6.5: Tests & Integration

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Write tests for match scoring (unit test each matcher)
- [ ] Write tests for AI orchestrator with mocked providers
- [ ] Write integration test: profile → job → match → score
- [ ] Create Dockerfiles for both services
- [ ] Add both to docker-compose.yml
- [ ] Verify both API keys are valid and fallback chain works

**Files to create:**
```
backend/ai_orchestrator/tests/__init__.py
backend/ai_orchestrator/tests/conftest.py
backend/ai_orchestrator/tests/test_providers.py
backend/ai_orchestrator/tests/test_orchestrator.py
backend/ai_orchestrator/tests/test_prompts.py
backend/ai_orchestrator/Dockerfile
backend/ai_orchestrator/requirements.txt
backend/match_service/tests/__init__.py
backend/match_service/tests/conftest.py
backend/match_service/tests/test_matchers.py
backend/match_service/tests/test_api.py
backend/match_service/tests/test_integration.py
backend/match_service/Dockerfile
backend/match_service/requirements.txt
```

---

### Phase 6 Verification Checklist

- [ ] `POST /api/v1/ai/execute` with resume optimization returns structured result
- [ ] `POST /api/v1/matches/score` returns match score (0-100)
- [ ] `GET /api/v1/matches/recommendations/{profileId}` returns top-10 jobs
- [ ] `GET /api/v1/matches/gaps/{profileId}/{jobId}` lists missing skills
- [ ] Match scoring without AI (rules-based) produces reasonable scores
- [ ] AI-enhanced matching improves accuracy (manual spot-check)
- [ ] `pytest tests/ -v` passes for both services
- [ ] Gemini API responds: `python -c "from google import genai; client = genai.Client(); print(client.models.generate_content(model='gemini-2.0-flash', contents='Hello'))"`
- [ ] Groq API responds: `python -c "from openai import OpenAI; client = OpenAI(base_url='https://api.groq.com/openai/v1'); print(client.chat.completions.create(model='llama-3.3-70b-versatile', messages=[{'role':'user','content':'Hello'}]).choices[0].message.content)"`

---

## 10. Phase 7: Outreach & Application Pipeline

**Goal:** Cover letter/email generation, application package assembly, application state machine.

**Services Involved:** Outreach Service, Application Service

**Dependencies:** Phase 2 (Profile), Phase 4 (Resume), Phase 6 (AI Orchestrator)

---

### Sprint 7.1: Outreach Service

**Estimated Time:** 6 hours

**Tasks:**

- [ ] Create `backend/outreach_service/` from service template
- [ ] Implement models:
  - `OutreachContent` → `outreach_content` table
- [ ] Implement cover letter generation:
  - Integrate with AI Orchestrator (Outreach Agent)
  - Generate personalized cover letter from profile + job + company data
  - Support multiple tones (professional, enthusiastic, concise)
- [ ] Implement email generation:
  - Generate email body with proper formatting
  - Subject line generation
  - Recruiter personalization hooks
- [ ] Implement content versioning (track changes)
- [ ] Implement endpoints:
  - `POST /api/v1/outreach/cover-letter` — generate cover letter
  - `POST /api/v1/outreach/email` — generate email content
  - `GET /api/v1/outreach/templates` — list available templates
  - `POST /api/v1/outreach/preview` — preview generated content
  - `PUT /api/v1/outreach/content/{id}` — manual edit

**Files to create:**
```
backend/outreach_service/app/models/__init__.py
backend/outreach_service/app/models/models.py
backend/outreach_service/app/schemas/__init__.py
backend/outreach_service/app/schemas/cover_letter.py
backend/outreach_service/app/schemas/email.py
backend/outreach_service/app/services/__init__.py
backend/outreach_service/app/services/cover_letter_service.py
backend/outreach_service/app/services/email_service.py
backend/outreach_service/app/services/personalization_service.py
backend/outreach_service/app/services/template_service.py
backend/outreach_service/app/api/v1/endpoints.py
backend/outreach_service/app/api/v1/dependencies.py
backend/outreach_service/app/api/router.py
backend/outreach_service/app/main.py
backend/outreach_service/app/core/config.py
backend/outreach_service/app/core/database.py
backend/outreach_service/app/tasks.py
```

---

### Sprint 7.2: Application Service

**Estimated Time:** 8 hours

**Tasks:**

- [ ] Create `backend/application_service/` from service template
- [ ] Implement models:
  - `Application` → `applications` table
  - `ApplicationEvent` → `application_events` table
- [ ] Implement application state machine:
  - All states: `draft`, `matched`, `resume_generated`, `cover_letter_generated`, `email_prepared`, `sent`, `delivered`, `opened`, `replied`, `interview_scheduled`, `offer_received`, `rejected`, `withdrawn`
  - State transition validation (prevent invalid transitions)
  - Event logging for audit trail
- [ ] Implement application package assembly:
  - Fetch ATS-optimized resume from Resume Service
  - Generate cover letter via Outreach Service
  - Generate email via Outreach Service
  - Assemble package metadata
- [ ] Implement resume auto-attachment:
  - Download PDF from MinIO
  - Attach to email as MIME attachment
- [ ] Implement endpoints:
  - `POST /api/v1/applications` — create application draft
  - `GET /api/v1/applications/{id}` — get application with timeline
  - `POST /api/v1/applications/{id}/submit` — submit via email
  - `POST /api/v1/applications/{id}/retry` — retry failed delivery
  - `PATCH /api/v1/applications/{id}/status` — manual status update
  - `GET /api/v1/applications` — list applications with filters
- [ ] Implement Celery tasks:
  - `assemble_application_package` — async package assembly
  - `send_application` — async email delivery
- [ ] Connect event chain: `application.draft_created` → resume generation → cover letter → email → send

**Files to create:**
```
backend/application_service/app/models/__init__.py
backend/application_service/app/models/models.py
backend/application_service/app/models/state_machine.py
backend/application_service/app/schemas/__init__.py
backend/application_service/app/schemas/application.py
backend/application_service/app/schemas/event.py
backend/application_service/app/services/__init__.py
backend/application_service/app/services/application_service.py
backend/application_service/app/services/state_machine.py
backend/application_service/app/services/package_assembler.py
backend/application_service/app/services/attachment_service.py
backend/application_service/app/services/event_service.py
backend/application_service/app/api/v1/endpoints.py
backend/application_service/app/api/v1/dependencies.py
backend/application_service/app/api/router.py
backend/application_service/app/main.py
backend/application_service/app/core/config.py
backend/application_service/app/core/database.py
backend/application_service/app/tasks.py
```

---

### Sprint 7.3: Tests & Integration

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Write tests for cover letter generation
- [ ] Write tests for application state machine transitions
- [ ] Write tests for package assembly
- [ ] Write integration test: draft → assemble → submit flow
- [ ] Create Dockerfiles for both services
- [ ] Add to docker-compose.yml

**Files to create:**
```
backend/outreach_service/tests/__init__.py
backend/outreach_service/tests/conftest.py
backend/outreach_service/tests/test_cover_letter.py
backend/outreach_service/tests/test_api.py
backend/outreach_service/Dockerfile
backend/outreach_service/requirements.txt
backend/application_service/tests/__init__.py
backend/application_service/tests/conftest.py
backend/application_service/tests/test_state_machine.py
backend/application_service/tests/test_package_assembly.py
backend/application_service/tests/test_api.py
backend/application_service/tests/test_integration.py
backend/application_service/Dockerfile
backend/application_service/requirements.txt
```

---

### Phase 7 Verification Checklist

- [ ] `POST /api/v1/outreach/cover-letter` generates personalized cover letter
- [ ] `POST /api/v1/outreach/email` generates professional email content
- [ ] `POST /api/v1/applications` creates draft application
- [ ] Application state machine correctly transitions through all states
- [ ] Package assembly fetches resume, generates cover letter, assembles package
- [ ] `POST /api/v1/applications/{id}/submit` triggers full pipeline
- [ ] `pytest tests/ -v` passes for both services

---

## 11. Phase 8: Frontend Dashboard

**Goal:** Complete React frontend with all pages and API integration.

**Services Involved:** Frontend (React)

**Dependencies:** Phases 2–7 (all backend APIs)

---

### Sprint 8.1: Frontend Scaffold

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Create React app with Vite + TypeScript
- [ ] Set up Tailwind CSS with custom theme (colors, typography, spacing)
- [ ] Set up React Router v6 with route structure
- [ ] Create API client layer with React Query:
  - `services/api.ts` — Axios/fetch wrapper with JWT token injection
  - `services/auth.ts` — login, register, refresh token logic
  - `services/profiles.ts` — profile CRUD
  - `services/resumes.ts` — resume operations
  - `services/jobs.ts` — job search
  - `services/matches.ts` — match score, recommendations
  - `services/applications.ts` — application CRUD
  - `services/outreach.ts` — cover letter, email generation
- [ ] Set up auth context/provider for global auth state
- [ ] Set up protected route wrapper

**Files to create:**
```
frontend/package.json
frontend/tsconfig.json
frontend/tsconfig.node.json
frontend/vite.config.ts
frontend/tailwind.config.js
frontend/postcss.config.js
frontend/index.html
frontend/public/favicon.ico
frontend/src/main.tsx
frontend/src/App.tsx
frontend/src/vite-env.d.ts
frontend/src/index.css
frontend/src/services/api.ts
frontend/src/services/auth.ts
frontend/src/services/profiles.ts
frontend/src/services/resumes.ts
frontend/src/services/jobs.ts
frontend/src/services/matches.ts
frontend/src/services/applications.ts
frontend/src/services/outreach.ts
frontend/src/context/AuthContext.tsx
frontend/src/components/common/ProtectedRoute.tsx
frontend/src/components/common/Layout.tsx
frontend/src/components/common/Navbar.tsx
frontend/src/components/common/Sidebar.tsx
frontend/src/types/index.ts
```

---

### Sprint 8.2: Core Pages

**Estimated Time:** 12 hours

**Tasks:**

- [ ] **Login/Register page:** Email/password login, registration form, OAuth buttons (Google, LinkedIn)
- [ ] **Dashboard:** Overview stats (applications sent, match scores, upcoming interviews), recent activity feed
- [ ] **Profile pages:**
  - Profile editor (personal info, skills, experience, education, projects, certifications)
  - Skills management with proficiency levels
  - Timeline view for experience/education
- [ ] **Job search page:**
  - Search bar with filters (role, skills, location, remote)
  - Job card list with match score badges
  - Job detail view with apply button
- [ ] **Resume pages:**
  - Master resume viewer/editor
  - Resume generation dialog (select role, template, optimizations)
  - Download PDF button
  - ATS score display
- [ ] **Application pages:**
  - Application list with status badges
  - Application detail with timeline
  - Submit/retry buttons

**Files to create:**
```
frontend/src/pages/LoginPage.tsx
frontend/src/pages/RegisterPage.tsx
frontend/src/pages/DashboardPage.tsx
frontend/src/pages/ProfilePage.tsx
frontend/src/pages/ProfileEditPage.tsx
frontend/src/pages/SkillsPage.tsx
frontend/src/pages/JobsPage.tsx
frontend/src/pages/JobDetailPage.tsx
frontend/src/pages/ResumesPage.tsx
frontend/src/pages/ResumeDetailPage.tsx
frontend/src/pages/ResumeGeneratePage.tsx
frontend/src/pages/ApplicationsPage.tsx
frontend/src/pages/ApplicationDetailPage.tsx
frontend/src/components/profile/PersonalInfoForm.tsx
frontend/src/components/profile/SkillsList.tsx
frontend/src/components/profile/SkillBadge.tsx
frontend/src/components/profile/ExperienceTimeline.tsx
frontend/src/components/profile/EducationList.tsx
frontend/src/components/profile/ProjectsList.tsx
frontend/src/components/jobs/JobCard.tsx
frontend/src/components/jobs/JobFilters.tsx
frontend/src/components/jobs/JobDetail.tsx
frontend/src/components/jobs/MatchScoreBadge.tsx
frontend/src/components/resumes/ResumeCard.tsx
frontend/src/components/resumes/ResumeViewer.tsx
frontend/src/components/resumes/GenerateResumeDialog.tsx
frontend/src/components/resumes/TemplateSelector.tsx
frontend/src/components/applications/ApplicationCard.tsx
frontend/src/components/applications/StatusBadge.tsx
frontend/src/components/applications/TimelineView.tsx
frontend/src/components/applications/SubmitButton.tsx
frontend/src/hooks/useAuth.ts
frontend/src/hooks/useProfile.ts
frontend/src/hooks/useJobs.ts
frontend/src/hooks/useResumes.ts
frontend/src/hooks/useApplications.ts
frontend/src/utils/formatters.ts
frontend/src/utils/validators.ts
```

---

### Sprint 8.3: Docker & Tests

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Create Dockerfile for frontend (multi-stage: build + nginx serve)
- [ ] Add to docker-compose.yml
- [ ] Write basic frontend tests (component smoke tests)
- [ ] Verify all pages render correctly
- [ ] Test full flow: register → create profile → search jobs → generate resume → submit application

**Files to create:**
```
frontend/Dockerfile
frontend/nginx.conf
frontend/src/test-setup.ts
frontend/src/__tests__/LoginPage.test.tsx
frontend/src/__tests__/ProfilePage.test.tsx
frontend/src/__tests__/JobCard.test.tsx
frontend/vitest.config.ts
```

---

### Phase 8 Verification Checklist

- [ ] Login/register flow works end-to-end
- [ ] Profile editor loads and saves
- [ ] Job search returns results with match scores
- [ ] Resume generation dialog shows templates and generates PDF
- [ ] Application list shows status timeline
- [ ] Full flow works: register → create profile → search → match → generate resume → submit application
- [ ] Running `docker compose up frontend` serves the app at `http://localhost:3000`
- [ ] No console errors in browser

---

## 12. Phase 9: Email Delivery & Tracking

**Goal:** Actual email delivery via SMTP/Postal, delivery tracking, application analytics dashboard.

**Services Involved:** Application Service (delivery logic), Tracking Service, Notification Service

**Dependencies:** Phase 7 (Application Service), Phase 8 (Frontend)

---

### Sprint 9.1: Email Delivery Implementation

**Estimated Time:** 6 hours

**Tasks:**

- [ ] Implement email provider abstraction in Application Service:
  - `SMTPProvider` — direct SMTP delivery (smtplib)
  - `PostalProvider` — self-hosted Postal transactional email server
- [ ] Implement email attachment (resume PDF from MinIO)
- [ ] Implement delivery status tracking:
  - Record provider message ID
  - Log delivery attempt (success/failure) in `email_delivery_logs`
  - Implement retry logic with exponential backoff (5 retries)
- [ ] Implement delivery webhook endpoints:
  - `POST /api/v1/webhooks/delivery` — generic delivery webhook
  - Update application status based on webhook (delivered, opened, bounced)
- [ ] Implement email tracking (open tracking pixel, link tracking) — optional, via Postal

**Files to modify/create:**
```
backend/application_service/app/services/email/__init__.py
backend/application_service/app/services/email/base_provider.py
backend/application_service/app/services/email/smtp_provider.py
backend/application_service/app/services/email/postal_provider.py
backend/application_service/app/services/email/attachment_service.py
backend/application_service/app/services/delivery_service.py
backend/application_service/app/services/delivery_logger.py
backend/application_service/app/api/v1/webhooks.py
backend/application_service/app/core/email_config.py
```

---

### Sprint 9.2: Tracking Service

**Estimated Time:** 5 hours

**Tasks:**

- [ ] Create `backend/tracking_service/` from service template
- [ ] Implement tracking endpoints:
  - `GET /api/v1/tracking/applications` — list all applications for user
  - `GET /api/v1/tracking/applications/{id}` — get application timeline
  - `GET /api/v1/tracking/stats` — aggregate stats (total sent, success rate, avg response time)
  - `GET /api/v1/tracking/analytics` — detailed analytics (daily trend, source breakdown)
  - `POST /api/v1/tracking/export` — export application data as CSV/JSON
- [ ] Implement analytics computation:
  - Applications by status (funnel visualization)
  - Daily/weekly application counts
  - Source performance (which job sources generate most interviews)
  - Response rate and average response time
- [ ] Implement notification service:
  - In-app notifications (WebSocket via Redis pub-sub)
  - Application status change alerts
  - New job match alerts
  - Digest emails (weekly summary)

**Files to create:**
```
backend/tracking_service/app/models/__init__.py
backend/tracking_service/app/models/models.py
backend/tracking_service/app/schemas/__init__.py
backend/tracking_service/app/schemas/tracking.py
backend/tracking_service/app/schemas/analytics.py
backend/tracking_service/app/services/__init__.py
backend/tracking_service/app/services/tracking_service.py
backend/tracking_service/app/services/analytics_service.py
backend/tracking_service/app/services/export_service.py
backend/tracking_service/app/api/v1/endpoints.py
backend/tracking_service/app/api/v1/dependencies.py
backend/tracking_service/app/api/router.py
backend/tracking_service/app/main.py
backend/tracking_service/app/core/config.py
backend/tracking_service/app/core/database.py
backend/tracking_service/tests/__init__.py
backend/tracking_service/tests/conftest.py
backend/tracking_service/tests/test_analytics.py
backend/tracking_service/tests/test_api.py
backend/tracking_service/Dockerfile
backend/tracking_service/requirements.txt
backend/notification_service/app/__init__.py
backend/notification_service/app/main.py
backend/notification_service/app/services/__init__.py
backend/notification_service/app/services/notification_service.py
backend/notification_service/app/services/websocket_service.py
backend/notification_service/app/core/config.py
backend/notification_service/Dockerfile
backend/notification_service/requirements.txt
```

---

### Sprint 9.3: Frontend Tracking Pages

**Estimated Time:** 4 hours

**Tasks:**

- [ ] Add tracking dashboard page:
  - Application funnel visualization (draft → sent → delivered → replied → interview)
  - Stats cards (total sent, success rate, response rate)
  - Daily application chart
  - Source performance breakdown
- [ ] Add notification center:
  - Notification list with read/unread
  - Real-time notifications via WebSocket
  - Notification preferences
- [ ] Add export button for application data

**Files to create:**
```
frontend/src/pages/TrackingPage.tsx
frontend/src/pages/AnalyticsPage.tsx
frontend/src/pages/NotificationsPage.tsx
frontend/src/components/tracking/ApplicationFunnel.tsx
frontend/src/components/tracking/StatsCard.tsx
frontend/src/components/tracking/DailyChart.tsx
frontend/src/components/tracking/SourceBreakdown.tsx
frontend/src/components/tracking/Timeline.tsx
frontend/src/components/notifications/NotificationList.tsx
frontend/src/components/notifications/NotificationBadge.tsx
frontend/src/hooks/useTracking.ts
frontend/src/hooks/useNotifications.ts
```

---

### Phase 9 Verification Checklist

- [ ] Email sent via SMTP/Postal reaches inbox (test with Mailpit or real SMTP)
- [ ] Resume PDF is correctly attached to email
- [ ] Delivery webhook updates application status correctly
- [ ] Tracked delivery logs show sent → delivered → opened states
- [ ] `GET /api/v1/tracking/stats` returns correct aggregate stats
- [ ] Analytics page shows funnel visualization
- [ ] In-app notifications appear in real-time
- [ ] Export downloads CSV with correct data

---

## 13. Phase 10: Polish & Scale

**Goal:** Monitoring, alerting, performance optimization, documentation finalization.

**Services Involved:** All services

**Dependencies:** All phases complete

---

### Sprint 10.1: Logging & Monitoring

**Estimated Time:** 6 hours

**Tasks:**

- [ ] Set up Prometheus + Grafana:
  - Add Prometheus metrics endpoints to each service (`/metrics`)
  - Configure prometheus.yml with all service targets
  - Create Grafana dashboards:
    - Service health dashboard (uptime, request rate, error rate)
    - Queue dashboard (depth, processing time, failure rate)
    - AI dashboard (tokens consumed, generation time, per-agent breakdown)
    - Business dashboard (applications sent, matches found, emails delivered)
  - Add structured JSON logging to all services via structlog
- [ ] Set up Loki + Promtail for log aggregation:
  - Configure Promtail to scrape Docker container logs
  - Create Loki data source in Grafana
  - Create log exploration dashboard
- [ ] Set up OpenTelemetry tracing:
  - Add OpenTelemetry instrumentation to FastAPI apps
  - Configure trace export to Jaeger or Grafana Tempo
  - Set sampling rates (100% errors, 10% success)

**Files to create:**
```
docker/prometheus/prometheus.yml
docker/prometheus/alert.rules.yml
docker/grafana/dashboards/service-health.json
docker/grafana/dashboards/queue-status.json
docker/grafana/dashboards/ai-usage.json
docker/grafana/dashboards/business-kpis.json
docker/grafana/datasources/prometheus.yml
docker/grafana/datasources/loki.yml
docker/loki/loki-config.yml
docker/promtail/promtail-config.yml
docker/otel-collector/otel-config.yml
```

---

### Sprint 10.2: Performance Optimization

**Estimated Time:** 6 hours

**Tasks:**

- [ ] Profile and optimize slow endpoints:
  - Add database query optimization (missing indexes, N+1 queries)
  - Add Redis caching for frequently accessed data
  - Add pagination limits to all list endpoints
  - Implement response compression (gzip)
- [ ] Optimize AI agent performance:
  - Add request batching for high-volume AI tasks
  - Implement response caching (same prompt → cached result)
  - Add model warm-up script (pre-load model into memory)
- [ ] Optimize PDF generation:
  - Cache rendered HTML templates
  - Use PDF/A format for smaller file sizes
  - Add generation timeouts
- [ ] Database optimizations:
  - Review and add missing indexes
  - Configure PgBouncer connection pooling
  - Set up PostgreSQL query performance monitoring
- [ ] Add rate limiting to all API endpoints

**Files to modify/create:**
```
backend/shared/utils/cache.py             (Redis caching decorators)
backend/shared/middleware/rate_limit.py    (Rate limiting middleware)
backend/shared/middleware/compression.py   (Response compression)
# (No model warm-up needed — Gemini API is fully managed)
```

---

### Sprint 10.3: Documentation & Finalization

**Estimated Time:** 6 hours

**Tasks:**

- [ ] Create `docs/api-reference.md`:
  - Auto-generate from FastAPI OpenAPI schema
  - Add manual descriptions for complex endpoints
  - Include cURL examples for each endpoint
  - Include request/response body examples
- [ ] Create `docs/setup.md`:
  - Prerequisites (Docker, Python 3.12+, Node 20+, Gemini API key, Groq API key)
  - Step-by-step setup instructions
  - Environment configuration
  - Running tests
  - Common troubleshooting
- [ ] Create `CONTRIBUTING.md` with:
  - Code style guide (Black, Ruff)
  - PR workflow
  - Testing guidelines
- [ ] Final review pass on all docs for consistency
- [ ] Add docstrings to all public API endpoints
- [ ] Ensure all environment variables are documented in `.env.example`
- [ ] Update version numbers and dates

**Files to create:**
```
docs/api-reference.md
docs/setup.md
CONTRIBUTING.md
```

---

### Phase 10 Verification Checklist

- [ ] Prometheus scrapes all service `/metrics` endpoints
- [ ] Grafana dashboards display real-time data
- [ ] Loki ingests logs from all services
- [ ] OpenTelemetry traces show end-to-end request flow
- [ ] API rate limiting works (exceed limit → 429)
- [ ] Redis caching reduces response times for frequent queries
- [ ] Documentation is complete and accurate
- [ ] All environment variables documented

---

## 14. Future Phases

These phases extend the platform beyond the core implementation:

### Phase 11: Career Intelligence Agent
- Missing skill detection and learning path recommendations
- Career progression suggestions
- Interview preparation (generate questions + answer feedback)
- Integration with learning platforms (Coursera, Udemy — optional)

### Phase 12: Browser Automation Agent
- Auto-fill job application forms on external portals
- One-click apply for supported platforms
- Headless browser integration (Playwright/Selenium)
- Session management and CAPTCHA handling

### Phase 13: Advanced AI Features
- RAG-based semantic job search (Qdrant/Weaviate vector DB)
- Resume A/B testing (generate multiple versions, track performance)
- Salary prediction and negotiation assistance
- Network analysis (mutual connections at target companies)

### Phase 14: Enterprise Features
- Multi-user teams (shared job boards, collaborative applications)
- SSO/SAML authentication
- Audit logging for compliance
- Admin dashboard with user management

---

## 15. Appendix: Quick-Reference Command Cheatsheet

```bash
# ─── Infrastructure ─────────────────────────────────────
docker compose up -d                    # Start all services
docker compose up -d postgres redis minio  # Start only infra
docker compose logs -f profile-api      # Follow service logs
docker compose down                     # Stop all services

# ─── Database ───────────────────────────────────────────
alembic upgrade head                    # Run all migrations
alembic revision --autogenerate -m "msg"  # Create migration
psql -h localhost -U postgres -d career_platform  # Connect

# ─── Testing ────────────────────────────────────────────
pytest backend/profile_service/tests/   # Test single service
pytest tests/ -v --cov=app              # Test with coverage
make test                               # Run all tests

# ─── Development ────────────────────────────────────────
cd backend/profile_service && uvicorn app.main:app --reload  # Run service
cd frontend && npm run dev              # Run frontend
pip install -r requirements.txt         # Install deps

# ─── AI ─────────────────────────────────────────────────
pip install google-genai                # Install Gemini SDK
pip install openai                       # Install OpenAI SDK (for Groq)
export GEMINI_API_KEY="your-key-here"  # Set Gemini API key
export GROQ_API_KEY="your-key-here"    # Set Groq API key
python -c "from google import genai; client = genai.Client(); print(client.models.generate_content(model='gemini-2.0-flash', contents='Hello'))"  # Test Gemini
python -c "from openai import OpenAI; client = OpenAI(base_url='https://api.groq.com/openai/v1'); print(client.chat.completions.create(model='llama-3.3-70b-versatile', messages=[{'role':'user','content':'Hello'}]).choices[0].message.content)"  # Test Groq

# ─── Service Scaffolding ────────────────────────────────
bash backend/scripts/create_service.sh my_service  # Create new service
```

---

> **Document Version:** 1.0  
> **Total Phases:** 10 core + 4 future  
> **Estimated Total:** 12–16 weeks (full-time solo)  
> **Next Step:** Begin Phase 1 — Foundation & Infrastructure
