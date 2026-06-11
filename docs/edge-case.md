# Edge Cases & Failure Scenarios — AI Career Automation Platform

> **Version:** 1.0  
> **Status:** Active  
> **Last Updated:** June 11, 2026  
> **Scope:** All 9 microservices, infrastructure, AI agents, frontend

---

## Table of Contents

1. [General Platform Edge Cases](#1-general-platform-edge-cases)
2. [Auth Service Edge Cases](#2-auth-service-edge-cases)
3. [Profile Service Edge Cases](#3-profile-service-edge-cases)
4. [Resume Service Edge Cases](#4-resume-service-edge-cases)
5. [Job Service Edge Cases](#5-job-service-edge-cases)
6. [Match Service Edge Cases](#6-match-service-edge-cases)
7. [AI Orchestrator Edge Cases](#7-ai-orchestrator-edge-cases)
8. [Outreach Service Edge Cases](#8-outreach-service-edge-cases)
9. [Application Service Edge Cases](#9-application-service-edge-cases)
10. [Tracking & Notification Edge Cases](#10-tracking--notification-edge-cases)
11. [Frontend Edge Cases](#11-frontend-edge-cases)
12. [Infrastructure Edge Cases](#12-infrastructure-edge-cases)
13. [Data Integrity Edge Cases](#13-data-integrity-edge-cases)
14. [Security Edge Cases](#14-security-edge-cases)
15. [Race Condition Matrix](#15-race-condition-matrix)

---

## 1. General Platform Edge Cases

### 1.1 API Gateway & Rate Limiting

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-001 | User exceeds 100 req/min rate limit | Return `429 Too Many Requests` with `Retry-After` header, log the violation | Medium |
| EC-002 | User sends malformed JSON in request body | Return `400 Bad Request` with descriptive error (field-level details) | Low |
| EC-003 | Request with extremely large payload (>10MB) | Return `413 Payload Too Large`, reject before processing | Medium |
| EC-004 | API version in URL doesn't exist (`/api/v99/`) | Return `404 Not Found` with supported versions listed | Low |
| EC-005 | Request includes unexpected query parameters | Ignore extra params (don't error), log at DEBUG level | Low |
| EC-006 | Concurrent requests from same user exceed burst limit | Apply token bucket rate limiting, queue excess requests | Medium |
| EC-007 | IPv6 vs IPv4 rate limiting buckets | Normalize both to a canonical form, apply same bucket | Low |
| EC-008 | Health check endpoints (`/health`, `/ready`) | Skip rate limiting and auth for health endpoints | Low |

### 1.2 Inter-Service Communication

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-009 | Downstream service returns 503 (unavailable) | Upstream service should retry with exponential backoff (3 attempts), then fail gracefully with cached data if available | High |
| EC-010 | Downstream service returns 500 (internal error) | Log the error, return a 502 Bad Gateway to the client with a generic message | Medium |
| EC-011 | Downstream service takes >30s to respond | Request should timeout, return 504 Gateway Timeout | Medium |
| EC-012 | Circular service dependency (A → B → A) | Detect at startup via dependency graph validation, fail fast | Critical |
| EC-013 | Service A sends event, Service B never receives it | Use Celery with acknowledgments and dead-letter queues; implement periodic reconciliation jobs | High |

### 1.3 Celery / Queue Processing

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-014 | Celery worker crashes mid-task | Task is re-delivered to another worker (acks_late=true), at-least-once delivery | High |
| EC-015 | Redis (broker) goes down | Workers cannot receive new tasks; in-flight tasks complete but can't report results. Alert immediately | Critical |
| EC-016 | Task retries exhausted (still fails) | Task goes to dead-letter queue, alert operator, log full error | Medium |
| EC-017 | Celery Beat misses a scheduled tick | Next scheduled tick fires as normal; missed tick is skipped (not replayed) | Low |
| EC-018 | Task queue grows to >10,000 pending tasks | Alert: queue backlog. Workers should auto-scale if configured | Medium |
| EC-019 | Duplicate task execution (same task delivered twice) | All tasks should be idempotent — running twice should produce same result | High |
| EC-020 | Task scheduled for same job+profile by two events | Use `task_uniq` or database unique constraint to prevent duplicate processing | Medium |
| EC-021 | Extremely long-running task (>1 hour) | Set task soft/hard time limits; log warning at soft limit, kill at hard limit | High |

---

## 2. Auth Service Edge Cases

### 2.1 Registration & Login

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-022 | Register with already-registered email | Return `409 Conflict` with message "Email already registered" | Low |
| EC-023 | Login with unregistered email | Return `401 Unauthorized` — don't reveal whether email exists (generic "Invalid credentials") | Medium |
| EC-024 | Login with correct email but wrong password | Return `401 Unauthorized` with generic "Invalid credentials" message | Low |
| EC-025 | Password with exactly 8 characters (minimum) | Accepted, no issue | Low |
| EC-026 | Password with 129+ characters (maximum) | Reject with `422` and validation error | Low |
| EC-027 | Password is all whitespace | Reject as invalid (no leading/trailing whitespace allowed in passwords) | Medium |
| EC-028 | Email with unicode characters (e.g., ém@il.com) | Validate per RFC 5321; reject exotic unicode but allow common international chars | Low |
| EC-029 | Registration with SQL injection attempt in email field | Parameterized queries prevent injection; return 400 validation error | Critical |
| EC-030 | Registration with XSS in name field | Sanitize on input, escape on output. Store sanitized, not raw | High |

### 2.2 Token & Session Management

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-031 | Expired access token used in request | Return `401 Unauthorized` with `token_expired` error code | Low |
| EC-032 | Tampered JWT (modified payload) | JWT signature validation fails, return `401 Unauthorized` | High |
| EC-033 | Expired refresh token used | Return `401 Unauthorized`; client must re-authenticate | Medium |
| EC-034 | Refresh token used twice (replay attack) | Implement refresh token rotation: invalidate old token, if reused, invalidate all tokens for user | High |
| EC-035 | JWT with `alg: none` header | Reject — algorithm must be explicitly set to RS256 or HS256 | Critical |
| EC-036 | JWT issued for deleted user | Auth middleware checks user existence in DB; return 401 if user not found | Medium |
| EC-037 | Token blacklist Redis goes down | Fall back to short TTL on tokens (5 min access tokens) to limit damage | High |
| EC-038 | User logged in on 10+ devices simultaneously | Allow by default; configurable max sessions per user | Low |

### 2.3 OAuth2

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-039 | OAuth provider returns invalid authorization code | Return `400 Bad Request`, log the provider error | Low |
| EC-040 | OAuth provider is unreachable | Return `503 Service Unavailable` with "Provider temporarily unavailable" | Medium |
| EC-041 | User cancels OAuth flow mid-way | Redirect back to app with `error=access_denied`, show user-friendly message | Low |
| EC-042 | OAuth state parameter doesn't match (CSRF) | Reject with `400 Bad Request`, log potential CSRF attempt | High |
| EC-043 | Same OAuth account linked to two different platform accounts | Return `409 Conflict` — one OAuth account can only link to one platform account | Medium |
| EC-044 | OAuth access token expires during platform session | Use refresh token to get new access token transparently; if both expired, re-prompt OAuth | Medium |
| EC-044b | OAuth **refresh** token expires (provider-specific TTL, e.g., 90 days for Microsoft) | Cannot silently refresh; fall back to SMTP for email delivery, prompt user to re-authorize OAuth | High |

### 2.4 Password Reset

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-045 | Password reset token expired | Return 410 Gone, prompt user to request a new reset link | Low |
| EC-046 | Password reset for unregistered email | Return 200 OK anyway (don't reveal whether email exists) | Medium |
| EC-047 | User requests password reset 10+ times in 5 minutes | Rate limit to 1 request per minute, return warning | Low |
| EC-048 | New password same as old password | Allow (some users rotate back); or optionally reject with "Use a different password" | Low |

---

## 3. Profile Service Edge Cases

### 3.1 CRUD Operations

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-049 | Create profile for user that already has one | Return `409 Conflict` — profile already exists | Medium |
| EC-050 | Get profile for non-existent user | Return `404 Not Found` | Low |
| EC-051 | Update profile with empty payload | Return `400 Bad Request` — nothing to update | Low |
| EC-052 | Update profile with 100+ skills in one request | Accept (bulk operations allowed), but validate each skill | Low |
| EC-053 | Delete profile while applications exist | Soft-delete profile, mark applications as orphaned, notify user | High |
| EC-054 | Export profile with 20+ years of experience | Accept and export correctly (no artificial limits on date ranges) | Low |
| EC-055 | Import profile with fields that don't exist in schema | Ignore unknown fields, or return warning listing skipped fields | Low |
| EC-056 | Import profile with missing required fields | Return `422` with field-level validation errors | Low |
| EC-057 | Profile with future start dates for experience | Reject — experience cannot start in the future | Medium |
| EC-058 | End date before start date in experience | Return validation error with field-level message | Medium |
| EC-059 | Phone number with international format (+1 234 567 8900) | Accept and store in E.164 format | Low |

### 3.2 Data Validation

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-060 | URL fields with `javascript:` protocol | Reject as invalid URL | High |
| EC-061 | Skill name with 500 characters | Truncate to max 100 chars with warning | Low |
| EC-062 | Empty skills array | Accept (user may have no skills yet) | Low |
| EC-063 | 50+ work experience entries | Accept, but only top 10-15 displayed in resume by default | Low |
| EC-064 | GPA value of 4.0 on a 4.0 scale | Accept | Low |
| EC-065 | GPA value of 10.0 on a 10.0 scale | Accept (validate against scale field) | Low |
| EC-066 | GPA with more than 2 decimal places | Round to 2 decimal places | Low |
| EC-067 | LinkedIn URL not matching linkedin.com domain | Warning but accept (user may use regional domain like linkedin.cn) | Low |

### 3.3 Concurrent Access

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-068 | Two concurrent requests update same profile field | Last-write-wins is acceptable; use `updated_at` timestamp for conflict detection | Medium |
| EC-069 | User deletes profile while export is in progress | Export should use a read-committed snapshot; return data or error, not partial data | Medium |
| EC-070 | Import profile (overwrite) while user is editing profile | Import wins, user's in-progress edits are lost. Show warning on UI | Medium |

---

## 4. Resume Service Edge Cases

### 4.1 Resume Generation

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-071 | Generate resume for profile with no skills | Generate resume with empty skills section (don't crash) | Medium |
| EC-072 | Generate resume for profile with 20+ years experience | Generate multi-page resume; ensure pagination works | Low |
| EC-073 | Generate resume for non-existent profile | Return `404 Not Found` on profile lookup | Low |
| EC-074 | Generate resume with invalid template ID | Fall back to default template | Low |
| EC-075 | Generate resume for same profile+role twice | Create new version, keep all versions in history | Low |
| EC-076 | PDF generation takes >60 seconds | Celery task timeout; retry once, then log as error | High |
| EC-077 | PDF generation produces file >10MB | Warn user, suggest compression; accept up to 25MB | Medium |
| EC-078 | Resume content contains emoji characters | Render as-is (WeasyPrint supports emoji in PDFs with appropriate fonts) | Low |
| EC-079 | Resume content is extremely long (20+ pages) | Generate anyway, but warn user that resume should be 1-2 pages | Low |
| EC-080 | Template uses unsupported CSS features | WeasyPrint renders what it can, silently ignores unsupported CSS | Low |

### 4.2 ATS Optimization

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-081 | Optimize resume for job with empty description | Return error — job description is required for optimization | Medium |
| EC-081b | Optimize resume for an expired job (posted_date > 6 months ago) | Allow optimization but warn user "This job posting may no longer be active" | Low |
| EC-082 | Optimize resume — job description is not in English | Optimize anyway (ATS systems work with multiple languages), but warn user | Low |
| EC-083 | Optimize resume with no matching keywords between profile and job | Return low ATS score (0-10%), suggest adding relevant missing skills | Medium |
| EC-084 | Optimize resume — AI agent produces invalid structured output | Retry with more constrained prompt; on 2nd failure, return last valid state | High |
| EC-085 | ATS score computation divides by zero (job has 0 required skills) | Set match score to 0, return error: "No skills found in job description" | Medium |
| EC-086 | Resume already perfectly optimized (ATS score 95+) | Still analyze, note "Resume is already well-optimized" | Low |
| EC-087 | Keyword stuffing detection — AI adds too many keywords | Limit keyword additions to max 15% of original content length | Medium |

### 4.3 PDF Download & Storage

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-088 | Download resume that has no generated PDF yet | Return `404` — PDF not yet generated | Low |
| EC-089 | MinIO is down during PDF generation | Fail the task, retry with backoff. Return 503 to user | Critical |
| EC-090 | Generated PDF is corrupted on disk | Compare stored file size vs expected; regenerate if mismatch found | High |
| EC-091 | Download link from MinIO presigned URL expires | Generate a new presigned URL transparently | Low |
| EC-092 | Multiple concurrent downloads of same PDF | MinIO handles concurrent reads; limit to 100 simultaneous downloads | Low |
| EC-092b | User clicks "Generate" twice for the same resume quickly | First call starts generation, second call either returns in-progress status (202 Accepted) or queues a second version after first completes | Medium |

### 4.4 Template Management

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-093 | Delete a template that is in use by existing resumes | Soft-delete; existing resumes keep a snapshot of the template used | Medium |
| EC-094 | Upload a template with malicious HTML/JS | Sanitize all template HTML — strip `<script>`, `on*` attributes, `javascript:` URLs | Critical |
| EC-095 | Template with extremely complex layout (tables, columns, graphics) | Test rendering; WeasyPrint handles most CSS2.1 features | Low |
| EC-096 | All templates deleted (none available) | Fall back to a minimal built-in hardcoded template | Medium |

---

## 5. Job Service Edge Cases

### 5.1 Job Scraping

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-097 | Job source website is down | Log failure, increment error count on source config, skip until next schedule | Medium |
| EC-098 | Job source returns 403 Forbidden (blocked) | Log with alert, disable source after 3 consecutive failures, notify admin | High |
| EC-099 | Job source changes HTML structure (scraper breaks) | Catch parse errors, log full diff hints, alert developer to update scraper | High |
| EC-100 | Scraper finds 0 new jobs (all already exist) | No-op; update `last_run_at` timestamp, log "0 new jobs found" | Low |
| EC-101 | Scraper finds 10,000+ new jobs in one run | Process in batches of 500, commit between batches to avoid memory overflow | High |
| EC-102 | Job description contains HTML/markdown | Strip HTML tags, normalize line breaks, store as plain text + structured data | Medium |
| EC-103 | Salary field has non-standard format (e.g., "₹15L/yr") | Store raw value, attempt to normalize to standard range; flag if unparseable | Medium |
| EC-103b | User attempts to create application for an expired job (expiry_date < NOW()) | Reject with message "This job posting has expired on {expiry_date}. Apply to active jobs instead." | Medium |
| EC-103c | Job has no expiry_date set | Treat as active indefinitely; don't auto-expire | Low |
| EC-104 | Job URL is extremely long (>2000 chars) | Store as-is (PostgreSQL TEXT can handle it); index only on hash | Low |
| EC-105 | Duplicate job from same source (same external_id) | UPSERT — update existing record if content changed | Low |
| EC-106 | Duplicate job from different sources (same company, same title) | Keep both as separate records (different sources); link via dedup hash | Medium |

### 5.2 Job Filtering & Search

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-107 | Search with empty query string | Return all active jobs (paginated) | Low |
| EC-108 | Search with `required_skills` that matches 0 jobs | Return empty result set with `total: 0` | Low |
| EC-109 | Filter by salary range but job has no salary data | Exclude jobs without salary data from salary-filtered results | Medium |
| EC-110 | Filter by location with partial match ("San" vs "San Francisco") | Use substring matching or fuzzy matching on location | Medium |
| EC-111 | Sort by posted_date but job has null posted_date | Treat nulls as oldest (or newest, configurable) | Low |
| EC-112 | Pagination beyond available results (`page=100` on 50 results) | Return empty `data` array with correct `total` count | Low |
| EC-113 | Search query with SQL-like characters (`' OR 1=1--`) | Parameterized query — no injection possible; treat as literal string | Critical |
| EC-114 | Search with extremely long query (1000+ chars) | Truncate to 200 chars with warning | Low |

### 5.3 Source Management

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-115 | Add a job source with invalid base URL | Validate URL format on creation; reject with validation error | Low |
| EC-116 | Disable a source while scraping is in progress | Allow current scrape to finish, prevent new runs | Low |
| EC-117 | Trigger immediate scrape while previous scrape is still running | Skip — return "Scrape already in progress for this source" | Medium |
| EC-118 | All sources disabled | Platform shows no jobs; warn user on dashboard | Low |

---

## 6. Match Service Edge Cases

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-119 | Score match between empty profile and job | Return minimum score (0), note "Complete your profile for better matches" | Medium |
| EC-120 | Score match between profile and job in different languages | Language mismatch — AI-enhanced matching handles cross-language; rules-based returns lower score | Medium |
| EC-121 | Score match with job that has no required skills | Only match on experience, education, and location factors (45% of total weight) | Medium |
| EC-122 | Score match where profile has 0 matching skills | Low score but non-zero (experience/education/location can still match) | Low |
| EC-123 | Batch matching: 10,000 new jobs matched against 1,000 profiles | Process in batches of 100 profiles × 100 jobs; use background Celery task | High |
| EC-124 | Batch matching times out (>30 min) | Split into smaller chunks; each chunk is a separate Celery task | High |
| EC-125 | Match recommendation returns fewer than 10 jobs | Return all matched jobs (even 1), no padding | Low |
| EC-126 | Skill gap analysis with 50+ missing skills | List top-10 most impactful missing skills, group rest by category | Medium |
| EC-127 | Profile has no experience but has education | Education match weighted higher for entry-level roles | Low |

---

## 7. AI Orchestrator Edge Cases

### 7.1 LLM Provider

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-128 | Ollama service is down | Fail over to LocalAI; if both down, return 503 with "AI service unavailable" | Critical |
| EC-128b | Requested model not found in Ollama (never pulled or deleted) | Fall back to next available smaller model in chain; log warning with available models list | High |
| EC-128c | Ollama is pulling a model (still downloading) when request arrives | Return 503 with "Model is loading, retry in {estimated_remaining}s" — client should retry | Medium |
| EC-129 | Ollama returns 429 (too many requests) | Implement client-side rate limiting, queue requests, retry with backoff | High |
| EC-130 | LLM response is empty (model returns no output) | Retry with simpler prompt; on 2nd failure, return fallback result | Medium |
| EC-131 | LLM response is malformed JSON | Parse retry with stricter prompt; on 2nd failure, return error | High |
| EC-132 | LLM response is valid JSON but doesn't match expected schema | Validate against Pydantic schema; if invalid, retry with schema included in prompt | Medium |
| EC-133 | LLM response is valid but nonsensical (e.g., garbage text) | Hallucination detection: check for coherence; if suspicious, retry | Medium |
| EC-134 | Model returns toxic or biased content | Content filtering pass before returning to user; flag for review | High |
| EC-135 | Prompt is too long (exceeds context window) | Summarize/trim sections; prioritize job description and latest experience | High |
| EC-136 | Model takes >120 seconds to generate response | Hard timeout; fall back to smaller model, if still slow, return error | High |
| EC-137 | GPU OOM (out of memory) during generation | Catch OOM error, switch to smaller quantized model (8B → 3B) | Critical |
| EC-138 | AI cost tracking | Since models run locally on Ollama, AI costs are $0. Track only token counts and duration | Low |

### 7.2 Prompt Templates

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-139 | Prompt template variable is missing | Template rendering should fail with clear error message listing missing variables | Medium |
| EC-140 | Prompt template contains sensitive data (PII) | WARNING: User PII (email, phone, address) should never be in prompts. Strip PII before sending to LLM | Critical |
| EC-141 | Prompt injection attack via user profile data | Sanitize all user-provided data in prompts; escape special characters | Critical |
| EC-142 | Non-English text in prompts affects model output | Prompt in English, user data can be multilingual; model handles mixed languages | Low |

### 7.3 Structured Output

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-143 | LLM returns JSON with extra fields not in schema | Strip extra fields, use only validated fields | Medium |
| EC-144 | LLM returns JSON with missing required fields | Retry with explicit schema reminder; on failure, return error | High |
| EC-145 | LLM returns extremely long output (>10,000 tokens) | Truncate to max expected length, log warning | Medium |
| EC-146 | Pydantic validation of LLM output fails | Retry (2 attempts); if still failing, use fallback rules-based result | High |

---

## 8. Outreach Service Edge Cases

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-147 | Generate cover letter for job with no company name | Use company name from job URL domain, or "the Company" as fallback | Low |
| EC-148 | Generate cover letter for job with extremely long company name | Truncate after 100 chars for display; full name in letter body | Low |
| EC-149 | Email content contains personal info leakage (phone, address) | Strip sensitive PII from email body; include only name, title, and relevant experience | High |
| EC-150 | Cover letter exceeds email body length limits (100KB) | Truncate to fit, or offer as PDF attachment instead | Medium |
| EC-151 | Preview content is regenerated but user has unsaved edits | Show warning: "Your edits will be lost if you regenerate" | Low |
| EC-152 | User requests 10+ versions of same cover letter | Allow up to 20 versions per job, oldest auto-deleted | Low |
| EC-153 | AI generates cover letter with overly enthusiastic tone | Apply tone guardrails in the prompt; allow user to request tone adjustments | Low |

---

## 9. Application Service Edge Cases

### 9.1 State Machine

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-154 | Transition application from "draft" directly to "sent" (skip intermediate states) | Reject — state machine requires sequential transitions; return 400 with valid transitions | High |
| EC-155 | Transition from "rejected" to "interview_scheduled" | Reject — "rejected" is a terminal state with no outgoing transitions | High |
| EC-156 | Double-submit: user clicks "Submit" twice quickly | First click transitions to "sent"; second click returns current state (idempotent) | Medium |
| EC-157 | Webhook delivers "delivered" event before "sent" event | Accept out-of-order events; fill in missing states retrospectively if possible | Medium |
| EC-158 | Application in "sent" state for 30+ days with no delivery update | Periodic reconciliation job checks delivery status with provider | Medium |
| EC-159 | Application status webhook received for unknown application ID | Log warning with webhook payload, return 404, don't create phantom records | Low |

### 9.2 Package Assembly

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-160 | Package assembly fails because resume PDF is missing | Skip PDF attachment, send email with cover letter only, flag application | High |
| EC-161 | Package assembly fails because cover letter generation failed | Use a basic cover letter template as fallback | High |
| EC-162 | Package assembly takes too long (>5 min) | Timeout Celery task, mark as failed, retry up to 2 times | Medium |
| EC-163 | Resume PDF attachment is >25MB | Compress PDF; if still too large, share MinIO download link instead of direct attachment | Medium |

### 9.3 Email Delivery

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-164 | SMTP server rejects email (invalid recipient) — **hard bounce** | Log hard bounce, mark application as "failed", do NOT retry (permanent failure) | Medium |
| EC-164b | SMTP server rejects email temporarily (mailbox full, rate limited) — **soft bounce** | Log soft bounce, retry 3 times with exponential backoff (5min, 15min, 1hr); if all fail, mark as "failed" | Medium |
| EC-165 | SMTP server is unreachable | Retry 5 times with exponential backoff (30s, 1min, 2min, 4min, 8min) | High |
| EC-166 | Email sent but provider returns success before actually sending | Track via webhooks; status is "sent" until webhook confirms "delivered" | Medium |
| EC-167 | Recipient email address is invalid format | Validate on application creation; catch validation error before send | Medium |
| EC-168 | Email is flagged as spam by recipient's provider | Track bounce/spam reports; alert user to improve email content | High |
| EC-169 | Email contains attachments that trigger spam filters | Avoid attachment types known to trigger filters; prefer PDF (safe) | Medium |
| EC-170 | Sending from Gmail API exceeds daily quota | Fall back to secondary email provider (SMTP) | High |
| EC-171 | Sending from Outlook API token expired | Attempt to refresh token via OAuth refresh flow; if failed, fall back to SMTP | High |

---

## 10. Tracking & Notification Edge Cases

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-172 | Application stats show 0 applications | Show empty state with call-to-action "Find your first job match" | Low |
| EC-173 | User has 1000+ applications | Dashboard paginates; analytics aggregate across all | Medium |
| EC-174 | Notification sent for application that user already viewed | Mark as read if application was viewed after notification was triggered | Low |
| EC-175 | User clears all notifications | Soft-delete (mark as read); keep for audit purposes | Low |
| EC-176 | Export CSV with 10,000+ rows | Stream export to avoid memory issues; send download link via email for large exports | High |
| EC-177 | Analytics computation times out for large dataset | Pre-compute aggregates nightly; serve cached results on dashboard | Medium |

---

## 11. Frontend Edge Cases

### 11.1 UI/UX

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-178 | User accesses dashboard without completing profile | Show onboarding prompt/modal with progress indicator | Low |
| EC-179 | Browser back button after form submission | Show warning if form has unsaved changes | Low |
| EC-180 | Network disconnection while submitting a form | Show offline banner, save draft locally, retry on reconnection | High |
| EC-181 | PDF preview not supported in browser | Show fallback: "Download PDF to view" with download button | Low |
| EC-182 | User opens two browser tabs with same profile editor | Warn on second tab: "Profile is being edited in another tab" | Low |
| EC-183 | Very long skill name breaks layout | CSS truncation with ellipsis; full name in tooltip | Low |
| EC-184 | Empty job search results | Show friendly illustration + suggestions to broaden search criteria | Low |
| EC-185 | Browser extension blocks API requests (uBlock, Privacy Badger) | Use standard fetch API; request CORS headers properly | Medium |

### 11.2 Forms & Validation

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-186 | Submit form with disabled JavaScript | All form submissions use standard HTML form posts (with JS enhancement) | Medium |
| EC-187 | Date picker for birth date shows future dates | Restrict date picker to past dates only | Low |
| EC-188 | File upload for avatar exceeds 5MB | Validate file size on client before upload; reject with message | Low |
| EC-189 | Upload non-image file for avatar field | Validate MIME type client-side; reject non-image formats | Low |
| EC-190 | Very long text in textarea (>10,000 chars) | Allow with character counter; enforce max length server-side | Low |

### 11.3 Performance

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-191 | 1000+ skills in a user's profile | Virtualized list with pagination; don't render all at once | Medium |
| EC-192 | Slow API response (>5s) on dashboard load | Show skeleton loading + optimistic UI for each section | Medium |
| EC-193 | Large PDF (>10MB) in browser PDF viewer | Use streaming; show loading progress | Low |
| EC-194 | Browser tab backgrounded during long operation | Use `requestAnimationFrame` for animations; Service Workers for background tasks | Low |

---

## 12. Infrastructure Edge Cases

### 12.1 Database

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-195 | PostgreSQL connection pool exhausted | Queue requests; return 503 if queue exceeds threshold | Critical |
| EC-196 | PostgreSQL deadlock between two concurrent transactions | Deadlock detection kills one transaction; retry killed transaction | High |
| EC-197 | Database migration fails mid-way (partial migration) | Use transactional DDL (PostgreSQL supports); rollback on failure | Critical |
| EC-198 | Disk space full on PostgreSQL host | Database refuses writes; alert with urgency; read-only mode | Critical |
| EC-199 | PostgreSQL replication lag in read replicas | Route critical reads to primary; stale reads acceptable for analytics | Medium |

### 12.2 Storage (MinIO)

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-200 | MinIO disk space full | Fail writes with explicit "Storage full" error; alert immediately | Critical |
| EC-201 | MinIO object corrupted on disk | Checksum verification on read; regenerate from source if corrupted | High |
| EC-202 | Attempt to download non-existent object | Return 404; log as warning (possible reference integrity issue) | Low |
| EC-203 | Concurrent upload of same file to same path | Last-write-wins; MinIO handles consistency | Low |

### 12.3 Docker & Deployment

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-204 | Docker container runs out of memory | OOMKilled by Docker; container restarts; alert on restart count | Critical |
| EC-205 | Docker health check fails 3 times in a row | Docker restarts container; if restart fails, alert | High |
| EC-206 | Port conflict on host machine (port already in use) | Docker Compose fails to start; clear error message in logs | Medium |
| EC-207 | .env file missing required variables | Service fails to start with clear error listing missing vars | High |

### 12.4 CI/CD

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-208 | Test suite passes locally but fails in CI | Environment mismatch; pin exact dependency versions in requirements.txt | Medium |
| EC-209 | Docker image build fails due to network timeout | Retry build with backoff; if persistent, alert | Medium |
| EC-210 | Migration fails in CI but passes locally | DB state mismatch; use fresh DB for CI migrations | Medium |

---

## 13. Data Integrity Edge Cases

### 13.1 Referential Integrity

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-211 | Resume references a profile that was deleted | Soft-delete prevents hard deletes; alternatively, cascade delete or orphan the resume | High |
| EC-212 | Application references a job that was scraped but later removed | Keep application but show "Job no longer available" | Medium |
| EC-213 | Match references a job that no longer exists | Return null job data in match response; keep match for historical purposes | Medium |
| EC-214 | Cover letter references a job that was deleted | Keep cover letter content as historical artifact; show "Original job deleted" | Low |

### 13.2 Data Consistency

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-215 | Celery task creates resume but fails to update application state | Reconciliation job checks: application.status vs actual resume existence; fix mismatches | High |
| EC-216 | Application marked as "sent" but email was never actually sent | Reconciliation job: check delivery logs; if no log exists, revert to "email_prepared" | High |
| EC-217 | Duplicate match records for same profile+job | DB unique constraint prevents; on conflict, update existing match | Medium |
| EC-218 | Orphaned resume files in MinIO (no DB record) | Periodic cleanup job: list MinIO objects, cross-reference with DB, delete orphans | Medium |

### 13.3 Time & Timezone

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-219 | User creates application at 11:59 PM in their timezone | Store in UTC; display in user's local timezone | Low |
| EC-220 | Daylight saving time transition creates ambiguous timestamps | Store all timestamps in UTC; convert to user's timezone for display | Medium |
| EC-221 | Job posted_date is in the future (scraper error) | Clamp to current datetime; log warning about scraper data quality | Low |
| EC-222 | Different date formats across scraped jobs (MM/DD vs DD/MM) | Normalize dates during parsing; use ISO 8601 internally | Medium |

---

## 14. Security Edge Cases

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| EC-223 | User accesses another user's profile via IDOR (IDOR attack) | Auth middleware checks: user can only access own profile (profile_id == auth_user_id) | Critical |
| EC-224 | User accesses another user's application list | Same as EC-223 — enforce ownership check on all endpoints | Critical |
| EC-225 | User modifies another user's application status | Status update endpoint validates ownership; return 403 | Critical |
| EC-226 | API key leaked in client-side code | Service API keys should NEVER be in client code; use server-side proxy | Critical |
| EC-227 | Brute force login attempt (100+ attempts in 1 min) | Rate limit: 5 attempts per minute per IP; temporary IP ban after 20 attempts | Critical |
| EC-228 | Mass account creation via automation | CAPTCHA on registration; email verification required for active accounts | High |
| EC-229 | HTML/script injection in profile bio field | Server-side sanitization (Bleach or similar); stored XSS prevention | Critical |
| EC-230 | CSRF attack on state-changing endpoints | SameSite=Strict cookies + CSRF tokens for cookie-based auth | High |
| EC-231 | Path traversal in file download endpoints | Validate file paths: reject paths containing `..` or starting with `/` | Critical |
| EC-232 | Mass assignment (updating fields that should be read-only) | Pydantic schemas explicitly define writable fields; reject unknown fields | High |
| EC-233 | Session fixation attack | Regenerate session ID on login | Medium |

---

## 15. Race Condition Matrix

This section documents all known race conditions and their mitigation strategies.

| # | Scenario | Services Involved | Risk | Mitigation |
|---|----------|-------------------|------|------------|
| RC-001 | Profile update + Resume generation at same time | Profile, Resume | Low | Resume generation reads profile at start; if profile changes mid-generation, resume uses snapshot (acceptable) |
| RC-002 | Job scraped + Match batch starting simultaneously | Job, Match | Medium | Match batch uses jobs updated after last match run; newly scraped job may be missed until next batch cycle (acceptable) |
| RC-003 | Application submit + Cover letter generation | Application, Outreach | High | State machine locks: application transitions to "cover_letter_generated" only after cover letter task completes. Use Celery chain tasks |
| RC-004 | Two webhook events update same application status | Application | High | Optimistic locking via `updated_at` check; second webhook retries on conflict |
| RC-005 | User deletes profile while application pipeline is running | Profile, Application | High | Soft-delete: profile marked as inactive; pipeline completes with snapshot data. Final application status: "orphaned" |
| RC-006 | OAuth callback handled twice (duplicate request) | Auth | Medium | State nonce consumed on first use; second request fails with "state already used" |
| RC-007 | Two admins disable same job source simultaneously | Job | Low | Last-write-wins; both set is_active=False, no conflict |
| RC-008 | Celery task processes same job+profile match twice | Match | High | Unique constraint on (profile_id, job_id); second insert fails, update instead |
| RC-009 | Email send task retries while first attempt succeeds | Application | High | Provider message ID dedup: check if provider_message_id exists before marking as sent |
| RC-010 | User clicks "Apply" twice on same job | Application | Medium | Unique constraint on (profile_id, job_id) for active applications; second click returns existing application |

---

> **Document Version:** 1.1  
> **Total Edge Cases Documented:** 243  
> **Critical Severity:** 33  
> **High Severity:** 52  
> **Medium Severity:** 91  
> **Low Severity:** 67  
> **Last Updated:** June 11, 2026
