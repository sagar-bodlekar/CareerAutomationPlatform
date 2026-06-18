# Problem Statement 
# Unified System Architecture

## Project Vision

Build a complete AI-powered Career Automation Platform by combining three existing projects:

1. ResumeBuilder
2. Job-Agent
3. Cover-Mailer

The platform should function as an intelligent career operating system that automates the entire job application lifecycle from profile creation to interview preparation.

The objective is to eliminate repetitive manual work involved in job searching, resume customization, cover letter generation, email outreach, and application tracking.

---

# Existing Systems

## ResumeBuilder

Responsible for:

* User profile management
* Resume creation
* Resume template management
* PDF generation
* Skills and experience management
* Structured resume data generation

---

## Job-Agent

Responsible for:

* Job discovery
* Job scraping
* Job aggregation
* Job filtering
* Match analysis
* Job export and storage

Sources may include:

* Naukri
* Wellfound
* RemoteOK
* Company Career Pages
* Additional job sources

---

## Cover-Mailer

Responsible for:

* Cover letter generation
* Personalized email generation
* Automated outreach
* Email delivery
* Application communication

---

# Core Problem

Current job application workflows are fragmented.

Candidates must:

* Search jobs manually
* Maintain multiple resumes
* Modify resumes for every application
* Create custom cover letters
* Attach documents manually
* Send emails manually
* Track applications manually

This process is slow, repetitive, error-prone, and difficult to scale.

---

# Proposed Solution

Create a unified AI-driven platform where all career-related activities operate from a single profile and data source.

The platform should automate:

* Job discovery
* Job matching
* Resume optimization
* Resume generation
* Cover letter generation
* Email generation
* Resume attachment
* Application delivery
* Application tracking

---

# Single Source of Truth (SSOT)

The ResumeBuilder profile becomes the central data model for the entire platform.

All modules consume the same structured profile.

Example:

```json
{
  "personalInfo": {},
  "skills": [],
  "experience": [],
  "education": [],
  "projects": [],
  "certifications": [],
  "socialLinks": []
}
```

Every system reads from this profile.

No duplicate data management should exist.

---

# Unified System Architecture

```
                     +------------------+
                     | User Profile     |
                     | (SSOT Database)  |
                     +------------------+
                              |
                              |
          +-------------------+-------------------+
          |                                       |
          v                                       v

 +------------------+                  +------------------+
 | Resume Builder   |                  | Job Agent        |
 +------------------+                  +------------------+
          |                                       |
          |                                       |
          +---------------+-----------------------+
                          |
                          v

                +---------------------+
                | Job Match Engine    |
                +---------------------+
                          |
                          v

                +---------------------+
                | ATS Optimizer       |
                +---------------------+
                          |
                          v

                +---------------------+
                | Resume Generator    |
                +---------------------+
                          |
                          v

                +---------------------+
                | Cover Mailer        |
                +---------------------+
                          |
                          v

                +---------------------+
                | Application Package |
                +---------------------+
                          |
                          v

                +---------------------+
                | Email Delivery      |
                +---------------------+
                          |
                          v

                +---------------------+
                | Tracking Dashboard  |
                +---------------------+
```

---

# End-to-End Workflow

## Step 1: User Profile Creation

User creates:

* Personal information
* Skills
* Work experience
* Education
* Projects
* Certifications
* Social links

The platform stores all information in a structured schema.

---

## Step 2: Master Resume Creation

System generates:

* Master Resume
* ATS Resume
* Structured Resume Dataset

This becomes the foundation for future resume variations.

---

## Step 3: Automated Job Discovery

Job-Agent continuously searches jobs based on:

* Preferred roles
* Skills
* Experience
* Locations
* Remote preferences

Jobs are collected and normalized into a central database.

---

## Step 4: AI Job Matching

The system compares:

* Candidate profile
* Resume content
* Skills
* Experience

against

* Job description
* Required skills
* Preferred qualifications

Output:

* Match score
* Missing skills
* Strength areas
* Recommendation score

---

## Step 5: ATS Resume Optimization

For every high-scoring job:

The AI system:

* Extracts keywords
* Identifies ATS requirements
* Optimizes content
* Reorders relevant experience
* Improves ATS compatibility

---

## Step 6: Dynamic Resume Generation

The system generates role-specific resumes.

