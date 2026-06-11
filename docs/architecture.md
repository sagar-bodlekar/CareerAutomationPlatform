# AI Career Automation Platform — Architecture Document

> **Version:** 1.2  
> **Status:** Draft  
> **Last Updated:** June 11, 2026  
> **License Commitment:** All core infrastructure is free and open-source. AI uses Google Gemini API (generous free tier available; no required subscriptions).

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Principles](#2-architecture-principles)
3. [High-Level System Architecture](#3-high-level-system-architecture)
4. [Component Architecture](#4-component-architecture)
5. [Data Models & Schema](#5-data-models--schema)
6. [API Design](#6-api-design)
7. [Workflow Pipelines](#7-workflow-pipelines)
8. [AI Agent Architecture](#8-ai-agent-architecture)
9. [Technology Stack](#9-technology-stack)
10. [Directory Structure](#10-directory-structure)
11. [Queue & Task Processing](#11-queue--task-processing)
12. [Storage Strategy](#12-storage-strategy)
13. [Integration Patterns](#13-integration-patterns)
14. [Security Architecture](#14-security-architecture)
15. [Deployment Architecture](#15-deployment-architecture)
16. [Monitoring & Observability](#16-monitoring--observability)
17. [Phase Roadmap](#17-phase-roadmap)
18. [Success Metrics](#18-success-metrics)
19. [Appendices](#19-appendices)

---

## 1. System Overview

The AI Career Automation Platform is a unified, modular system that automates the entire job application lifecycle. It combines three core domains — **Resume Building**, **Job Discovery & Matching**, and **Application Outreach & Tracking** — into a single intelligent platform powered by AI agents.

### 1.1 Core Philosophy

- **Single Source of Truth (SSOT):** The user profile is the central data model. Every module reads from and writes to this shared profile. No duplicate data management.
- **Event-Driven Automation:** State changes (e.g., "job matched") trigger downstream workflows (e.g., "generate resume") automatically.
- **AI-First:** AI agents drive all optimization, generation, and matching logic. Humans review and approve, never manually construct.
- **Modular & Extensible:** Each domain is an independent service with well-defined contracts. New modules (e.g., Interview Prep Agent) can be added without modifying existing ones.

### 1.2 Target User Flow

```
Create Profile
    → Discover Jobs (automated)
    → Match Opportunities (AI-scored)
    → Optimize Resume for ATS (AI)
    → Generate Role-Specific Resume (AI → PDF)
    → Generate Cover Letter (AI)
    → Build Application Package (automated)
    → Attach Resume + Send Email (automated)
    → Track Progress (dashboard)
    → Prepare for Interview (AI, future)
```

---

## 2. Architecture Principles

| Principle | Description |
|-----------|-------------|
| **Separation of Concerns** | Each service owns one domain. No cross-domain logic leakage. |
| **API-First Design** | All functionality is exposed via REST/gRPC APIs. No direct database sharing between services. |
| **Idempotent Operations** | All task processing is idempotent to support retries without side effects. |
| **Fail Gracefully** | Downstream failures (e.g., email provider down) don't cascade to upstream services. |
| **Observability by Default** | Every service emits structured logs, metrics, and traces. |
| **Stateless Services** | Services are stateless; state lives in the database and message queue. Enables horizontal scaling. |
| **Configuration Over Code** | Environment-driven configuration for all service behavior. |

---

## 3. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                               │
├──────────────────────┬──────────────────────┬───────────────────────┤
│   React Dashboard    │    REST API Client   │   Browser Extension   │
│   (Web App)          │    (CLI / SDK)       │   (Future)            │
└──────────┬───────────┴──────────┬───────────┴───────────┬───────────┘
           │                      │                       │
           ▼                      ▼                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                                   │
│                    (Traefik / Nginx + Auth)                          │
│              Rate Limiting · Auth · Routing · Logging                │
└──────┬───────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                                   │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Profile      │  │  Resume       │  │  Job          │             │
│  │  Service      │  │  Service      │  │  Service      │             │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Match        │  │  Outreach     │  │  Application  │             │
│  │  Service      │  │  Service      │  │  Service      │             │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Tracking     │  │  AI Orchestr. │  │  Notification │             │
│  │  Service      │  │  Service      │  │  Service      │             │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└──────┬───────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      AI AGENT LAYER                                  │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Resume       │  │  Job Match    │  │  Outreach     │             │
│  │  Optimizer    │  │  Engine       │  │  Agent        │             │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐                                 │
│  │  Career       │  │  ATS          │                                 │
│  │  Intelligence │  │  Analyzer     │                                 │
│  └──────────────┘  └──────────────┘                                 │
└──────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     DATA & INFRASTRUCTURE LAYER                       │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │PostgreSQL│  │  Redis   │  │  MinIO   │  │  Queue   │            │
│  │  (SSOT)  │  │ (Cache)  │  │(Storage) │  │(Celery)  │            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.1 Layer Responsibilities

| Layer | Responsibility |
|-------|----------------|
| **Client Layer** | Web dashboard, CLI tool, future browser extension |
| **API Gateway** | Auth, rate limiting, request routing, API versioning |
| **Service Layer** | Business logic for each domain (stateless, horizontally scalable) |
| **AI Agent Layer** | LLM-powered agents for optimization, matching, generation |
| **Data Layer** | Persistence, caching, file storage, async task queues |

---

## 4. Component Architecture

### 4.1 Profile Service

**Purpose:** Manages the Single Source of Truth — the user's complete career profile.

**Responsibilities:**
- CRUD operations on user profile
- Profile validation & schema enforcement
- Profile versioning (track changes over time)
- Profile import/export (LinkedIn, JSON, XML)
- Profile analytics (skill coverage, experience gaps)

**Dependencies:**
- PostgreSQL (profile data)
- Redis (profile cache)

**Key Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/profiles` | Create profile |
| GET | `/api/v1/profiles/{id}` | Get profile |
| PUT | `/api/v1/profiles/{id}` | Update profile |
| GET | `/api/v1/profiles/{id}/export` | Export profile as JSON |
| POST | `/api/v1/profiles/{id}/import` | Import profile from external source |

---

### 4.2 Resume Service

**Purpose:** Generates, optimizes, and manages resumes.

**Responsibilities:**
- Master resume creation from profile
- Role-specific resume generation (Frontend, Backend, Full Stack, Python, AI/ML, DevOps)
- ATS-optimized resume generation
- PDF generation with templating
- Resume versioning & history
- Template management (multiple layouts & styles)

**Dependencies:**
- Profile Service (reads profile data)
- AI Agent Layer (Resume Optimizer, ATS Analyzer)
- Storage (PDF files)
- Queue (async resume generation)

**Key Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/resumes` | Create master resume |
| POST | `/api/v1/resumes/{id}/generate` | Generate role-specific resume |
| GET | `/api/v1/resumes/{id}` | Get resume metadata |
| GET | `/api/v1/resumes/{id}/download` | Download PDF |
| PUT | `/api/v1/resumes/{id}` | Update resume content |
| POST | `/api/v1/resumes/{id}/optimize` | Trigger ATS optimization |

---

### 4.3 Job Service

**Purpose:** Discovers, scrapes, normalizes, and stores job listings.

**Responsibilities:**
- Job scraping from multiple sources (Naukri, Wellfound, RemoteOK, company career pages)
- Job normalization (unified schema across sources)
- Job filtering (role, skills, experience, location, remote preference)
- Job deduplication
- Schedule management (scrape intervals per source)
- Source health monitoring

**Sources (Planned):**
- Naukri
- Wellfound (AngelList)
- RemoteOK
- LinkedIn (via API/scraping)
- Company career pages (generic scraper)
- Indeed
- Glassdoor

**Dependencies:**
- PostgreSQL (job storage)
- Queue (async scraping tasks)
- Redis (scraping dedup cache, rate limiting)

**Key Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/jobs` | List/filter/search jobs |
| GET | `/api/v1/jobs/{id}` | Get job details |
| POST | `/api/v1/jobs/refresh` | Trigger immediate scrape |
| GET | `/api/v1/jobs/sources` | List configured sources & status |
| PUT | `/api/v1/jobs/sources/{id}` | Update source configuration |

---

### 4.4 Match Service

**Purpose:** Compares candidate profiles against job descriptions to compute compatibility scores.

**Responsibilities:**
- Profile-to-job matching score computation
- Skill gap analysis
- Strength area identification
- Match recommendations (top-N jobs for user)
- Batch matching for new jobs vs all active profiles

**Dependencies:**
- Profile Service (profile data)
- Job Service (job listings)
- AI Agent Layer (Job Match Engine)

**Match Score Components:**
| Factor | Weight | Description |
|--------|--------|-------------|
| Skills Match | 35% | Overlap between profile skills and job requirements |
| Experience Match | 25% | Years and relevance of experience |
| Education Match | 15% | Degree and field alignment |
| Location Match | 10% | Geographic proximity or remote compatibility |
| Title Match | 10% | Current/previous title alignment with target role |
| Certification Match | 5% | Relevant certifications |

**Key Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/matches/score` | Get match score for profile+job |
| GET | `/api/v1/matches/recommendations/{profileId}` | Get top job matches |
| GET | `/api/v1/matches/gaps/{profileId}/{jobId}` | Get detailed skill gaps |
| POST | `/api/v1/matches/batch` | Trigger batch matching |

---

### 4.5 Outreach Service

**Purpose:** Generates and manages cover letters, emails, and application content.

**Responsibilities:**
- Cover letter generation (AI-powered, personalized)
- Email content generation
- Recruiter-specific personalization
- Template management for outreach content
- Bulk outreach campaign management

**Dependencies:**
- Profile Service (user data)
- Job Service (job details)
- AI Agent Layer (Outreach Agent)

**Key Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/outreach/cover-letter` | Generate cover letter |
| POST | `/api/v1/outreach/email` | Generate email content |
| GET | `/api/v1/outreach/templates` | List email templates |
| POST | `/api/v1/outreach/preview` | Preview generated content |

---

### 4.6 Application Service

**Purpose:** Orchestrates the complete application package and delivery pipeline.

**Responsibilities:**
- Application package assembly (resume PDF + cover letter + email)
- Resume attachment to email
- Application state machine management
- Application submission via email (SMTP, Gmail, Outlook)
- Delivery tracking & logging
- Retry logic for failed deliveries

**Application State Machine:**
```
Draft
  → Matched
  → Resume Generated
  → Cover Letter Generated
  → Email Prepared
  → Sent (email dispatched)
  → Delivered (delivery confirmed by provider)
  → Opened (email tracked)
  → Replied (response received)
  → Interview Scheduled
  → Offer Received
  → Rejected (terminal)
  → Withdrawn (terminal)
```

**Dependencies:**
- Resume Service (PDF generation)
- Outreach Service (cover letter, email)
- Email providers (SMTP, Gmail API, Outlook API)
- Queue (async delivery)

**Key Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/applications` | Create application |
| GET | `/api/v1/applications/{id}` | Get application status |
| POST | `/api/v1/applications/{id}/submit` | Submit/send application |
| POST | `/api/v1/applications/{id}/retry` | Retry failed delivery |
| PATCH | `/api/v1/applications/{id}/status` | Update status (manual) |

---

### 4.7 Tracking Service

**Purpose:** Provides a unified view of all applications, their lifecycle, and analytics.

**Responsibilities:**
- Application status aggregation
- Timeline & history view
- Analytics & metrics computation
- Notification generation (via Notification Service)
- Export reports

**Key Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/tracking/applications` | List all applications for user |
| GET | `/api/v1/tracking/applications/{id}` | Get application timeline |
| GET | `/api/v1/tracking/stats` | Get aggregate stats |
| GET | `/api/v1/tracking/analytics` | Get detailed analytics |
| POST | `/api/v1/tracking/export` | Export application data |

---

### 4.8 AI Orchestrator Service

**Purpose:** Manages AI agent invocation, prompt construction, response parsing, and fallback logic.

**Responsibilities:**
- AI agent routing (which agent handles which task)
- Prompt template management
- LLM provider abstraction (OpenAI, Anthropic, local models)
- Context window management (trimming, summarization for long inputs)
- Response validation & structured parsing
- Fallback & retry logic across providers
- Token usage tracking & cost optimization

**AI Agent Registry:**
| Agent | Model | Tasks |
|-------|-------|-------|
| Resume Optimizer | Gemini API (gemini-2.0-flash / gemini-1.5-pro) | ATS optimization, keyword extraction, resume tailoring |
| Job Match Engine | Gemini API (gemini-2.0-flash / gemini-1.5-pro) | Match scoring, skill gap detection |
| Outreach Agent | Gemini API (gemini-2.0-flash / gemini-1.5-pro) | Cover letter, email, personalization |
| Career Intelligence | Gemini API (gemini-2.0-flash / gemini-1.5-pro) | Career recommendations, skill suggestions, interview prep |

**Key Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/ai/execute` | Execute an AI task |
| GET | `/api/v1/ai/agents` | List configured AI agents |
| GET | `/api/v1/ai/usage` | Get token usage & cost stats |

---

### 4.9 Notification Service

**Purpose:** Handles all user-facing notifications (email, in-app, push).

**Responsibilities:**
- Application status change notifications
- New job match alerts
- Failed delivery alerts
- Weekly digests

**Channels:**
- In-app (WebSocket push)
- Email (transactional)
- Push (future)

---

## 5. Data Models & Schema

### 5.1 User Profile (SSOT)

This is the canonical data model. All other entities reference this.

```sql
-- Core Profile Table
CREATE TABLE user_profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL UNIQUE REFERENCES auth_users(id),
    headline        VARCHAR(200),
    summary         TEXT,
    total_experience_years DECIMAL(4,1),
    current_role    VARCHAR(100),
    preferred_roles TEXT[],          -- Array of role preferences
    preferred_locations TEXT[],      -- Array of preferred locations
    remote_preference VARCHAR(20),   -- 'remote', 'hybrid', 'onsite', 'any'
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Personal Information
CREATE TABLE personal_info (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id      UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    full_name       VARCHAR(150),
    email           VARCHAR(255),
    phone           VARCHAR(30),
    location        VARCHAR(200),
    linkedin_url    VARCHAR(500),
    portfolio_url   VARCHAR(500),
    github_url      VARCHAR(500),
    website_url     VARCHAR(500),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Skills
CREATE TABLE skills (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id      UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    category        VARCHAR(50),     -- 'technical', 'soft', 'domain', 'language'
    proficiency     VARCHAR(20),     -- 'beginner', 'intermediate', 'advanced', 'expert'
    years_experience DECIMAL(3,1),
    is_top_skill    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_skills_profile_id ON skills(profile_id);

-- Work Experience
CREATE TABLE work_experiences (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id      UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    company_name    VARCHAR(200) NOT NULL,
    title           VARCHAR(200) NOT NULL,
    location        VARCHAR(200),
    start_date      DATE NOT NULL,
    end_date        DATE,
    is_current      BOOLEAN DEFAULT FALSE,
    description     TEXT,
    achievements    TEXT[],
    technologies    TEXT[],
    company_url     VARCHAR(500),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_experiences_profile_id ON work_experiences(profile_id);

-- Education
CREATE TABLE education (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id      UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    institution     VARCHAR(200) NOT NULL,
    degree          VARCHAR(100),
    field           VARCHAR(100),
    start_date      DATE,
    end_date        DATE,
    gpa             DECIMAL(3,2),
    achievements    TEXT[],
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_education_profile_id ON education(profile_id);

-- Projects
CREATE TABLE projects (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id      UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    technologies    TEXT[],
    url             VARCHAR(500),
    start_date      DATE,
    end_date        DATE,
    is_current      BOOLEAN DEFAULT FALSE,
    highlights      TEXT[],
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_projects_profile_id ON projects(profile_id);

-- Certifications
CREATE TABLE certifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id      UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    issuer          VARCHAR(200),
    issue_date      DATE,
    expiry_date     DATE,
    credential_id   VARCHAR(100),
    credential_url  VARCHAR(500),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_certifications_profile_id ON certifications(profile_id);

-- Social Links
CREATE TABLE social_links (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id      UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    platform        VARCHAR(50) NOT NULL,   -- 'github', 'linkedin', 'twitter', etc.
    url             VARCHAR(500) NOT NULL,
    username        VARCHAR(100),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_social_links_profile_id ON social_links(profile_id);
```

### 5.2 Resume Schema

```sql
-- Resumes
CREATE TABLE resumes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id      UUID NOT NULL REFERENCES user_profiles(id),
    title           VARCHAR(200) NOT NULL,      -- 'Master Resume', 'Frontend Resume', etc.
    resume_type     VARCHAR(50) NOT NULL,        -- 'master', 'role-specific', 'ats-optimized'
    target_role     VARCHAR(100),                -- Role this resume is optimized for
    target_job_id   UUID REFERENCES jobs(id),    -- Specific job (for ATS-optimized)
    content         JSONB NOT NULL,              -- Structured resume content
    ats_score       DECIMAL(5,2),                -- ATS compatibility score
    version         INT DEFAULT 1,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_resumes_profile_id ON resumes(profile_id);
CREATE INDEX idx_resumes_type ON resumes(profile_id, resume_type);

-- Resume Files (PDF storage metadata)
CREATE TABLE resume_files (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id       UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    file_path       VARCHAR(500) NOT NULL,       -- Path in S3/MinIO/local storage
    file_size_bytes BIGINT,
    mime_type       VARCHAR(50) DEFAULT 'application/pdf',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_resume_files_resume_id ON resume_files(resume_id);

-- Resume Templates
CREATE TABLE resume_templates (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    layout_config   JSONB NOT NULL,              -- Template layout configuration
    is_default      BOOLEAN DEFAULT FALSE,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 5.3 Job Schema

```sql
-- Jobs
CREATE TABLE jobs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id         VARCHAR(200),                -- Original ID from source
    source              VARCHAR(50) NOT NULL,         -- 'naukri', 'wellfound', 'remoteok', etc.
    source_url          VARCHAR(1000) NOT NULL,
    title               VARCHAR(200) NOT NULL,
    company_name        VARCHAR(200),
    company_url         VARCHAR(500),
    company_logo_url    VARCHAR(500),
    location            VARCHAR(200),
    location_type       VARCHAR(30),                 -- 'remote', 'hybrid', 'onsite'
    salary_min          DECIMAL(12,2),
    salary_max          DECIMAL(12,2),
    salary_currency     VARCHAR(3) DEFAULT 'USD',
    description         TEXT,
    requirements        TEXT,
    responsibilities    TEXT,
    required_skills     TEXT[],
    preferred_skills    TEXT[],
    experience_required VARCHAR(50),                 -- e.g., '3-5 years'
    education_required  VARCHAR(100),
    employment_type     VARCHAR(50),                 -- 'full-time', 'part-time', 'contract'
    posted_date         TIMESTAMPTZ,
    expiry_date         TIMESTAMPTZ,
    is_active           BOOLEAN DEFAULT TRUE,
    raw_data            JSONB,                       -- Original scraped data
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source, external_id)
);
CREATE INDEX idx_jobs_source ON jobs(source);
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_jobs_skills ON jobs USING GIN(required_skills);
CREATE INDEX idx_jobs_posted ON jobs(posted_date DESC);
CREATE INDEX idx_jobs_active ON jobs(is_active) WHERE is_active = TRUE;
```

### 5.4 Match Schema

```sql
-- Job Matches
CREATE TABLE job_matches (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id      UUID NOT NULL REFERENCES user_profiles(id),
    job_id          UUID NOT NULL REFERENCES jobs(id),
    match_score     DECIMAL(5,2) NOT NULL,          -- 0.00 to 100.00
    skills_match    JSONB,                           -- {matched: [...], missing: [...], extra: [...]}
    experience_match JSONB,                          -- {score: ..., analysis: ...}
    education_match JSONB,
    location_match  JSONB,
    strength_areas  TEXT[],                          -- Top strengths for this match
    gaps            TEXT[],                          -- Skill/experience gaps
    recommendation  VARCHAR(20),                     -- 'strong_match', 'good_match', 'weak_match', 'no_match'
    raw_analysis    JSONB,                           -- Full AI analysis output
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(profile_id, job_id)
);
CREATE INDEX idx_matches_profile ON job_matches(profile_id);
CREATE INDEX idx_matches_score ON job_matches(match_score DESC);
```

### 5.5 Application Schema

```sql
-- Applications
CREATE TABLE applications (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id          UUID NOT NULL REFERENCES user_profiles(id),
    job_id              UUID NOT NULL REFERENCES jobs(id),
    match_id            UUID REFERENCES job_matches(id),
    resume_id           UUID REFERENCES resumes(id),
    status              VARCHAR(30) NOT NULL DEFAULT 'draft',
                        -- 'draft', 'matched', 'resume_generated', 'cover_letter_generated',
                        -- 'email_prepared', 'sent', 'delivered', 'opened', 'replied',
                        -- 'interview_scheduled', 'offer_received', 'rejected', 'withdrawn'
    cover_letter_id     UUID REFERENCES outreach_content(id),
    email_content_id    UUID REFERENCES outreach_content(id),
    email_provider      VARCHAR(30),                -- 'smtp', 'gmail', 'outlook'
    delivery_status     JSONB,                      -- {sent_at, delivered_at, opened_at, ...}
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_applications_profile ON applications(profile_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_created ON applications(created_at DESC);

-- Application Timeline Events
CREATE TABLE application_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id  UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    from_status     VARCHAR(30),
    to_status       VARCHAR(30) NOT NULL,
    triggered_by    VARCHAR(50),                     -- 'system', 'ai', 'user', 'webhook'
    metadata        JSONB,                           -- Additional event data
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_app_events_app ON application_events(application_id);
CREATE INDEX idx_app_events_created ON application_events(created_at DESC);
```

### 5.6 Outreach Content Schema

```sql
-- Outreach Content (Cover Letters & Emails)
CREATE TABLE outreach_content (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id      UUID NOT NULL REFERENCES user_profiles(id),
    content_type    VARCHAR(30) NOT NULL,            -- 'cover_letter', 'email'
    job_id          UUID REFERENCES jobs(id),
    subject         VARCHAR(500),                    -- Email subject line
    body            TEXT NOT NULL,                   -- Full content body
    tone            VARCHAR(30),                     -- 'professional', 'enthusiastic', 'concise'
    personalization JSONB,                           -- Personalization metadata
    version         INT DEFAULT 1,
    ai_model        VARCHAR(50),                     -- Model used for generation
    token_count     INT,                             -- Tokens consumed
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_outreach_profile ON outreach_content(profile_id);
CREATE INDEX idx_outreach_type ON outreach_content(profile_id, content_type);
```

### 5.7 Email Delivery Schema

```sql
-- Email Delivery Logs
CREATE TABLE email_delivery_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id  UUID REFERENCES applications(id),
    from_address    VARCHAR(255) NOT NULL,
    to_address      VARCHAR(255) NOT NULL,
    subject         VARCHAR(500),
    provider        VARCHAR(30) NOT NULL,            -- 'smtp', 'gmail', 'outlook'
    provider_message_id VARCHAR(500),
    status          VARCHAR(30) NOT NULL,             -- 'sent', 'delivered', 'failed', 'bounced', 'opened'
    status_code     VARCHAR(10),
    error_message   TEXT,
    sent_at         TIMESTAMPTZ,
    delivered_at    TIMESTAMPTZ,
    opened_at       TIMESTAMPTZ,
    metadata        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_email_logs_app ON email_delivery_logs(application_id);
CREATE INDEX idx_email_logs_status ON email_delivery_logs(status);
```

### 5.8 Job Sources Configuration

```sql
-- Job Sources Configuration
CREATE TABLE job_sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL,
    source_type     VARCHAR(50) NOT NULL,            -- 'api', 'scraper', 'rss'
    base_url        VARCHAR(500),
    config          JSONB,                           -- Scraper/API configuration
    schedule        VARCHAR(50),                     -- Cron expression
    is_active       BOOLEAN DEFAULT TRUE,
    last_run_at     TIMESTAMPTZ,
    last_run_status VARCHAR(30),                     -- 'success', 'failed', 'running'
    error_count     INT DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 5.9 AI Agent Execution Logs

```sql
-- AI Agent Execution Logs
CREATE TABLE ai_execution_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name      VARCHAR(50) NOT NULL,
    task_type       VARCHAR(50) NOT NULL,            -- 'resume_optimize', 'match_score', etc.
    input_tokens    INT,
    output_tokens   INT,
    total_cost      DECIMAL(10,6),
    model           VARCHAR(50),
    provider        VARCHAR(30),
    duration_ms     INT,
    status          VARCHAR(20),                     -- 'success', 'failed', 'fallback'
    error_message   TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_ai_logs_agent ON ai_execution_logs(agent_name);
CREATE INDEX idx_ai_logs_created ON ai_execution_logs(created_at DESC);
```

---

## 6. API Design

### 6.1 API Gateway Configuration

- **Base URL:** `https://api.career-platform.com/api/v1`
- **Authentication:** JWT Bearer tokens (via Auth Service)
- **Rate Limiting:** 100 req/min per user (standard), 1000 req/min (premium)
- **Response Envelope:**

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150
  },
  "errors": null
}
```

### 6.2 Error Response Format

```json
{
  "success": false,
  "data": null,
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### 6.3 API Versioning

- URL-based versioning: `/api/v1/`, `/api/v2/`
- Deprecation headers: `X-API-Deprecated: true`, `X-API-Sunset: <date>`

---

## 7. Workflow Pipelines

### 7.1 Full Application Pipeline

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Profile  │───▶│ Job      │───▶│ Match    │───▶│ Resume   │
│ Created  │    │ Scraped  │    │ Found    │    │ Generated│
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                     │
                                                     ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Email    │◀───│ Package  │◀───│ Cover    │◀───│ ATS      │
│ Sent     │    │ Built    │    │ Letter   │    │ Optimized│
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │
     ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│ Tracked  │───▶│ Analytics│───▶│ Notify   │
│ (Live)   │    │ Computed │    │ User     │
└──────────┘    └──────────┘    └──────────┘
```

### 7.2 Event-Driven Workflow (Async via Queue)

**Trigger Events & Handlers:**

| Trigger Event | Emitted By | Handled By | Result |
|---------------|------------|------------|--------|
| `profile.created` | Profile Service | Resume Service | Generate master resume |
| `job.scraped` | Job Service | Match Service | Compute matches for all active profiles |
| `match.found` | Match Service | Notification Service | Alert user of new match |
| `match.high_score` | Match Service | Application Service | Auto-create application draft |
| `application.draft_created` | Application Service | Resume Service | Generate ATS-optimized resume |
| `resume.generated` | Resume Service | Application Service | Update application state |
| `resume.generated` | Resume Service | Outreach Service | Generate cover letter |
| `cover_letter.generated` | Outreach Service | Application Service | Prepare email, build package |
| `package.ready` | Application Service | Delivery Service | Send email with attachments |
| `email.sent` | Delivery Service | Tracking Service | Update tracking dashboard |
| `email.delivered` | Email Webhook | Application Service | Update application status |
| `email.opened` | Email Webhook | Application Service | Update application status |
| `email.replied` | Email Webhook | Application Service | Update status, notify user |

### 7.3 Scheduled Job Scraping Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                    Scheduler (Celery Beat)               │
│                                                         │
│  Every 30 min  ───▶  Scrape Naukri                      │
│  Every 60 min  ───▶  Scrape Wellfound                   │
│  Every 30 min  ───▶  Scrape RemoteOK                    │
│  Every 120 min ───▶  Scrape Company Career Pages        │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                    Job Scraper Workers                    │
│                                                         │
│  1. Fetch raw page/API response                         │
│  2. Parse & normalize into job schema                   │
│  3. Deduplicate against existing jobs                   │
│  4. Upsert into jobs table                              │
│  5. Emit job.scraped event                              │
└─────────────────────────────────────────────────────────┘
```

---

## 8. AI Agent Architecture

### 8.1 Agent Orchestration Pattern

```
┌──────────────┐
│  Request      │  User action or system event triggers AI task
│  (Task +      │
│   Context)    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                AI Orchestrator Service                    │
│                                                          │
│  1. Select Agent (Resume Optimizer, Match Engine, etc.)  │
│  2. Build Prompt from template + context                 │
│  3. Trim context to fit model window                     │
│  4. Call LLM provider (with fallback chain)              │
│  5. Parse & validate structured response                 │
│  6. Log execution (tokens, cost, duration)               │
│  7. Return structured result                             │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│  Structured   │  JSON response consumed by calling service
│  Result       │
└──────────────┘
```

### 8.2 Prompt Template Architecture

Templates are stored as Jinja2 files with variable injection:

```
ai/prompts/
├── resume_optimizer/
│   ├── ats_optimization.j2
│   ├── keyword_extraction.j2
│   └── resume_scoring.j2
├── job_matcher/
│   ├── match_scoring.j2
│   ├── skill_gap_analysis.j2
│   └── recommendation.j2
├── outreach/
│   ├── cover_letter.j2
│   ├── email_generation.j2
│   └── personalization.j2
└── career_intelligence/
    ├── skill_recommendation.j2
    └── interview_questions.j2
```

### 8.3 LLM Provider Abstraction

```python
# Abstract interface for LLM providers
class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, model: str, **kwargs) -> LLMResponse: ...

class GeminiProvider(LLMProvider): ...      # Google Gemini API via google-genai SDK

# Provider configuration — Gemini as primary provider
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_DEFAULT_MODEL = "gemini-2.0-flash"   # Fast, cost-effective for most tasks
GEMINI_PRO_MODEL = "gemini-1.5-pro"          # Heavy reasoning tasks
```

> **Note:** Gemini API requires a free API key from [Google AI Studio](https://aistudio.google.com/). The free tier includes generous rate limits suitable for development and personal use. Upgrade to pay-as-you-go for higher production limits.

### 8.4 Structured Output Parsing

All AI agents return structured JSON. The orchestrator validates against Pydantic schemas:

```python
class ResumeOptimizationResult(BaseModel):
    optimized_sections: list[Section]
    keywords_added: list[str]
    ats_score: float
    changes_summary: str

class MatchScoreResult(BaseModel):
    overall_score: float
    skill_match_score: float
    experience_match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    strength_areas: list[str]
    recommendation: str
```

---

## 9. Technology Stack

### 9.1 Backend

| Technology | Purpose | Justification |
|------------|---------|---------------|
| **FastAPI** | API Framework | Async-first, automatic OpenAPI docs, Pydantic integration, high performance |
| **Python 3.12+** | Runtime | Rich AI/ML ecosystem, async support, broad library support |
| **SQLAlchemy 2.0** | ORM | Mature, async support, migrations via Alembic |
| **Alembic** | Migrations | Industry standard for Python DB migrations |
| **Celery** | Task Queue | Distributed task processing, beat scheduler, result backend |
| **Redis** | Cache + Broker | Fast in-memory cache, Celery broker, rate limiting counters |
| **Pydantic v2** | Validation | Schema validation, settings management, serialization |
| **httpx** | HTTP Client | Async HTTP for LLM providers and external APIs |

### 9.2 AI / ML

| Technology | Purpose | License |
|------------|---------|---------|
| **Google Gemini API** | Primary LLM provider (gemini-2.0-flash, gemini-1.5-pro) via google-genai SDK | Free tier available / Pay-as-you-go |
| **google-genai** | Official Google GenAI Python SDK for Gemini API access | Apache 2.0 |
| **LangChain / LlamaIndex** | Prompt management, chain building (optional, evaluate) | MIT |
| **Sentence-Transformers** | Embedding generation for semantic matching | Apache 2.0 |
| **Qdrant** | Vector database for semantic job search (future) — self-hosted | Apache 2.0 |
| **Weaviate** | Vector database alternative — self-hosted | BSD-3-Clause |

### 9.3 Frontend

| Technology | Purpose |
|------------|---------|
| **React 18+** | UI Framework |
| **TypeScript** | Type safety |
| **Tailwind CSS** | Styling |
| **React Query** | Server state management |
| **React Router v6** | Routing |
| **Vite** | Build tool |
| **React PDF** | PDF preview rendering |

### 9.4 Database & Storage

| Technology | Purpose |
|------------|---------|
| **PostgreSQL 16** | Primary database (SSOT) |
| **Redis 7** | Caching, session store, rate limiting |
| **Celery + Redis** | Task queue |
| **MinIO** | File storage (PDFs, templates, assets) — S3-compatible, self-hosted |
| **Alembic** | Database migrations |

### 9.5 Infrastructure & DevOps

| Technology | Purpose | License |
|------------|---------|---------|
| **Docker** | Containerization | Apache 2.0 |
| **Docker Compose** | Local development orchestration | Apache 2.0 |
| **Kubernetes** | Production orchestration (future) | Apache 2.0 |
| **Traefik / Nginx** | Reverse proxy, API gateway | MIT / BSD-2-Clause |
| **Prometheus + Grafana** | Monitoring & metrics | Apache 2.0 / AGPLv3 |
| **Loki + Grafana** | Log aggregation | AGPLv3 |
| **PgBouncer** | PostgreSQL connection pooling | ISC

### 9.6 Email Delivery

| Technology | Purpose | License |
|------------|---------|---------|
| **SMTP** | Direct SMTP delivery (simple, no extra service needed) | Built-in |
| **Postal** | Self-hosted transactional email server with web UI, bounce handling, delivery logs | MIT |
| **Mailcow** | Full self-hosted email server stack (Docker-based) | GPLv3 |
| **Maddy** | Lightweight composable mail server | MIT |
| **Plunk** | Self-hosted transactional email platform with Resend-like API | AGPLv3 |
| **Gmail API** | Gmail integration (optional, user's own account) | Free API |
| **Microsoft Graph API** | Outlook integration (optional, user's own account) | Free API |

> **Note:** All email delivery options listed are either open-source (Postal, Mailcow, Maddy, Plunk) or free APIs (Gmail, Outlook). For maximum freedom and zero vendor lock-in, start with **Postal** (self-hosted transactional engine) or direct **SMTP** delivery. The Gmail/Outlook APIs are **optional** proprietary integrations for users who want to send from their personal accounts — the platform works fully without them.

---

### 9.7 License Summary

All technologies in the stack are free and open-source. None require paid subscriptions or API keys to function.

| Category | Technologies | License Type |
|----------|-------------|--------------|
| **Backend Runtime** | Python 3.12+, FastAPI, SQLAlchemy, Celery, Pydantic | PSF / MIT / Apache 2.0 |
| **Databases** | PostgreSQL, Redis, SQLite (dev), Qdrant | PostgreSQL / BSD-3-Clause / Apache 2.0 |
| **AI / ML** | Google Gemini API, google-genai SDK, Sentence-Transformers | Apache 2.0 / Free tier |
| **Storage** | MinIO (S3-compatible), Local Filesystem | AGPLv3 / None |
| **Frontend** | React, TypeScript, Tailwind CSS, Vite | MIT |
| **Infrastructure** | Docker, Nginx, Traefik, Prometheus, Grafana, Loki | Apache 2.0 / MIT / AGPLv3 |
| **Email** | Postal, Mailcow, Maddy, SMTP | MIT / GPLv3 / None |
| **Queue** | Celery + Redis (self-hosted) | BSD-3-Clause / BSD-3-Clause |
| **Auth** | JWT (PyJWT), bcrypt (passlib), OAuth2 libraries | MIT / BSD-3-Clause

---

### 14.4 Environment & Secrets Management

Environment variables are managed per-environment using a layered strategy:

| Environment | Config Method | Secrets Storage |
|-------------|--------------|----------------|
| **Local Dev** | `.env` files (local, not committed) | `.env` file, `.env.example` as template |
| **CI/CD** | GitHub Actions secrets / environment files | Encrypted GitHub secrets |
| **Staging** | Docker Compose `.env` files | Separate `.env.staging`, injected at deploy |
| **Production** | Kubernetes Secrets or Vault | HashiCorp Vault / Kubernetes External Secrets Operator |

**Key secrets managed:**
- Database credentials (PostgreSQL, Redis)
- Email provider credentials (SMTP)
- JWT signing secret
- Encryption keys (for PII)
- Optional OAuth2 client IDs (Gmail, Outlook, LinkedIn)

> **Note:** AI inference uses Google Gemini API (free tier available). Email can be delivered entirely via self-hosted SMTP/Postal.

---

## 10. Directory Structure

```
career-platform/
│
├── backend/
│   ├── profile_service/         # Profile Service
│   │   ├── app/
│   │   │   ├── api/             # Route handlers
│   │   │   ├── core/            # Config, dependencies
│   │   │   ├── models/          # SQLAlchemy models
│   │   │   ├── schemas/         # Pydantic schemas
│   │   │   ├── services/        # Business logic
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── alembic/             # Migrations
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── resume_service/          # Resume Service
│   ├── job_service/             # Job Service (scraping + storage)
│   ├── match_service/           # Match Service
│   ├── outreach_service/        # Outreach Service
│   ├── application_service/     # Application Service
│   ├── tracking_service/        # Tracking Service
│   ├── ai_orchestrator/         # AI Orchestrator Service
│   │   ├── app/
│   │   │   ├── agents/          # Agent implementations
│   │   │   ├── providers/       # LLM provider abstractions
│   │   │   ├── prompts/         # Jinja2 prompt templates
│   │   │   ├── schemas/         # Input/output schemas
│   │   │   └── main.py
│   │   ├── tests/
│   │   └── Dockerfile
│   │
│   ├── notification_service/    # Notification Service
│   ├── shared/                  # Shared libraries
│   │   ├── models/              # Shared DB models
│   │   ├── schemas/             # Shared Pydantic schemas
│   │   ├── utils/               # Common utilities
│   │   └── config/              # Base configuration
│   │
│   ├── docker-compose.yml
│   └── Makefile
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API client services
│   │   ├── hooks/               # Custom hooks
│   │   ├── stores/              # State management
│   │   ├── types/               # TypeScript types
│   │   └── utils/               # Utilities
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
│
├── docs/
│   ├── architecture.md          # This document
│   ├── problemStatement.md      # Original problem statement
│   ├── api-reference.md         # Full API documentation
│   └── setup.md                 # Development setup guide
│
├── scripts/
│   ├── setup.sh                 # Initial setup script
│   ├── seed_data.py             # Database seeding
│   └── migrate.sh               # Migration helper
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml               # CI pipeline
│   │   └── deploy.yml           # Deployment pipeline
│   └── CODEOWNERS
│
├── .env.example
├── .gitignore
├── README.md
└── docker-compose.yml           # Root compose (all services)
```

### 10.1 Internal Structure Per Service

Each microservice follows a consistent internal structure:

```
service_name/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app initialization
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py            # Route aggregation
│   │   ├── v1/                  # Versioned endpoints
│   │   │   ├── __init__.py
│   │   │   ├── endpoints.py
│   │   │   └── dependencies.py  # Depends (auth, DB session)
│   │   └── deps.py              # Shared dependencies
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Pydantic Settings
│   │   ├── database.py          # DB engine & session
│   │   ├── logging.py           # Logging configuration
│   │   └── events.py            # Event publishers/consumers
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py            # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── request.py           # Request schemas
│   │   └── response.py          # Response schemas
│   └── services/
│       ├── __init__.py
│       └── service.py           # Business logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   └── test_services.py
├── Dockerfile
├── requirements.txt
└── alembic/                     # (If service has its own DB)
```

---

## 11. Queue & Task Processing

### 11.1 Queue Architecture

```
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Celery Beat   │    │  Celery       │    │  Celery       │
│  (Scheduler)   │───▶│  Broker       │───▶│  Workers      │
│                │    │  (Redis)      │    │               │
│ Generates      │    │               │    │ Consume tasks │
│ periodic tasks │    │ Task queue    │    │ Emit events   │
└───────────────┘    └───────────────┘    └───────────────┘
```

### 11.2 Task Definitions

| Task | Queue | Retry Policy | Description |
|------|-------|-------------|-------------|
| `scrape_jobs` | `jobs` | 3 retries, 5min delay | Scrape a job source |
| `generate_resume` | `resumes` | 2 retries, 1min delay | Generate resume PDF |
| `generate_cover_letter` | `outreach` | 2 retries, 1min delay | Generate cover letter |
| `send_application` | `delivery` | 5 retries, exponential backoff | Send application email |
| `compute_matches` | `matches` | 2 retries, 1min delay | Batch match computation |
| `optimize_resume_ats` | `ai` | 2 retries, 30s delay | ATS optimization via AI |

### 11.3 Celery Configuration

```python
# celery_config.py
from celery import Celery

celery_app = Celery(
    "career_platform",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
    include=[
        "job_service.tasks",
        "resume_service.tasks",
        "outreach_service.tasks",
        "application_service.tasks",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,           # Re-deliver if worker dies
    worker_prefetch_multiplier=1,  # One task at a time per worker
    task_default_retry_delay=60,   # Default retry delay (seconds)
    task_max_retries=3,             # Default max retries
    beat_schedule={
        "scrape-naukri-every-30min": {
            "task": "job_service.tasks.scrape_jobs",
            "schedule": crontab(minute="*/30"),
            "args": ("naukri",),
        },
        "scrape-wellfound-every-60min": {
            "task": "job_service.tasks.scrape_jobs",
            "schedule": crontab(minute="0 *"),
            "args": ("wellfound",),
        },
        "scrape-remoteok-every-30min": {
            "task": "job_service.tasks.scrape_jobs",
            "schedule": crontab(minute="*/30"),
            "args": ("remoteok",),
        },
        "compute-matches-every-15min": {
            "task": "match_service.tasks.compute_new_matches",
            "schedule": crontab(minute="*/15"),
        },
    },
)
```

---

## 12. Storage Strategy

### 12.1 File Storage

| Asset Type | Storage | Path Pattern | Retention |
|------------|---------|-------------|-----------|
| Resume PDFs | MinIO | `resumes/{profile_id}/{resume_id}.pdf` | Indefinite |
| Cover Letters | MinIO | `cover-letters/{profile_id}/{letter_id}.pdf` | Indefinite |
| Profile Avatars | MinIO | `avatars/{profile_id}/avatar.jpg` | Indefinite |
| Resume Templates | Git + MinIO | `templates/{template_id}/layout.json` | Versioned |
| Application Logs | PostgreSQL | `email_delivery_logs` table | 90-day retention |
| Scraping Artifacts | MinIO | `scraping/{source}/{job_id}.html` | 7-day retention |

### 12.2 Caching Strategy

| Cache | Type | TTL | Used By |
|-------|------|-----|---------|
| Profile Data | Redis | 5 min | All services |
| Job Listings (frequently accessed) | Redis | 15 min | Job Service |
| Match Scores (recent) | Redis | 30 min | Match Service |
| API Rate Limit Counters | Redis | 1 min | API Gateway |
| Session Tokens | Redis | Session TTL | Auth Service |
| Scraping Dedup Set | Redis | 7 days | Job Service |
| Celery Result Backend | Redis | 1 day | All workers |

---

## 13. Integration Patterns

### 13.1 Inter-Service Communication

```
┌──────────────┐         ┌──────────────┐
│  Service A   │ ──HTTP──▶  Service B   │  Synchronous (read queries)
└──────────────┘         └──────────────┘

┌──────────────┐         ┌──────────────┐
│  Service A   │ ──Event──▶  Service B   │  Async (state changes)
│  (Publisher) │          │  (Consumer)  │
└──────────────┘         └──────────────┘
```

- **Synchronous:** HTTP REST calls for read queries (e.g., Profile Service → Resume Service for profile data)
- **Asynchronous:** Celery tasks / Redis pub-sub for event-driven workflows (e.g., Job scraped → Match computation)
- **No direct DB sharing:** Services communicate only via APIs and events

### 13.2 Email Provider Abstraction

```python
class EmailProvider(ABC):
    @abstractmethod
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        attachments: list[Attachment],
    ) -> DeliveryResult: ...

    @abstractmethod
    async def check_delivery_status(self, message_id: str) -> DeliveryStatus: ...

class SMTPProvider(EmailProvider): ...
class GmailProvider(EmailProvider): ...
class OutlookProvider(EmailProvider): ...
```

### 13.3 Webhook Integration

Email providers can send delivery webhooks:

```
POST /api/v1/webhooks/gmail
POST /api/v1/webhooks/outlook
POST /api/v1/webhooks/sendgrid
```

Webhooks update application status automatically (delivered, opened, replied, bounced).

---

## 14. Security Architecture

### 14.1 Auth Service

A dedicated **Auth Service** handles all identity and access management as a first-class microservice.

**Responsibilities:**
- User registration & login (email/password, OAuth2 providers)
- JWT token issuance, refresh, and revocation
- API key management for service-to-service auth
- Password hashing (bcrypt via passlib) & recovery flows
- OAuth2 flows for Gmail, Outlook, LinkedIn integrations

**Auth Service Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | User registration |
| POST | `/api/v1/auth/login` | Login, returns JWT pair (access + refresh) |
| POST | `/api/v1/auth/refresh` | Refresh token rotation |
| POST | `/api/v1/auth/logout` | Invalidate refresh token |
| POST | `/api/v1/auth/oauth/{provider}` | OAuth2 initiation (Google, Microsoft, LinkedIn) |
| GET | `/api/v1/auth/oauth/{provider}/callback` | OAuth2 callback handler |

**Token Design:**
| Token | Lifetime | Storage | Purpose |
|-------|----------|---------|---------|
| Access JWT | 15 min | Memory (HTTP-only cookie or Auth header) | API authorization |
| Refresh JWT | 7 days | HTTP-only cookie | Obtain new access tokens |
| Service API Key | 1 year (rotatable) | Environment / Vault | Service-to-service calls |

**Auth Database Tables:**
```sql
-- Users (auth service owns this)
CREATE TABLE auth_users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    email_verified  BOOLEAN DEFAULT FALSE,
    mfa_enabled     BOOLEAN DEFAULT FALSE,
    mfa_secret      VARCHAR(100),
    role            VARCHAR(20) NOT NULL DEFAULT 'user',  -- 'user', 'admin', 'service'
    is_active       BOOLEAN DEFAULT TRUE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- OAuth connections
CREATE TABLE auth_oauth_connections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth_users(id) ON DELETE CASCADE,
    provider        VARCHAR(50) NOT NULL,  -- 'google', 'microsoft', 'linkedin'
    provider_user_id VARCHAR(255) NOT NULL,
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    token_expiry    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider, provider_user_id)
);

-- API keys for service-to-service
CREATE TABLE auth_api_keys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name    VARCHAR(100) NOT NULL,
    key_hash        VARCHAR(255) NOT NULL,
    permissions     TEXT[],
    expires_at      TIMESTAMPTZ,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

**Auth Flow:**
```
User Login → Auth Service validates credentials
           → Issues access JWT (15min) + refresh JWT (7d)
           → All subsequent API calls include access JWT
           → API Gateway validates JWT before proxying to services
            → If expired, client uses refresh JWT to get new access JWT
```

### 14.2 Data Security

- **PII Encryption:** Personal data encrypted at rest (AES-256)
- **HTTPS Only:** TLS 1.3 for all external communication
- **Email Credentials:** Stored encrypted, injected via environment variables
- **LLM Model Paths:** Model paths stored in environment configuration, never hardcoded
- **External AI Provider:** AI inference uses Google Gemini API — requires a Gemini API key (free tier available from Google AI Studio)

### 14.3 API Security

- **Rate Limiting:** Per-user and per-IP rate limiting (Redis-backed sliding window)
- **AI API Rate Limits:** AI Orchestrator implements concurrency limits and request queuing to respect Gemini API rate limits and prevent quota exhaustion
- **CORS:** Restricted to known origins
- **Input Validation:** Pydantic schema validation on all endpoints
- **SQL Injection Protection:** SQLAlchemy parameterized queries
- **Database Connection Pooling:** PgBouncer for production PostgreSQL connection pooling across multiple service instances
- **Request Size Limits:** Configurable max body size

---

## 15. Deployment Architecture

### 15.1 Local Development

```yaml
# docker-compose.yml (local)
services:
  postgres:        # PostgreSQL 16
  redis:           # Redis 7
  minio:           # S3-compatible storage
  profile-api:     # Profile Service
  resume-api:      # Resume Service
  job-api:         # Job Service
  match-api:       # Match Service
  outreach-api:    # Outreach Service
  application-api: # Application Service
  tracking-api:    # Tracking Service
  ai-orchestrator: # AI Orchestrator
  celery-worker:   # Celery worker (all queues)
  celery-beat:     # Celery beat scheduler
  frontend:        # React dev server
  nginx:           # Reverse proxy
```

### 15.2 Production (Kubernetes — Future)

```
┌─────────────────────────────────────────────┐
│           Kubernetes Cluster                  │
│                                              │
│  ┌─────────────┐  ┌─────────────┐           │
│  │ Ingress      │  │             │           │
│  │ Controller   │──│ Auth Proxy  │           │
│  └─────────────┘  └─────────────┘           │
│         │                                    │
│         ▼                                    │
│  ┌──────────────────────────────────┐        │
│  │         Service Mesh             │        │
│  │      (Istio / Linkerd)           │        │
│  └──────────────────────────────────┘        │
│         │                                    │
│         ▼                                    │
│  ┌──────────────────────────────────┐        │
│  │   Pods (horizontally scaled)     │        │
│  │   - profile-service (x3)         │        │
│  │   - resume-service (x3)          │        │
│  │   - job-service (x5)             │        │
│  │   - match-service (x3)           │        │
│  │   - outreach-service (x2)        │        │
│  │   - application-service (x3)     │        │
│  │   - ai-orchestrator (x5)         │        │
│  └──────────────────────────────────┘        │
│                                              │
│  ┌──────────────────────────────────┐        │
│  │   StatefulSets                    │        │
│  │   - PostgreSQL (Primary + Replica)│        │
│  │   - Redis Cluster                 │        │
│  │   - MinIO (distributed)           │        │
│  └──────────────────────────────────┘        │
│                                              │
│  ┌──────────────────────────────────┐        │
│  │   Celery Worker Pools             │        │
│  │   - jobs queue (x5)               │        │
│  │   - resumes queue (x3)            │        │
│  │   - outreach queue (x2)           │        │
│  │   - delivery queue (x3)           │        │
│  │   - ai queue (x10)                │        │
│  └──────────────────────────────────┘        │
└─────────────────────────────────────────────┘
```

---

## 16. Monitoring & Observability

### 16.1 Logging

- **Structure:** JSON structured logging (via structlog or python-json-logger)
- **Level:** INFO in production, DEBUG in development
- **Fields:** `service`, `trace_id`, `user_id`, `duration_ms`, `status_code`
- **Aggregation:** Loki + Grafana (or ELK stack)

### 16.2 Metrics (Prometheus)

**Service-Level Metrics:**
- `http_requests_total` (method, path, status)
- `http_request_duration_seconds` (histogram)
- `service_errors_total` (error type)
- `task_queue_depth` (per queue)
- `task_processing_duration_seconds` (per task type)
- `ai_tokens_consumed_total` (per agent, per model)
- `ai_cost_total` (per agent)

**Business Metrics:**
- `applications_created_total`
- `applications_sent_total`
- `applications_by_status`
- `jobs_scraped_total` (per source)
- `match_scores_distribution`
- `resume_generations_total`
- `emails_delivered_total`
- `emails_opened_total`
- `emails_bounced_total`

### 16.3 Distributed Tracing

- **Tool:** OpenTelemetry
- **Traces:** End-to-end request flow across services
- **Sampling:** 100% for errors, 10% for successful requests (adjustable)
- **Propagation:** W3C Trace Context via HTTP headers

### 16.4 Alerting

| Alert | Condition | Severity |
|-------|-----------|----------|
| High error rate | >5% error rate over 5 min | Critical |
| Queue backlog | >1000 tasks in a queue for >10 min | Warning |
| Scraper failure | >3 consecutive failures for any source | Warning |
| AI cost spike | >2x normal hourly cost | Info |
| Delivery failure | >10% bounce rate in 1 hour | Critical |
| Service down | Endpoint returning 5xx for >1 min | Critical |

---

## 17. Phase Roadmap

| Phase | Features | Dependencies |
|-------|----------|-------------|
| **P1: Foundation** | User profile CRUD, master resume generation, PDF export, basic dashboard | PostgreSQL, Redis, FastAPI, React |
| **P2: Job Discovery** | Job scraping (Naukri, Wellfound, RemoteOK), job storage, job listing UI | Job Service, Scraper infrastructure |
| **P3: AI Matching** | Match score computation, skill gap analysis, match recommendation UI | AI Orchestrator, Match Service |
| **P4: ATS Optimization** | ATS keyword extraction, resume optimization, ATS score display | AI Orchestrator, Resume Service |
| **P5: Application Pipeline** | Cover letter generation, email generation, application package assembly | Outreach Service, Application Service |
| **P6: Email Delivery** | SMTP/Gmail/Outlook integration, resume attachment, delivery tracking | Delivery Service, Email Providers |
| **P7: Tracking Dashboard** | Application lifecycle pipeline, analytics, notifications, timeline view | Tracking Service, Notification Service |
| **P8: Automation & Scale** | One-click apply, batch apply, Celery worker scaling, performance optimization | All services |
| **P9: Career Intelligence** | Missing skill detection, career path recommendations, interview prep | AI Orchestrator (Career Intelligence Agent) |
| **P10: Browser Agent** | Automated form filling on job portals, auto-apply | Browser automation framework |

---

## 18. Success Metrics

### 18.1 Business KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Applications sent per day per user | 10+ | Tracking dashboard |
| Interview conversion rate | >5% | Application events |
| Resume generation speed | <30 seconds | AI execution logs |
| ATS score improvement | >20% | Before/after comparison |
| Time saved per user per week | >10 hours | User surveys + analytics |

### 18.2 Technical KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Job matching accuracy (precision@10) | >85% | User feedback + A/B testing |
| Email delivery success rate | >98% | Delivery logs |
| Resume generation latency (p95) | <60 seconds | Prometheus histograms |
| Job scraping coverage (unique jobs/day) | >10,000 | Job service metrics |
| Platform uptime | 99.9% | Monitoring |
| AI cost per application | <$0.10 | AI execution logs |
| Queue processing latency (p95) | <5 seconds | Celery monitoring |

---

## 19. Appendices

### A. Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Monorepo vs Polyrepo | Monorepo | Easier coordination, shared models, single CI |
| Async vs Sync tasks | Celery (async) | Distributed processing, retries, scheduling |
| Microservices vs Monolith | Microservices | Independent scaling, team ownership, fault isolation |
| REST vs GraphQL | REST (initially) | Simpler, cacheable, universal client support |
| SQL vs NoSQL for profile | PostgreSQL | Strong schema, relations, JSONB for flexibility |
| File storage | MinIO | S3-compatible, fully self-hosted, no AWS dependency |
| LLM provider choice | Google Gemini API | Google's foundation models — fast, cost-effective, generous free tier; google-genai SDK for easy integration |

### B. Error Handling Strategy

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Retry    │────▶│ Fallback │────▶│ Dead     │
│ (3x)     │     │ (Alt LLM)│     │ Letter   │
└──────────┘     └──────────┘     └──────────┘
                                       │
                                       ▼
                                 ┌──────────┐
                                 │ Alert    │
                                 │ (Manual  │
                                 │ Review)  │
                                 └──────────┘
```

### C. Glossary

| Term | Definition |
|------|------------|
| **SSOT** | Single Source of Truth — the central user profile |
| **ATS** | Applicant Tracking System — software used by employers to filter resumes |
| **Celery Beat** | Scheduler that triggers periodic tasks |
| **Celery Worker** | Worker process that executes queued tasks |
| **Application Package** | Assembled set of resume PDF + cover letter + email |
| **Job Match Score** | Numerical score (0-100) indicating profile-job fit |
| **AI Agent** | Specialized AI module that performs a specific career task |

---

> **Document Version:** 1.0  
> **Author:** Architecture Team  
> **Last Updated:** June 11, 2026  
> **Next Review:** Phase 1 completion