Examples:

* Frontend Resume
* Backend Resume
* Full Stack Resume
* Python Resume
* AI Engineer Resume
* DevOps Resume

Generated as PDF automatically.

---

## Step 7: Personalized Cover Letter Generation

Using:

* Resume data
* User profile
* Job description
* Company information

The AI generates:

* Cover Letter
* Personalized Application Content
* Recruiter-specific messaging

---

## Step 8: Application Package Generation

The platform automatically creates:

Application Package

* ATS Optimized Resume PDF
* Cover Letter
* Email Content
* Application Metadata

No manual document preparation required.

---

## Step 9: Automated Resume Attachment

The generated resume PDF is automatically attached to the application email.

Flow:

Generate Resume PDF
→ Generate Cover Letter
→ Generate Email
→ Attach Resume
→ Send Application

The user should never need to manually download and attach files.

---

## Step 10: Email Delivery

The platform sends applications through:

* SMTP
* Gmail Integration
* Outlook Integration
* Custom Email Providers

Delivery logs must be stored.

---

## Step 11: Application Tracking

Every application enters a lifecycle pipeline.

States:

Draft
→ Matched
→ Resume Generated
→ Cover Letter Generated
→ Email Prepared
→ Sent
→ Delivered
→ Opened
→ Replied
→ Interview Scheduled
→ Offer Received
→ Rejected

Users can monitor all activities from a dashboard.

---

# AI Components

## Resume Optimization Agent

Responsibilities:

* ATS optimization
* Keyword extraction
* Resume scoring
* Resume tailoring

---

## Job Matching Agent

Responsibilities:

* Match score generation
* Skill gap detection
* Recommendation engine

---

## Outreach Agent

Responsibilities:

* Cover letter generation
* Email generation
* Recruiter personalization

---

## Career Intelligence Agent

Responsibilities:

* Missing skill detection
* Career recommendations
* Resume improvement suggestions
* Interview preparation guidance

---

# Technical Requirements

## Backend (All Free & Open-Source)

* **FastAPI** — Async-first Python web framework (MIT)
* **Python 3.12+** — Runtime (PSF License)
* REST APIs with automatic OpenAPI documentation
* Modular microservices architecture
* **Celery** — Async task queue (BSD-3-Clause)
* **SQLAlchemy 2.0** + **Alembic** — ORM and migrations (MIT)

---

## Database (All Free & Open-Source)

* **PostgreSQL** — Primary relational database (SSOT)
* **Redis** — Caching, queue broker, rate limiting
* **Qdrant** or **Weaviate** — Vector database for semantic job search (future) — self-hosted, Apache 2.0 / BSD-3-Clause

---

## Queue Processing (All Free & Open-Source)

Required for:

* Job scraping
* Resume generation
* Cover letter generation
* Email delivery

Recommended solution:

* **Celery** + **Redis** — Distributed task queue with beat scheduler, retry logic, and monitoring

> Celery is BSD-licensed and self-hosted. No paid queue services needed.

---

## Storage (All Free & Open-Source)

Store:

* Resume PDFs
* Generated Cover Letters
* Job Records
* Application History

Recommended solution:

* **MinIO** — S3-compatible object storage, fully self-hosted (AGPLv3)
* **Local Filesystem** — For development/testing

> No AWS S3 or paid cloud storage required. MinIO is fully compatible with the S3 API.

---

# Future Roadmap

## Phase 1

Unified Dashboard

## Phase 2

AI Job Matching

## Phase 3

ATS Optimization Engine

## Phase 4

Automated Application Package Generation

## Phase 5

One-Click Apply System

## Phase 6

Browser Automation Agent

## Phase 7

Interview Preparation Agent

## Phase 8

Career Copilot AI

## Phase 9 "Frontend Real Data Integration"

Replace all sample/mock data with live backend API calls:

- API service layer hardening & error handling
- Page-by-page mock data migration (Dashboard, Profile, Jobs, Resumes, Applications, Tracking, Notifications)
- Loading states & skeleton UI for every page
- Error states & retry mechanisms for every API call
- Empty states & onboarding CTAs for new users
- Mutation loading & success/error feedback
- Optimistic updates for instant UI feedback

## Phase 10 "Frontend Edge Case Hardening"

Fortify the frontend against edge cases:

- Error boundaries at route and section level
- Offline resilience with mutation queuing
- Stale data handling with cache invalidation
- Race condition mitigation (token refresh, double-submit, parallel requests)
- Token refresh queue & multi-tab session sync

## Phase 11 "Frontend Performance & Polish"

Optimize for production:

- Code splitting & lazy loading
- Virtual scrolling for large lists
- Bundle optimization & tree shaking
- Dark mode support
- Responsive design at all breakpoints
- Accessibility audit & keyboard navigation

## Phase 12 "Frontend Testing & QA"

Comprehensive test coverage:

- MSW integration tests for all pages
- Playwright E2E tests for critical paths
- Visual regression tests
- Mutation & optimistic update tests

---

# Technical Requirements

## Frontend (All Free & Open-Source)

| Technology | Purpose |
|------------|---------|
| **React 18+** | UI Framework |
| **TypeScript** | Type safety |
| **Tailwind CSS** | Styling |
| **React Query (TanStack Query)** | Server state management |
| **React Router v6** | Routing |
| **Vite** | Build tool |
| **Axios** | HTTP client |
| **React PDF** | PDF preview rendering |
| **vitest** | Unit & integration testing |
| **MSW** | API mocking for tests |
| **Playwright** | E2E testing |
| **react-window / @tanstack/virtual** | Virtual scrolling |
| **react-i18next** | Internationalization |
| **lucide-react** | Icons |

---

## Data Fetching Strategy

| Concern | Solution |
|---------|----------|
| Server state | React Query (`useQuery`, `useMutation`) — caching, dedup, refetch, pagination |
| Auth state | React Context — JWT tokens, user object, login/logout |
| UI state | React `useState`/`useReducer` — forms, modals, toggles |
| URL state | React Router `useSearchParams` — filters, pagination |
| Real-time updates | WebSocket (primary) → polling fallback (Phase 15) |
| Offline support | Service Worker + IndexedDB mutation queue (Phase 15) |

---

# Success Metrics

Business KPIs:

* Applications sent per day
* Interview conversion rate
* Resume generation speed
* ATS score improvement
* Time saved per user

Technical KPIs:

* Job matching accuracy
* Email delivery success rate
* Resume generation latency
* Queue processing performance
* Platform reliability

---

# Sample Data to Real Data Transition Challenge

## Current State

The frontend dashboard currently operates entirely on hardcoded sample/mock data.

Each page maintains its own dataset:

| Page | Mock Data Source | Problem |
|------|-----------------|---------|
| Dashboard | Hardcoded `recentActivity` array + static stat numbers | Stats never change, activity feed is fake |
| ProfilePage | Hardcoded `mockProfile` object | Cannot show real user data from backend |
| JobsPage | Hardcoded `mockJobs` array of 6 jobs | No real job scraping integration, filters don't work |
| ResumesPage | Hardcoded `mockResumes` array | Cannot generate or download real resumes |
| ApplicationsPage | Hardcoded `mockApps` array with fake statuses | No real application pipeline, status never updates |
| TrackingPage | Assumes data from mock applications | Charts show fake trends |

## The Transition Challenge

The frontend must transition from **demo-ready sample data** to **production-ready live data** through a careful, page-by-page migration.

### Key Challenges

**1. Contract Alignment**
- Frontend TypeScript types must match backend Pydantic schemas exactly
- API endpoint paths, HTTP methods, query parameters must align
- Response envelope (`ApiResponse<T>`) parsing must be consistent
- Backend may return fields not yet needed; frontend must handle gracefully

**2. Loading State Coverage**
- Every data-dependent component must show a loading skeleton while data fetches
- Every mutation (save, submit, generate) must show a loading spinner
- Transitions between loading → data → error must be smooth
- No content layout shift (CLS) during state transitions

**3. Error State Coverage**
- Every API call must handle: 400, 401, 403, 404, 409, 422, 429, 500, 503, network error, timeout
- Error messages must be user-friendly, not technical (e.g., not "Cannot read property 'name' of undefined")
- Failed mutations must roll back optimistic UI updates
- Offline state must be detected and communicated to user

**4. Empty State Coverage**
- New users with no profile data must see helpful onboarding CTAs
- No jobs matching filters → suggest broadening search
- No applications yet → guide user to find and apply to jobs
- No resumes yet → prompt user to generate their first resume
- No notifications → inform user they'll appear here

**5. Race Condition Prevention**
- Double-submit on application create/submit
- Token refresh race (multiple simultaneous API calls during refresh)
- Stale data after mutation (cache must be invalidated)
- Parallel requests partial failure (one fails, others succeed)

**6. Performance Constraints**
- Initial page load under 2 seconds (p95)
- Smooth scrolling with 1000+ items (virtual list)
- No unnecessary re-renders during data updates
- Bundle size under 200KB initial JS (gzipped)

---

# Frontend-Backend Contract Alignment

## Standard API Response Format

All backend endpoints return a consistent response envelope:

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

The frontend `api.ts` Axios client expects this envelope and parses it accordingly:

```typescript
// api.ts helper functions
export async function getList<T>(url: string, params?: Record<string, unknown>): Promise<PaginatedResponse<T>>
export async function getById<T>(url: string): Promise<T>
export async function createItem<T, R = T>(url: string, body: T): Promise<R>
export async function updateItem<T, R = T>(url: string, body: Partial<T>): Promise<R>
export async function postAction<R = unknown>(url: string, body?: unknown): Promise<R>
```

## Contract Verification Checklist

Each service must be verified against its frontend service file:

- [ ] Auth: `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/refresh`, `/api/v1/auth/logout`, `/api/v1/auth/me`
- [ ] Profiles: `/api/v1/profiles/{id}`, `/api/v1/profiles/{id}/export`, `/api/v1/profiles/{id}/import`, `/api/v1/profiles/{id}/analytics`
- [ ] Jobs: `/api/v1/jobs`, `/api/v1/jobs/{id}`, `/api/v1/jobs/refresh`, `/api/v1/jobs/sources`
- [ ] Resumes: `/api/v1/resumes`, `/api/v1/resumes/{id}/generate`, `/api/v1/resumes/{id}/download`, `/api/v1/resumes/{id}/optimize`, `/api/v1/resumes/templates`
- [ ] Matches: `/api/v1/matches/score`, `/api/v1/matches/recommendations/{profileId}`, `/api/v1/matches/gaps/{profileId}/{jobId}`
- [ ] Applications: `/api/v1/applications`, `/api/v1/applications/{id}/submit`, `/api/v1/applications/{id}/retry`, `/api/v1/applications/{id}/events`
- [ ] Outreach: `/api/v1/outreach/cover-letter`, `/api/v1/outreach/email`, `/api/v1/outreach/templates`
- [ ] Tracking: `/api/v1/tracking/stats`, `/api/v1/tracking/analytics`, `/api/v1/tracking/funnel`, `/api/v1/tracking/trends`, `/api/v1/tracking/export`
- [ ] Notifications: `/api/v1/notifications`, `/api/v1/notifications/unread/count`, `/api/v1/notifications/{id}/read`, `/api/v1/notifications/read-all`

---

# Frontend Integration Architecture

## Data Flow Pattern

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Page        │────▶│  Custom      │────▶│  Service     │
│  Component   │     │  Hook        │     │  Function    │
│              │     │              │     │              │
│ Renders UI   │     │ useQuery/    │     │ axios.get()  │
│ using data   │     │ useMutation  │     │ axios.post() │
│ from hooks   │     │ + cache mgmt │     │ + auth       │
└──────────────┘     └──────────────┘     └──────────────┘
                                              │
                                              ▼
                                        ┌──────────────┐
                                        │  API Gateway │
                                        │  /api/v1/    │
                                        └──────────────┘
```

## State Management Per Component

```
type PageState<T> =
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error; retry: () => void }
  | { status: "empty"; message: string }
  | { status: "stale"; data: T; lastUpdated: Date }
```

Every page must render all 5 states correctly.

---

# Final Objective

Transform the traditional workflow:

Search Job
→ Create Resume
→ Create Cover Letter
→ Send Application

into:

Create Profile
→ Discover Jobs
→ Match Opportunities
→ Optimize ATS Resume
→ Generate Resume
→ Generate Cover Letter
→ Create Application Package
→ Attach Resume Automatically
→ Send Application
→ Track Progress
→ Prepare For Interview

using a single intelligent AI-powered career automation platform — where every interaction is backed by real data, every action has proper loading/error feedback, and the user never sees stale or fake data.
